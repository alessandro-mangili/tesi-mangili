import angr, logging
from moduli.print_logger import *
from moduli.abs_hook import *
from moduli.memory_write_handler import *
from moduli.boot_hook import *
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


logging.getLogger('angr').setLevel('ERROR')

# entry-point --> boot_main
proj = angr.Project('../Firmware/walk400h.bin',
    arch='ARMCortexM',
    main_opts={'backend': 'blob', 'base_addr': 0x08000000,
               'entry_point': BOOT_RESET_HANLDER + THUMB}
)
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
    0x080084c8,  # walk_preparing_flash
    0x08008d7e,  # memset
    0x08002230,  # HAL_FLASH_Lock
    0x08002848, 
    
]:
    proj.hook(addr + THUMB, DoNothing())
    

proj.hook(0x08007eac + THUMB, HookIDK())

proj.hook(0x08008474 + THUMB, ReturnZero())     # check_sd_card -> 0 (OK)
proj.hook(0x08007464 + THUMB, ReturnZero())     # f_open -> 0
proj.hook(PRINTF + THUMB, HookPrintf())     # hooking di printf

proj.hook(0x0800789c + THUMB, HookFStat())      #f_stat -> 0 
proj.hook(0x08007630 + THUMB, HookFRead())      #f_read -> 0 

proj.hook(0x080085f8 + THUMB, ReturnZero())     # walk_is_wrp_enabled

proj.hook(0x0800220c + THUMB, ReturnZero())     # HAL_FLASH_Unlock -> OK
proj.hook(0x080028a8 + THUMB, ReturnZero())     # HAL_FLASHEx_Erase -> HAL_OK

proj.hook(0x080011ee + THUMB, ReturnZero())     # src_something

proj.hook(0x080084e4 + THUMB, ReturnZero())     # walk_start_flash_erase

proj.hook(0x08007b2c + THUMB, DoNothing())      # walk_is_firmware_demo

proj.hook(0x08002268 + THUMB, ReturnZero())     # FLASH_WaitForLastOperation

proj.hook(MEMSET, angr.procedures.SIM_PROCEDURES['libc']['memset']())
proj.hook(MEMCPY, angr.procedures.SIM_PROCEDURES['libc']['memcpy']())

state = proj.factory.entry_state(
    add_options={
        # in caso di memoria e registri non inizializzati angr li mette a 0
        angr.options.ZERO_FILL_UNCONSTRAINED_REGISTERS,
        angr.options.ZERO_FILL_UNCONSTRAINED_MEMORY,
    }
)

cfg = proj.analyses.CFGFast()

state.memory.store(0x20000000, b'\x00' * 0x20000)

state.inspect.b('mem_write', mem_write_address = FLASH_BASE, when=angr.BP_BEFORE, action=flash_write_handler)
state.register_plugin('printf_log', PrintfLogger())

simgr = proj.factory.simulation_manager(state)

simgr.explore(
    find= lambda s: 'flash_write' in s.globals, 
    avoid = [RUN_APP + THUMB ],
    n=5000
)

print("")
print(f"Found: {len(simgr.found)}")
print(f"Active: {len(simgr.active)}")
print(f"Errored: {len(simgr.errored)}")
print(f"Deadended: {len(simgr.deadended)}")

if simgr.found:
    s = simgr.found[0]
    
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
        print(f"Constraints: {len(s.solver.constraints)}")
        for c in s.solver.constraints:
            print(f"  {c}")
    
    # ==================== Stack ====================       
    print_section("Stack")
    for i, frame in enumerate(s.callstack):
    
        st = "%d | %s -> %s, returning to %s" % (
            i,
            get_function_name(cfg, frame.call_site_addr, False),
            get_function_name(cfg, frame.func_addr, False),
            get_function_name(cfg, frame.current_return_target, False)
        )
        print(st)
    
    # ==================== Path ====================
    print_section("Path")
    print_path(s, cfg)
    

    # ==================== Printf ====================
    print_section("Printf")
    logs = s.get_plugin('printf_log').messages

    for i, msg in enumerate(logs):
        print(f"  [{i}] {msg.strip()}")
        
    # ==================== Footer ====================
    print(f"\n{'='*WIDTH}\n")

