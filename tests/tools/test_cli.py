from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class CLITests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "tools.cli", *args],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_assemble_prints_hex_output(self) -> None:
        result = self.run_cli("assemble", "examples/asm/minimal-halt.asm")

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "0000")
        self.assertEqual(result.stderr, "")

    def test_assemble_can_write_binary_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "program.bin"
            result = self.run_cli(
                "assemble",
                "examples/asm/minimal-halt.asm",
                "--format",
                "bin",
                "--output",
                str(output_path),
            )

            self.assertEqual(result.returncode, 0)
            self.assertEqual(output_path.read_bytes(), bytes.fromhex("0000"))

    def test_run_reports_halted_status(self) -> None:
        result = self.run_cli("run", "examples/asm/minimal-halt.asm")

        self.assertEqual(result.returncode, 0)
        self.assertIn("STATUS HALTED", result.stdout)
        self.assertIn("PC 0x0000", result.stdout)

    def test_run_trace_prints_step_lines(self) -> None:
        result = self.run_cli("run", "examples/asm/minimal-halt.asm", "--trace")

        self.assertEqual(result.returncode, 0)
        self.assertIn("STEP 0000 PC=0x0000 INSTR=0x0000 OP=0x0 A=0x0 B=0x0 C=0x0", result.stdout)
        self.assertIn("STATUS HALTED", result.stdout)

    def test_binary_output_requires_output_path(self) -> None:
        result = self.run_cli("assemble", "examples/asm/minimal-halt.asm", "--format", "bin")

        self.assertEqual(result.returncode, 1)
        self.assertIn("binary output requires --output", result.stderr)
