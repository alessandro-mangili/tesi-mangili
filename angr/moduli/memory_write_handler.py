import angr

"""
Handlers per il monitoraggio delle scritture in memoria durante l'esecuzione simbolica con angr.

Questo modulo fornisce due handler per intercettare operazioni di scrittura critiche:
1. flash_write_handler: Rileva tentativi di scrittura nella Flash memory
2. OnUsartTDRWrite: Cattura l'output di debug dalla periferica USART3

Usage:
    # Registra gli handler con filtri di indirizzo specifici
    state.inspect.b('mem_write', 
                   mem_write_address=FLASH_BASE, 
                   when=angr.BP_BEFORE, 
                   action=flash_write_handler)
    
    state.inspect.b('mem_write', 
                   mem_write_address=USART3 + 0x28,  # USART_TDR offset
                   when=angr.BP_AFTER, 
                   action=OnUsartTDRWrite)

Note:
    - I breakpoint sono già filtrati per indirizzo, quindi le funzioni handler
      non necessitano di controlli aggiuntivi sugli indirizzi
    - USART_TDR è a offset +0x28 dalla base USART3 (STM32 Reference Manual)

References:
    - angr Breakpoints: https://docs.angr.io/en/latest/core-concepts/simulation.html#breakpoints
    - STM32 Memory Map: Datasheet pagina 93 (boundary addresses)
    - STM32 USART Registers: Reference Manual sezione USART
"""


# ============================================================================
# HANDLER FLASH MEMORY
# ============================================================================

def flash_write_handler(state):
    """
    Rileva e traccia scritture nella regione Flash dell'applicazione STM32.
    
    Questo handler viene invocato automaticamente quando angr rileva una scrittura
    all'indirizzo FLASH_BASE grazie al filtro mem_write_address nel breakpoint.
    
    Args:
        state (angr.SimState): Stato corrente dell'esecuzione simbolica
    
    Side Effects:
        - Imposta state.globals['flash_write'] = True
        - Stampa messaggio di debug con indirizzo e valore su stdout
    
    Note:
        - Questa funzione viene chiamata SOLO per scritture a FLASH_BASE
        - Non necessita di controlli sull'indirizzo (già filtrato dal breakpoint)
        - Usa BP_BEFORE per intercettare prima dell'effettiva scrittura
    """
    addr = state.inspect.mem_write_address
    expr = state.inspect.mem_write_expr
    addr_val = state.solver.eval(addr)
    
    print(f"[FLASH] Scrittura a {hex(addr_val)}, Valore: {expr}")
    state.globals['flash_write'] = True



class Buffer(angr.SimStatePlugin):
    def __init__(self):
        super(Buffer, self).__init__()
        self.chars = []
    
    @angr.SimStatePlugin.memo
    def copy(self, memo):
        p = Buffer()
        p.chars = list(self.chars)
        return p


# ============================================================================
# HANDLER USART DEBUG
# ============================================================================

def OnUsartTDRWrite(state):
    expr = state.inspect.mem_write_expr
    conc_data = state.solver.eval(expr)
    data = conc_data & 0xFF  # Estrai solo il byte meno significativo

    # \r o \n = fine messaggio
    if data == 0x0D or data == 0x0A:
        # Ricostruisci stringa pulita (rimuovi \n, \r residui)
        message = ''.join(state.get_plugin('buffer').chars).replace('\n', '').replace('\r', '').strip()
        
        # Salva solo messaggi non vuoti
        if message:
            state.get_plugin('printf_log').messages.append(message)
        
        state.get_plugin('buffer').chars.clear()
    
    # Null byte - ignorato
    elif data == 0x00:
        pass
    
    # Caratteri stampabili ASCII
    elif 32 <= data < 255:
        state.get_plugin('buffer').chars.append(chr(data))