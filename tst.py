from xpire.scenes.cpm import CPM80_Scene

scene = CPM80_Scene()
scene.load_rom("../vcpu/8080PRE.COM")

from spyce_nvaders.cpu import emulate, State

with open("../vcpu/8080PRE.COM", "rb") as f:
    memory = bytearray(f.read())

memory = bytearray(0x100) + memory
memory += bytearray(0x10000 - len(memory))

state = State(memory)
state.pc = 0x100

cpu = scene.cpu
cpu.PC = 0x100


state.memory[0x0005] = 0xC9
cpu.memory[0x0005] = 0xC9

while True:

    assert cpu.PC == state.pc, f"cpu.PC={cpu.PC}, state.pc={state.pc}"

    _1_1 = cpu.memory[cpu.PC & 0xFFFF]
    _1_2 = cpu.memory[(cpu.PC + 1) & 0xFFFF]
    _1_3 = cpu.memory[(cpu.PC + 2) & 0xFFFF]

    _2_1 = state.memory[state.pc & 0xFFFF]
    _2_2 = state.memory[(state.pc + 1) & 0xFFFF]
    _2_3 = state.memory[(state.pc + 2) & 0xFFFF]

    assert _1_1 == _2_1, f"{_1_1:02x} {_2_1:02x} --> {cpu.PC:04x}, {state.pc:04x}"
    assert _1_2 == _2_2, f"{_1_2:02x} {_2_2:02x} --> {cpu.PC:04x}, {state.pc:04x}"
    assert _1_3 == _2_3, f"{_1_3:02x} {_2_3:02x} --> {cpu.PC:04x}, {state.pc:04x}"

    print(f"{_1_1:02x} {_1_2:02x} {_1_3:02x}, {_2_1:02x} {_2_2:02x} {_2_3:02x}")

    pc_is_zero_1 = cpu.PC == 0x00
    pc_is_zero_2 = state.pc == 0x00

    assert pc_is_zero_1 == pc_is_zero_2, f"{cpu.PC:04x} {state.pc:04x}"

    if state.pc == 0x00:
        break

    if cpu.PC == 0x00:
        break

    cpu.execute_instruction()
    emulate(state)

    assert (
        cpu.registers.A == state.a
    ), f"cpu.registers.A={cpu.registers.A}, state.a={state.a}"

    assert (
        cpu.registers.B == state.b
    ), f"cpu.registers.B={cpu.registers.B}, state.b={state.b}"

    assert (
        cpu.registers.C == state.c
    ), f"cpu.registers.C={cpu.registers.C}, state.c={state.c}"

    assert (
        cpu.registers.D == state.d
    ), f"cpu.registers.D={cpu.registers.D}, state.d={state.d}"

    assert (
        cpu.registers.E == state.e
    ), f"cpu.registers.E={cpu.registers.E}, state.e={state.e}"

    assert (
        cpu.registers.H == state.h
    ), f"cpu.registers.H={cpu.registers.H}, state.h={state.h}"

    assert (
        cpu.registers.L == state.l
    ), f"cpu.registers.L={cpu.registers.L}, state.l={state.l}"

    assert (
        cpu.flags.A == state._cc.ac
    ), f"cpu.flags.A={cpu.flags.A}, state.flags.a={state._cc.ac}"

    assert (
        cpu.flags.Z == state._cc.z
    ), f"cpu.flags.Z={cpu.flags.Z}, state.flags.z={state._cc.z}"

    assert (
        cpu.flags.S == state._cc.s
    ), f"cpu.flags.S={cpu.flags.S}, state.flags.s={state._cc.s}"

    assert (
        cpu.flags.C == state._cc.cy
    ), f"cpu.flags.C={cpu.flags.C}, state.flags.cy={state._cc.cy}"

    assert (
        cpu.flags.P == state._cc.p
    ), f"cpu.flags.P={cpu.flags.P}, state.flags.p={state._cc.p}"

    assert (cpu.SP & 0xFFFF) == (
        state.sp & 0xFFFF
    ), f"cpu.SP={cpu.SP}, state.sp={state.sp}"
