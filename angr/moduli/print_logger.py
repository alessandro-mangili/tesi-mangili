import angr

class PrintfLogger(angr.SimStatePlugin):
    """
    Plugin personalizzato per angr che memorizza i messaggi di printf durante l'esecuzione simbolica.

    Viene registrato nello stato con:
        state.register_plugin('printf_log', PrintfLogger())

    Implementazione:
        - Segue l'API di angr.state_plugins.plugin.SimStatePlugin
        - Implementa il metodo copy() per gestire correttamente i branch dell'esecuzione simbolica
        - Quando angr crea un branch (fork dello stato), il metodo copy() viene chiamato
        automaticamente per duplicare il plugin nei nuovi stati figli
        
    Attributi:
        messages (list): Lista di stringhe contenenti tutti i messaggi printf catturati

    Documentazione API: https://docs.angr.io/en/latest/api.html#angr.state_plugins.plugin.SimStatePlugin
    """

    def __init__(self):
        super(PrintfLogger, self).__init__()
        self.messages = []
    
    @angr.SimStatePlugin.memo
    def copy(self, memo):
        p = PrintfLogger()
        p.messages = list(self.messages)
        return p


class HookPrintf(angr.SimProcedure):
    
    """
    Hook per la funzione printf che cattura e formatta l'output.

    Funzionalità:
        - Intercetta chiamate a printf durante l'esecuzione simbolica
        - Estrae la format string e i primi 3 argomenti (r1, r2, r3 su ARM)
        - Gestisce i format specifier comuni: %s, %d, %u, %x
        - Per %x: converte in carattere ASCII se stampabile, altrimenti in hex
        - Salva i messaggi formattati nel plugin PrintfLogger
        
    Returns:
        0 (valore di ritorno standard per printf stub)
    """
    
    def run(self, fmt):
        args = [
            self.state.regs.r1,
            self.state.regs.r2,
            self.state.regs.r3
        ]
        try:
            fmt_addr = self.state.solver.eval(fmt)
            fmt_str = self.state.memory.load(fmt_addr, 100)
            fmt_concrete = self.state.solver.eval(fmt_str, cast_to=bytes)
            msg = fmt_concrete.split(b'\x00')[0].decode(errors='replace')

            for arg in args:
                if '%s' in msg:     
                    arg_addr = self.state.solver.eval(arg)
                    arg_bytes = self.state.memory.load(arg_addr, 100)
                    arg_concrete = self.state.solver.eval(arg_bytes, cast_to=bytes)
                    arg_str = arg_concrete.split(b'\x00')[0].decode(errors='replace')
                    msg = msg.replace('%s', arg_str, 1)
                        
                if '%d' in msg:     
                    arg = self.state.solver.eval(arg)
                    msg = msg.replace('%d', str(arg), 1)
                        
                if '%u' in msg:     
                    arg = self.state.solver.eval(arg)
                    msg = msg.replace('%u', str(arg), 1)
                            
                if '%x' in msg:     
                    arg = self.state.solver.eval(arg)
                    if 32 <= arg <= 126:  # Range ASCII stampabile
                        char_repr = f"{chr(arg)}"
                    else:
                        char_repr = f"0x{arg:x}"
                        
                    msg = msg.replace('%x', char_repr, 1)
        except:
            print(f"[ERROR] printf chiamata a {hex(self.state.addr)}")
            
        self.state.get_plugin('printf_log').messages.append(msg)
        return 0