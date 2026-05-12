import angr
import claripy

class HookFRead(angr.SimProcedure):
    """
    Hook per la funzione f_read di FatFS.

    Simula la lettura di un file copiando la magic signature simbolica nel buffer.

    Args:
        fil: Puntatore alla struttura FIL (file handle)
        buf: Buffer di destinazione dove scrivere i dati letti
        count: Numero di bytes da leggere
        read_ptr: Puntatore dove scrivere il numero di bytes effettivamente letti

    Returns:
        0 (FR_OK - successo)
    """
    def run(self, fil, buf, count, read_ptr):
        magic = self.state.globals.get('magic')
        self.state.memory.store(buf, magic)
        self.state.memory.store(read_ptr, claripy.BVV(magic.size(), 32), endness='Iend_LE')
            
        return 0 

class HookFStat(angr.SimProcedure):
    """
    Hook per la funzione f_stat di FatFS.
    
    Simula il recupero delle informazioni di un file, popolando la struttura FILINFO
    con una dimensione simbolica e il nome del file "WALKLITE-APP.bin".
    
    
    Args:
        file_path: Path del file da controllare
        filinfo: Puntatore alla struttura FILINFO da popolare
    
    Returns:
        0 (FR_OK - file trovato)
    """
    def run(self, file_path, filinfo):
        fsize = self.state.globals.get('file_size')
        self.state.memory.store(filinfo, fsize, endness='Iend_LE', inspect=False, disable_actions=False, condition=None)
        mem_read = self.state.memory.load(filinfo, 4, endness='Iend_LE', inspect=False)
        self.state.solver.add(mem_read == fsize)
        fname = "WalkHNG-APP.bin\x00"
        self.state.memory.store(filinfo + 9, fname)
        return 0
    

class HookIDK(angr.SimProcedure):
    def run(self):
        return 2
    
class Hook_check_sd_card(angr.SimProcedure):
    def run(self):
        return 0

class Hook_f_open(angr.SimProcedure):
    def run(self):
        return 0