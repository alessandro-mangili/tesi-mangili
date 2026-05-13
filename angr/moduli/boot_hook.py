import angr
import claripy

ALL_TYPES_STRING = '''
typedef unsigned char BYTE;
typedef unsigned short WORD;
typedef unsigned int UINT;
typedef unsigned int DWORD;
typedef unsigned int FSIZE_t;

typedef struct _FILINFO{
    FSIZE_t fsize;    
    WORD    fdate;    
    WORD    ftime;     
    BYTE    fattrib;  
    char    fname[13];  
} FILINFO;

'''

angr.types.register_types(angr.types.parse_types(ALL_TYPES_STRING))

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
        count = self.state.solver.eval(count)
        magic = self.state.globals.get('magic')
        self.state.memory.store(buf, magic)
        self.state.memory.store(read_ptr, claripy.BVV(count, 32), endness=self.state.arch.memory_endness)
            
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

        filinfo_obj = self.state.mem[filinfo].struct._FILINFO

        fsize = claripy.BVS(f'file_size', 32)
        self.state.globals['file_size'] = fsize
        fname = b"WalkHNG-APP.bin\x00"
        
        filinfo_obj.fsize = fsize

        cnt = 0
        for n in list(fname):
            filinfo_obj.fname[cnt] = claripy.BVV(n, 8)
            cnt += 1
            
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