from __future__ import annotations

import sys
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from assembler import assemble  # noqa: E402
from emulator import Emulator  # noqa: E402


class AssembleAndRunTests(unittest.TestCase):
    def test_assembled_program_runs_in_emulator(self) -> None:
        source = """
        start: MOV r0, r1
               ADD r0, r2
               HALT
        """
        emulator = Emulator()
        emulator.state.registers[1] = 9
        emulator.state.registers[2] = 4
        emulator.load_program(assemble(source))

        state = emulator.run()

        self.assertTrue(state.halted)
        self.assertIsNone(state.fault)
        self.assertEqual(state.registers[0], 13)
