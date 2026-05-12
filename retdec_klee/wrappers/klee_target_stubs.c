// ============================================================================
// IO function stubs
// ============================================================================
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

void klee_assert(int condition);
void klee_assume(int condition);
void klee_make_symbolic(void *addr, size_t nbytes, const char *name);
void klee_warning(const char *message);
void klee_abort();

//extern char klee_magic_buffer[32];

// HAL functions
void function_8001ef8(void) {  // HAL_Init
    //klee_warning("Reached HAL_Init");
    //klee_assert(1);
}

void function_8002c04(void) {  // HAL_PWREx_EnableBatteryCharging
    //klee_warning("Reached HAL_PWREx_EnableBatteryCharging");
    //klee_assert(0);
}

void function_8002b64(void) {  // HAL_PWR_EnableBkUpAccess
    //klee_warning("Reached HAL_PWR_EnableBkUpAccess");
    //klee_assert(0);
}

uint32_t function_8001f20(void) {  // HAL_GetTick
    //klee_warning("Reached HAL_GetTick");
    //klee_assert(0);
    return 0;
}

void function_8001f2c(void) {  // HAL_Delay
    //klee_warning("Reached HAL_Delay");
    //klee_assert(0);
}

void function_8002394(void) {  // HAL_FLASH_OB_Launch
    //klee_warning("Reached HAL_FLASH_OB_Launch");
    //klee_assert(0);
}

// Walk setup functions
void function_80006e4(void) {  // walk_clocks_setup
    //klee_warning("Reached walk_clocks_setup");
    //klee_assert(0);
}

int function_800084c(void) {  // walk_gpio_setup
    //klee_warning("Reached walk_gpio_setup");
    //klee_assert(0);
    return 0;
}

void function_8000b00(void) {  // walk_gpio_setup_2
    //klee_warning("Reached walk_gpio_setup_2");
    //klee_assert(0);
}

int function_80007c0(void) {  // walk_gpio_setup_3
    //klee_warning("Reached walk_gpio_setup_3");
    //klee_assert(0);
    return 0;
}

void function_8000808(void) {  // walk_uart_setup
    //klee_warning("Reached walk_uart_setup");
    //klee_assert(0);
}

void function_8000d48(void) {  // walk_buzzer_setup
    //klee_warning("Reached walk_buzzer_setup");
    //klee_assert(0);
}

void function_8001b6c(void) {  // walk_tft_setup
    //klee_warning("Reached walk_tft_setup");
    //klee_assert(0);
}

void function_8000bbc(void) {  // walk_check_usb_connection
    //klee_warning("Reached walk_check_usb_connection");
    //klee_assert(0);
}


void function_8000e24(void) {  // walk_start_oc_buzzer
    klee_warning("Reached walk_start_oc_buzzer");
    exit(42);
    //klee_assert(0);
}

// Display/Screen functions
void function_800176c(void) {  // walk_set_font_scale
    //klee_warning("Reached walk_set_font_scale");
    //klee_assert(0);
}

void function_80011ee(void) {  // scr_something_3
    //klee_warning("Reached scr_something_3");
    //klee_assert(0);
}

void function_80018ac(void) {  // draw_to_scr
    //klee_warning("Reached draw_to_scr");
    //klee_assert(0);
}

void function_800110e(void) {  // FUN_0800110e
    //klee_warning("Reached FUN_0800110e");
    //klee_assert(0);
}

void function_8007f84(void) {  // FUN_08007f84
    //klee_warning("Reached FUN_08007f84");
    //klee_assert(0);
}

// idk
uint32_t function_8007eac(void){
    //klee_warning("Reached idk");
    return 0;
}

// ============================================================================
// useful Stubs
// ============================================================================

// capire come fare funzioni


void function_8007de0(){
    klee_warning("CRITICAL: Signing firmware to flash!");
    //klee_assert(0);
}

// check_sd_card
int function_8008474(void){
    klee_warning("Reached check_sd_card --> returned 0");
    return 0;
}

//printf
int function_8008c48(const char *format, ...) {
    char msg[256];
    snprintf(msg, sizeof(msg), "Reached printf: %s", format ? format : "(null)");
    klee_warning(msg);
    return 0;
}


// f_open
int function_8007464(uint32_t *fil,char *path,uint8_t mode){
    klee_warning("Reached f_open --> returned 0");
    return 0;
}

// run_app()
void function_8007edc(){
    exit(42);
    return;
}

// ============================================================================
// stubs for walk_check_update_file
// ============================================================================


// memset
void function_8008d7e(void *p, char c, int s){
    klee_warning("Reached memset"); 
    return;
}

// f_stat
/**/
uint32_t function_800789c(char *path, uint32_t *info){
    klee_warning("Reached f_stat --> returned 0"); 
    return 0;
}

//f_read

uint32_t function_8007630(uint32_t *fil, void *buf,uint32_t to_read,uint32_t *read){
    char msg[128];
    snprintf(msg, sizeof(msg), "f_read: to_read=%u (0x%x), buf=%p", to_read, to_read, buf);
    klee_warning(msg);

    klee_make_symbolic(buf, to_read, "magic");
    klee_warning("MAKE MAGIC SYMBOLIC");
    return 0;
}


// f_close
uint32_t function_800787a(void){
    klee_warning("Reached f_close");
    return 0;
}

//strcpy
void function_8008fea(void){
    klee_warning("Reached strcpy");
    return;
}

//strcat
void function_08008fcc(void){
    klee_warning("Reached strcat");
    return;
}

//mod_strcmp
uint32_t function_80004fc(char * str, char * buf){
    char msg[128];
    snprintf(msg, sizeof(msg), "Reached mod_strcmp: str - > %s, buf - > %s", str, buf);
    klee_warning(msg);
    return 0;
}
