from __future__ import annotations

import sys
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from assembler import AssembleError, assemble  # noqa: E402


class MinimalAssemblerTests(unittest.TestCase):
    def test_assemble_halt(self) -> None:
        self.assertEqual(assemble("HALT"), bytes.fromhex("0000"))

    def test_assemble_mov_and_add(self) -> None:
        program = assemble(
            """
            MOV r0, r1
            ADD r0, r2
            """
        )

        self.assertEqual(program, bytes.fromhex("1020 2030"))

    def test_assemble_jmp_label(self) -> None:
        program = assemble(
            """
            JMP done
            NOP
            done: HALT
            """
        )

        self.assertEqual(program, bytes.fromhex("2040 0010 0000"))

    def test_assemble_jmp_numeric_target(self) -> None:
        program = assemble("JMP 0x0A")
        self.assertEqual(program, bytes.fromhex("A040"))

    def test_ignores_comments_and_blank_lines(self) -> None:
        program = assemble(
            """
            ; comment
            NOP ; trailing comment

            HALT
            """
        )

        self.assertEqual(program, bytes.fromhex("0010 0000"))

    def test_duplicate_label_raises_error(self) -> None:
        with self.assertRaisesRegex(AssembleError, "duplicate label"):
            assemble(
                """
                start: NOP
                start: HALT
                """
            )

    def test_invalid_register_raises_error(self) -> None:
        with self.assertRaisesRegex(AssembleError, "invalid register"):
            assemble("MOV r8, r0")

    def test_invalid_jump_target_raises_error(self) -> None:
        with self.assertRaisesRegex(AssembleError, "invalid jump target"):
            assemble("JMP nowhere")

    def test_jump_target_range_is_checked(self) -> None:
        with self.assertRaisesRegex(AssembleError, "out of range"):
            assemble("JMP 256")
