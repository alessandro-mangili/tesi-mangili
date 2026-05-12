import angr, logging
import claripy # type: ignore
from moduli.abs_hook import *

THUMB = 1
BOOT_RESET_HANLDER = 0x08001e34
BOOT_MAIN = 0x08007fb8

USART1 = 0x40013800
USART2 = 0x40004400
USART3 = 0x40004800
UART4 = 0x40004C00
UART5 = 0x40005000

def add_uart_breakpoints(s):
    s.inspect.b('mem_write', mem_write_address=USART1 + 0x28, when=angr.BP_AFTER, action=OnUsartTDRWrite)
    s.inspect.b('mem_write', mem_write_address=USART2 + 0x28, when=angr.BP_AFTER, action=OnUsartTDRWrite)
    s.inspect.b('mem_write', mem_write_address=USART3 + 0x28, when=angr.BP_AFTER, action=OnUsartTDRWrite)
    s.inspect.b('mem_write', mem_write_address=UART4 + 0x28, when=angr.BP_AFTER, action=OnUsartTDRWrite)
    s.inspect.b('mem_write', mem_write_address=UART5 + 0x28, when=angr.BP_AFTER, action=OnUsartTDRWrite)


def OnUsartTDRWrite(state):
    addr_expr = state.inspect.mem_write_address
    addr = state.solver.eval(addr_expr)
    
    expr = state.inspect.mem_write_expr
    conc_data = state.solver.eval(expr)
    data = conc_data & 0xFF 
    print(f"\t{hex(addr)} -> {chr(data)}")


proj = angr.Project('../Firmware/walk400h.bin',
    arch='ARMCortexM',
    main_opts={'backend': 'blob', 'base_addr': 0x08000000,
               'entry_point': BOOT_RESET_HANLDER + THUMB}
)

state = proj.factory.entry_state(
    add_options={
        angr.options.ZERO_FILL_UNCONSTRAINED_REGISTERS,
        angr.options.ZERO_FILL_UNCONSTRAINED_MEMORY,
    }
)

for addr in [
    0x08001ef8,  # HAL_Init
    0x08002c04,  # HAL_PWREx_EnableBatteryCharging
    0x08002b64,  # HAL_PWR_EnableBkUpAccess
    0x080006e4,  # walk_clocks_setup
    0x0800084c,  # walk_gpio_setup
    0x08000b00,  # walk_gpio_setup_2
    0x080007c0,  # walk_gpio_setup_3
]:
    proj.hook(addr + 1, DoNothing())

proj.hook(0x080053f8 + THUMB, ReturnZero())  # UART_WaitOnFlagUntilTimeout

simgr = proj.factory.simulation_manager(state)

for s in simgr.active:
    if not hasattr(s, '_uart_hooks_added'):
        add_uart_breakpoints(s)
        s._uart_hooks_added = True

while len(simgr.active) > 0:
    try:
        simgr.step(num_inst=1)
    except Exception as e:
        print(f'error on state {simgr.active}: {str(e)}')
        simgr.move(from_stash='active', to_stash='_Drop')
    print(f'\rsimgr: {simgr}, active: {simgr.active}, errored: {simgr.errored}, deadneded: {simgr.deadended}', end= "")
