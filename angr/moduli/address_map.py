# Mappa delle funzioni principali in boot_main
func_names = {
    0x08001e35: "boot_reset_handler",
    0x08001e89: "boot_generic_setup",
    0x08008cfd: "__libc_init_array",
    0x08002269: "FLASH_WaitForLastOperation",
    
    # HAL / Hardware Init
    0x08001ef9: "HAL_Init",
    0x08002c05: "HAL_PWREx_EnableBatteryCharging",
    0x08002b65: "HAL_PWR_EnableBkUpAccess",
    0x08001f21: "HAL_GetTick",
    0x08001f2d: "HAL_Delay",
    0x08002395: "HAL_FLASH_OB_Launch",
    0x0800220d: "HAL_FLASH_Unlock",      
    0x08002231: "HAL_FLASH_Lock",        
    0x080022f1: "HAL_FLASH_Program",     
    0x080028a9: "HAL_FLASHEx_Erase",    
    0x08005653: "HAL_UART_Init",

    # Walk - Setup Hardware
    0x080006e5: "walk_clocks_setup",
    0x0800084d: "walk_gpio_setup",
    0x08000b01: "walk_gpio_setup_2",
    0x080007c1: "walk_gpio_setup_3",
    0x08000809: "walk_uart_setup",
    0x08000d49: "walk_buzzer_setup",
    0x08001b6d: "walk_tft_setup",
    0x08000bbd: "walk_check_usb_connection",
    0x08000e25: "walk_start_oc_buzzer",

    # Walk - Display
    0x0800176d: "walk_set_font_scale",
    0x080011ef: "scr_something_3",
    0x080018ad: "draw_to_scr",
    0x0800110f: "FUN_0800110e",

    # Walk - Boot Flow
    0x08007fb9: "boot_main",
    0x08001e35: "boot_reset_handler",
    0x08007edd: "run_app",
    0x08018275: "app_reset_handler",
    0x0801c141: "app_main",

    # Walk - Update Flow
    0x08008475: "check_sd_card",
    0x08007be5: "walk_check_update_file",    
    0x08007ce9: "walk_program_flash",
    0x08008595: "walk_do_flash_programming", 
    0x080084c9: "walk_preparing_flash",    
    0x080084e5: "walk_start_flash_erase",  
    0x08007de1: "walk_update_flash",
    0x080022f1: "HAL_FLASH_Program",

    # Walk - Security
    0x080085f8: "walk_is_wrp_enabled",    
    0x08008704: "walk_disable_wrp",       
    0x08007ab0: "walk_sign_flash",        

    # FatFS
    0x08007465: "f_open",
    0x08007631: "f_read",
    0x0800789d: "f_stat",                 
    0x0800787b: "f_close",               
    0x080078f5: "f_unlink",              
    0x080084a5: "walk_close_fs",         

    # Misc
    0x08008c49: "printf",
    0x08007f85: "FUN_08007f84",
    0x08007ead: "idk",
    0x080004fd: "mod_strcmp",             
    0x08008feb: "strcpy",                
    0x08008fcd: "strcat",                
    0x08008d7f: "memset",       
    0x800625b: "validate"        
}

"""
Dato un indirizzo ritorna il nome della funzione corrispondente.
Se l'indirizzo è all'interno di una funzione, ritorna il nome della funzione stessa.

Args:
    addr: Indirizzo da risolvere (int, bool)

Returns:
    str: Nome della funzione o l'indrizzo stesso se non trovato
"""

def get_function_name(cfg, addr, back_to_flag):
    
    if not func_names.get(addr, "") == "":
        return func_names.get(addr, "")
    else:
        for func_addr, func in cfg.kb.functions.items():
            if func.addr < addr < func.addr + func.size:
                n = func_names.get(func.addr, "")
                if n:
                    return n if not back_to_flag else "back to: " + n
    
    return f"{addr:#x}" 



def print_path(s, cfg):
    jks = list(s.history.jumpkinds)
    jts = list(s.history.jump_targets)

    cnt = 0
    if (len(jks) == (len(jts) + 1)) and (jks[0] == "Ijk_Boring"):
        del jks[0]

    depth = 0
    print(" " * depth + get_function_name(cfg, s.project.entry, False))
    for i, k in enumerate(jks):
        if k == "Ijk_Call":
            depth += 1
            addr = s.solver.eval(jts[i])
            if addr in cfg.functions:
                print("│   " * (depth - 1) + ("├── " if depth > 0 else "") + get_function_name(cfg, addr, False))
            else:
                name = hex(addr)
                print("│   " * (depth - 1) + ("├── " if depth > 0 else "") + name)
        elif k == "Ijk_Ret":
            depth -= 1
    
    print(f"\nTotal jumps (jumpkinds): {len(s.history.jumpkinds)}")        
    