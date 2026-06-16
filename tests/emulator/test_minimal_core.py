from __future__ import annotations

import sys
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from emulator import Emulator  # noqa: E402


def encode(opcode: int, a: int = 0, b: int = 0, c: int = 0) -> bytes:
    instruction = ((opcode & 0xF) << 12) | ((a & 0xF) << 8) | ((b & 0xF) << 4) | (c & 0xF)
    return instruction.to_bytes(2, byteorder="little")


class MinimalCoreTests(unittest.TestCase):
    def test_halt_program_sets_halted_state(self) -> None:
        emulator = Emulator()
        emulator.load_program(encode(0x0))

        state = emulator.run()

        self.assertTrue(state.halted)
        self.assertIsNone(state.fault)
        self.assertEqual(state.pc, 0)

    def test_nop_advances_program_counter(self) -> None:
        emulator = Emulator()
        emulator.load_program(encode(0x1) + encode(0x0))

        state = emulator.step()

        self.assertEqual(state.pc, 2)
        self.assertFalse(state.halted)
        self.assertIsNone(state.fault)

    def test_mov_copies_register_value(self) -> None:
        emulator = Emulator()
        emulator.state.registers[3] = 0x1234
        emulator.load_program(encode(0x2, a=1, b=3))

        state = emulator.step()

        self.assertEqual(state.registers[1], 0x1234)
        self.assertEqual(state.pc, 2)
        self.assertIsNone(state.fault)

    def test_add_wraps_to_16_bits(self) -> None:
        emulator = Emulator()
        emulator.state.registers[2] = 0xFFFF
        emulator.state.registers[4] = 0x0002
        emulator.load_program(encode(0x3, a=2, b=4))

        state = emulator.step()

        self.assertEqual(state.registers[2], 0x0001)
        self.assertEqual(state.pc, 2)
        self.assertIsNone(state.fault)

    def test_jmp_uses_absolute_instruction_index(self) -> None:
        emulator = Emulator()
        program = encode(0x4, a=0x0, b=0x3) + encode(0x0) + encode(0x0) + encode(0x0)
        emulator.load_program(program)

        state = emulator.step()

        self.assertEqual(state.pc, 6)
        self.assertFalse(state.halted)
        self.assertIsNone(state.fault)

    def test_reserved_field_faults_decode(self) -> None:
        emulator = Emulator()
        emulator.load_program(encode(0x1, c=1))

        state = emulator.step()

        self.assertEqual(state.fault, "decode error: reserved field must be zero")
        self.assertFalse(state.halted)

    def test_fetch_beyond_memory_faults(self) -> None:
        emulator = Emulator()
        emulator.state.pc = 0xFFFF

        state = emulator.step()

        self.assertEqual(state.fault, "memory error: instruction fetch out of bounds at 0xFFFF")
        self.assertFalse(state.halted)

    def test_small_program_runs_to_completion(self) -> None:
        emulator = Emulator()
        emulator.state.registers[1] = 5
        emulator.state.registers[2] = 7
        program = b"".join(
            [
                encode(0x2, a=0, b=1),
                encode(0x3, a=0, b=2),
                encode(0x0),
            ]
        )
        emulator.load_program(program)

        state = emulator.run()

        self.assertTrue(state.halted)
        self.assertIsNone(state.fault)
        self.assertEqual(state.registers[0], 12)


if __name__ == "__main__":
    unittest.main()
