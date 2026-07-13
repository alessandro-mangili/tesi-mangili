import angr, logging

THUMB = 1
BOOT_RESET_HANLDER = 0x08001e34

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

simgr = proj.factory.simulation_manager(state)

while len(simgr.active) > 0:
    try:
        simgr.step(num_inst=1)
    except Exception as e:
        print(f'error on state {simgr.active}: {str(e)}')
        simgr.move(from_stash='active', to_stash='_Drop')
    print(f'\rsimgr: {simgr}, active: {simgr.active}, errored: {simgr.errored}, deadneded: {simgr.deadended}', end="")
