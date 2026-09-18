#include <stdint.h>
#include <string.h>

// ===================================
// KLEE symbolic execution interface
// ===================================

void klee_assert(int condition);
void klee_assume(int condition);
void klee_make_symbolic(void *addr, unsigned long nbytes, const char *name);
void klee_warning(const char *message);

// ===================================
// Firmware entry point declaration
// ===================================

extern int function_8007fb8(int arg1, int arg2);


int main(void) {
    int arg1, arg2, arg3, arg4;
    
    klee_make_symbolic(&arg1, sizeof(arg1), "arg1");
    klee_make_symbolic(&arg2, sizeof(arg2), "arg2");
    
    klee_assume(arg1 != 0);
    klee_assume(arg2 != 0);
    
    return function_8007fb8(arg1, arg2);
}
