import angr
import claripy

ALL_TYPES_STRING = '''
typedef unsigned char BYTE;
typedef unsigned short WORD;
typedef unsigned int UINT;
typedef unsigned int DWORD;
typedef unsigned int FSIZE_t;
typedef unsigned int LBA_t;

typedef struct _FILINFO{
    FSIZE_t fsize;    
    WORD    fdate;    
    WORD    ftime;     
    BYTE    fattrib;  
    char    fname[13];  
} FILINFO;

typedef struct {
    DWORD  fs;         /* Pointer to the volume holds this object */
    WORD    id;         /* Volume mount ID when this object was opened */
    BYTE    attr;       /* Object attribute */
    BYTE    stat;       /* Object chain status (exFAT: b1-0: =0:not contiguous, =2:contiguous, =3:fragmented in this session, b2:sub-directory stretched) */
    DWORD   sclust;     /* Object data cluster (0:no data or root directory) */
    FSIZE_t objsize;    /* Object size (valid when sclust != 0) */
    UINT    lockid;     /* File lock ID origin from 1 (index of file semaphore table Files[]) */
} FFOBJID;

typedef struct {
    FFOBJID obj;          /* Object identifier */
    BYTE    flag;         /* File status flags */
    BYTE    err;          /* Abort flag (error code) */
    FSIZE_t fptr;         /* File read/write pointer (byte offset origin from top of the file; 0 on open) */
    DWORD   clust;        /* Current cluster of fptr (one cluster behind if fptr is on the cluster boundary; invalid if fptr == 0) */
    LBA_t   sect;         /* Current data sector (can be invalid if fptr is on the cluster boundary)*/
    LBA_t   dir_sect;     /* Sector number containing the directory entry */
    BYTE*   dir_ptr;      /* Pointer to the directory entry in the window */
    DWORD*  cltbl;        /* Pointer to the cluster link map table (nulled on file open; set by application) */
    BYTE    buf[512]; /* File private data transfer buffer (Always valid if fptr is not on the sector boundary but can be invalid if fptr is on the sector boundary.) */
} FIL;

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
        ret_addr = hex(self.state.callstack.ret_addr)
        position = self.state.solver.eval(self.state.mem[fil].FIL.fptr.resolved)
        real_count = self.state.solver.eval(count)
        
        fill_info_obj = claripy.BVS(f'f_read_{hex(position)}_{hex(real_count)}_{ret_addr}', real_count * self.state.arch.bits)
        self.state.memory.store(buf, fill_info_obj, real_count, disable_actions=True, inspect=False)
        self.state.memory.store(read_ptr, real_count, 4, disable_actions=True, inspect=False)

        self.state.mem[fil].FIL.fptr = position + real_count
            
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
    def run(self, file_path, fill_info):
        size = self.state.mem.FILINFO._type.size // 8
        ret_addr = hex(self.state.callstack.ret_addr)
        fill_info_obj = claripy.BVS(f'f_stat_{file_path}_{ret_addr}', size * self.state.arch.bits)
        self.state.memory.store(fill_info, fill_info_obj, size, disable_actions=True, inspect=False)            
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