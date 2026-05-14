import angr, logging
from moduli.boot_hook import *
from moduli.print_logger import *
from moduli.abs_hook import *
from moduli.address_map import *

THUMB = 1
BOOT_MAIN = 0x08007fb8
ENTRY_POINT = 0x08007ff0
PRINTF = 0x08008c48
MEMSET = 0x08008d7e
MEMCPY = 0x08008d68
USART3 = 0x40004800
FLASH_BASE = 0x0800e000
BOOT_RESET_HANLDER = 0x08001e34
RUN_APP = 0x08007edc
WALK_FLASH_UPDATE = 0x08007de0

logging.getLogger('angr').setLevel(logging.ERROR)

# entry-point --> boot_main
proj = angr.Project('../Firmware/walk400h.bin',
    arch='ARMCortexM',
    main_opts={'backend': 'blob', 'base_addr': 0x08000000,
               'entry_point': BOOT_RESET_HANLDER + THUMB}
)

cfg = proj.analyses.CFGFast()           
     
# Hook init hardware - skip
for addr in [
    0x08001ef8,  # HAL_Init
    0x08002c04,  # HAL_PWREx_EnableBatteryCharging
    0x08002b64,  # HAL_PWR_EnableBkUpAccess
    0x080006e4,  # walk_clocks_setup
    0x0800084c,  # walk_gpio_setup
    0x08000b00,  # walk_gpio_setup_2
    0x080007c0,  # walk_gpio_setup_3
    0x08000808,  # walk_uart_setup
    0x08000d48,  # walk_buzzer_setup
    0x08001b6c,  # walk_tft_setup
    0x08000bbc,  # walk_check_usb_connection
    0x08001f20,  # HAL_GetTick
    0x08007f84,  # FUN_08007f84
    0x08000e24,  # walk_start_oc_buzzer 
    0x0800176c,  # walk_set_font_scale
    0x080011ee,  # scr_something_3
    0x080018ac,  # draw_to_scr
    0x0800110e,  # FUN_0800110e
    0x08001f2c,  # HAL_Delay
    0x08002394,  # HAL_FLASH_OB_Launch
    0x08002230,  # HAL_FLASH_Lock
]:
    proj.hook(addr + THUMB, DoNothing())

proj.hook(0x08007eac + THUMB, HookIDK())

proj.hook(0x08008474 + THUMB, ReturnZero())   # check_sd_card -> 0
proj.hook(0x08007464 + THUMB, ReturnZero())   # f_open -> 1 (FR_DISK_ERR, file non trovato)
proj.hook(PRINTF + THUMB, HookPrintf())   # hooking di printf


# simulare valori di ritorno delle funzioni sottostanti in modo da far ritornare il file di update

proj.hook(0x0800789c + THUMB, HookFStat())  #f_stat -> 0 copia info da file_struct a filinfo
proj.hook(0x08007630 + THUMB, HookFRead())  #f_read -> 0 quelo che fa f_read é prendere da file_struct qualcosa e copiare in magic il valore magic
 
# Ho Simulato solo il caso in cui WRP sia giá disabilitata
proj.hook(0x080085f8 + THUMB, ReturnZero())  # walk_is_wrp_enabled


proj.hook(0x0800220c + THUMB, ReturnZero())  # HAL_FLASH_Unlock -> OK
proj.hook(0x080028a8 + THUMB, ReturnZero())  # HAL_FLASHEx_Erase -> HAL_OK

proj.hook(0x080022f0 + THUMB, ReturnZero())  # HAL_FLASH_Program

proj.hook(0x08008594 + THUMB, ReturnZero())   # walk_do_flash_programming
proj.hook(0x080011ee + THUMB, ReturnZero())   # src_something

proj.hook(MEMSET, angr.procedures.SIM_PROCEDURES['libc']['memset']())
proj.hook(MEMCPY, angr.procedures.SIM_PROCEDURES['libc']['memcpy']())

state = proj.factory.entry_state(
    add_options={
        # in caso di memoria e registri non inizializzati angr li mette a 0
        angr.options.ZERO_FILL_UNCONSTRAINED_REGISTERS,
        angr.options.ZERO_FILL_UNCONSTRAINED_MEMORY,
    }
)

state.memory.store(0x20000000, b'\x00' * 0x20000)
state.register_plugin('printf_log', PrintfLogger())

simgr = proj.factory.simulation_manager(state)
simgr.explore(
    find=WALK_FLASH_UPDATE + THUMB, 
    avoid=[
        RUN_APP + THUMB
    ],
    n=5000
)

print("")
print(f"Found: {len(simgr.found)}")
print(f"Active: {len(simgr.active)}")
print(f"Errored: {len(simgr.errored)}")
print(f"Avoid: {len(simgr.avoid)}")
print(f"Deadended: {len(simgr.deadended)}")

if simgr.found:
    s = simgr.found[0]
    
    # Larghezza uniforme per tutte le sezioni
    WIDTH = 80
    
    def print_section(title):
        padding = (WIDTH - len(title) - 2) // 2
        print(f"\n{'='*padding} {title} {'='*padding}")
        if len(title) % 2 == 1:
            print('=' * WIDTH)
        else:
            print()
    
    # ==================== Constraints ====================
    print_section("Constraints")
    
    if s.solver.constraints:
        print(f"  Total constraints: {len(s.solver.constraints)}\n")
        for i, c in enumerate(s.solver.constraints, 1):
            print(f"  [{i:2d}] {c}")
    else:
        print("  No constraints")
    
    # ==================== Call Stack ====================
    print_section("Call Stack")
    
    for i, frame in enumerate(s.callstack):

        st = "%d | %s -> %s, returning to %s" % (
            i,
            get_function_name(cfg, frame.call_site_addr, False),
            get_function_name(cfg, frame.func_addr, False),
            get_function_name(cfg, frame.current_return_target, False)
        )
        print(st)
    
    # ==================== Execution Path ====================
    print_section("Execution Path")
    
    print_path(s, cfg)
    
    # ==================== Printf Logs ====================
    print_section("Printf Logs")
    
    logs = s.get_plugin('printf_log').messages
    if logs:
        for i, msg in enumerate(logs, 1):
            print(f"  [{i:2d}] {msg.strip()}")
    else:
        print("  No messages logged")
    
    # ==================== Footer ====================
    print(f"\n{'='*WIDTH}\n")