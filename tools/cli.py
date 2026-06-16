from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from assembler import AssembleError, assemble
from emulator import DecodeFault, Emulator, MemoryFault, decode_instruction_fields


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "assemble":
        return assemble_command(args)
    if args.command == "run":
        return run_command(args)

    parser.print_help()
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Command-line tools for the custom computer systems stack.")
    subparsers = parser.add_subparsers(dest="command")

    assemble_parser = subparsers.add_parser("assemble", help="Assemble an .asm source file into machine bytes.")
    assemble_parser.add_argument("source", help="Path to the assembly source file.")
    assemble_parser.add_argument(
        "-o",
        "--output",
        help="Optional output path. Binary output is written as bytes; hex output is written as text.",
    )
    assemble_parser.add_argument(
        "--format",
        choices=("hex", "bin"),
        default="hex",
        help="Output format. Default: hex.",
    )

    run_parser = subparsers.add_parser("run", help="Run an assembly or binary program in the emulator.")
    run_parser.add_argument("source", help="Path to an assembly source file or raw binary file.")
    run_parser.add_argument(
        "--input-format",
        choices=("asm", "bin"),
        default="asm",
        help="Input format. Default: asm.",
    )
    run_parser.add_argument(
        "--max-steps",
        type=int,
        default=1000,
        help="Maximum number of execution steps before aborting. Default: 1000.",
    )
    run_parser.add_argument(
        "--trace",
        action="store_true",
        help="Print one trace line per instruction before execution.",
    )

    return parser


def assemble_command(args: argparse.Namespace) -> int:
    try:
        program = assemble(read_text_file(args.source))
    except (AssembleError, OSError) as exc:
        print(f"assemble error: {exc}", file=sys.stderr)
        return 1

    if args.output:
        output_path = Path(args.output)
        if args.format == "bin":
            output_path.write_bytes(program)
        else:
            output_path.write_text(format_program_hex(program) + "\n", encoding="ascii")
    else:
        if args.format == "bin":
            print("assemble error: binary output requires --output", file=sys.stderr)
            return 1
        print(format_program_hex(program))

    return 0


def run_command(args: argparse.Namespace) -> int:
    try:
        program = load_program_bytes(args.source, args.input_format)
    except (AssembleError, OSError) as exc:
        print(f"run error: {exc}", file=sys.stderr)
        return 1

    emulator = Emulator()
    try:
        emulator.load_program(program)
        step_count = 0
        while not emulator.state.halted and emulator.state.fault is None:
            if step_count >= args.max_steps:
                raise RuntimeError("maximum step count exceeded")
            if args.trace:
                print(trace_line(emulator, step_count))
            emulator.step()
            step_count += 1
    except (MemoryFault, RuntimeError) as exc:
        print(f"run error: {exc}", file=sys.stderr)
        return 1

    print(render_final_state(emulator, step_count))
    return 0 if emulator.state.fault is None else 1


def read_text_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def load_program_bytes(path: str, input_format: str) -> bytes:
    file_path = Path(path)
    if input_format == "bin":
        return file_path.read_bytes()
    return assemble(read_text_file(path))


def format_program_hex(program: bytes) -> str:
    if len(program) % 2 != 0:
        return program.hex().upper()
    words = [program[index : index + 2].hex().upper() for index in range(0, len(program), 2)]
    return " ".join(words)


def trace_line(emulator: Emulator, step_count: int) -> str:
    instruction = emulator.read_instruction()
    opcode, a, b, c = decode_instruction_fields(instruction)
    return (
        f"STEP {step_count:04d} "
        f"PC=0x{emulator.state.pc:04X} "
        f"INSTR=0x{instruction:04X} "
        f"OP=0x{opcode:X} A=0x{a:X} B=0x{b:X} C=0x{c:X}"
    )


def render_final_state(emulator: Emulator, step_count: int) -> str:
    state = emulator.state
    status = "HALTED" if state.halted and state.fault is None else "FAULT"
    registers = " ".join(f"r{index}=0x{value:04X}" for index, value in enumerate(state.registers))
    lines = [
        f"STATUS {status}",
        f"STEPS {step_count}",
        f"PC 0x{state.pc:04X}",
        f"REGISTERS {registers}",
    ]
    if state.fault is not None:
        lines.append(f"FAULT {state.fault}")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
