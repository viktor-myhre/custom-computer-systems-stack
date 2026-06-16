from __future__ import annotations

from dataclasses import dataclass, field


MEMORY_SIZE = 65536
REGISTER_COUNT = 8
WORD_MASK = 0xFFFF


class EmulatorFault(Exception):
    """Base class for emulator faults."""


class DecodeFault(EmulatorFault):
    """Raised when an instruction encoding is invalid."""


class MemoryFault(EmulatorFault):
    """Raised when instruction fetch or memory access is invalid."""


def decode_instruction_fields(instruction: int) -> tuple[int, int, int, int]:
    opcode = (instruction >> 12) & 0xF
    a = (instruction >> 8) & 0xF
    b = (instruction >> 4) & 0xF
    c = instruction & 0xF
    return opcode, a, b, c


@dataclass
class CPUState:
    registers: list[int] = field(default_factory=lambda: [0] * REGISTER_COUNT)
    pc: int = 0
    halted: bool = False
    fault: str | None = None


class Emulator:
    def __init__(self) -> None:
        self.memory = bytearray(MEMORY_SIZE)
        self.state = CPUState()

    def reset(self) -> None:
        self.memory = bytearray(MEMORY_SIZE)
        self.state = CPUState()

    def load_program(self, program: bytes, start_address: int = 0) -> None:
        end_address = start_address + len(program)
        if start_address < 0 or end_address > MEMORY_SIZE:
            raise MemoryFault("program image exceeds memory bounds")
        self.memory[start_address:end_address] = program
        self.state.pc = start_address
        self.state.halted = False
        self.state.fault = None

    def run(self, max_steps: int = 1000) -> CPUState:
        steps = 0
        while not self.state.halted and self.state.fault is None:
            if steps >= max_steps:
                raise RuntimeError("maximum step count exceeded")
            self.step()
            steps += 1
        return self.state

    def step(self) -> CPUState:
        if self.state.halted or self.state.fault is not None:
            return self.state

        try:
            instruction = self._fetch_word(self.state.pc)
            self._execute(instruction)
        except DecodeFault as exc:
            self.state.fault = f"decode error: {exc}"
        except MemoryFault as exc:
            self.state.fault = f"memory error: {exc}"
        return self.state

    def read_instruction(self, address: int | None = None) -> int:
        if address is None:
            address = self.state.pc
        return self._fetch_word(address)

    def _fetch_word(self, address: int) -> int:
        if address < 0 or address + 1 >= MEMORY_SIZE:
            raise MemoryFault(f"instruction fetch out of bounds at 0x{address:04X}")
        low = self.memory[address]
        high = self.memory[address + 1]
        return low | (high << 8)

    def _execute(self, instruction: int) -> None:
        opcode, a, b, c = decode_instruction_fields(instruction)

        if opcode == 0x0:
            self._require_zero_fields(a, b, c)
            self.state.halted = True
            return
        if opcode == 0x1:
            self._require_zero_fields(a, b, c)
            self.state.pc = (self.state.pc + 2) & WORD_MASK
            return
        if opcode == 0x2:
            self._require_register(a)
            self._require_register(b)
            self._require_zero_fields(c)
            self.state.registers[a] = self.state.registers[b]
            self.state.pc = (self.state.pc + 2) & WORD_MASK
            return
        if opcode == 0x3:
            self._require_register(a)
            self._require_register(b)
            self._require_zero_fields(c)
            self.state.registers[a] = (self.state.registers[a] + self.state.registers[b]) & WORD_MASK
            self.state.pc = (self.state.pc + 2) & WORD_MASK
            return
        if opcode == 0x4:
            self._require_zero_fields(c)
            instruction_index = (a << 4) | b
            self.state.pc = (instruction_index * 2) & WORD_MASK
            return

        raise DecodeFault(f"invalid opcode 0x{opcode:X}")

    def _require_register(self, register_index: int) -> None:
        if register_index >= REGISTER_COUNT:
            raise DecodeFault(f"invalid register r{register_index}")

    def _require_zero_fields(self, *fields: int) -> None:
        for field in fields:
            if field != 0:
                raise DecodeFault("reserved field must be zero")
