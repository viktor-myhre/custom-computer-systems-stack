from __future__ import annotations

from dataclasses import dataclass
import re


REGISTER_NAMES = {f"r{index}": index for index in range(8)}


class AssembleError(Exception):
    """Raised when assembly source cannot be encoded."""


@dataclass
class ParsedLine:
    line_number: int
    mnemonic: str
    operands: list[str]


def assemble(source: str) -> bytes:
    labels, parsed_lines = _first_pass(source)
    output = bytearray()
    for instruction_index, parsed_line in enumerate(parsed_lines):
        output.extend(_encode_line(parsed_line, labels, instruction_index))
    return bytes(output)


def _first_pass(source: str) -> tuple[dict[str, int], list[ParsedLine]]:
    labels: dict[str, int] = {}
    parsed_lines: list[ParsedLine] = []
    instruction_index = 0

    for line_number, raw_line in enumerate(source.splitlines(), start=1):
        line = _strip_comment(raw_line).strip()
        if not line:
            continue

        while True:
            label_match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$", line)
            if label_match is None:
                break
            label_name = label_match.group(1)
            if label_name in labels:
                raise AssembleError(f"line {line_number}: duplicate label '{label_name}'")
            labels[label_name] = instruction_index
            line = label_match.group(2).strip()
            if not line:
                break
        if not line:
            continue

        mnemonic, operands = _parse_instruction(line, line_number)
        parsed_lines.append(ParsedLine(line_number=line_number, mnemonic=mnemonic, operands=operands))
        instruction_index += 1

    return labels, parsed_lines


def _strip_comment(line: str) -> str:
    return line.split(";", 1)[0]


def _parse_instruction(line: str, line_number: int) -> tuple[str, list[str]]:
    parts = line.split(None, 1)
    mnemonic = parts[0].upper()
    operand_text = parts[1] if len(parts) > 1 else ""
    operands = [operand.strip() for operand in operand_text.split(",")] if operand_text else []
    operands = [operand for operand in operands if operand]

    if operand_text and "," not in operand_text and len(operands) > 1:
        raise AssembleError(f"line {line_number}: invalid operand list")

    return mnemonic, operands


def _encode_line(parsed_line: ParsedLine, labels: dict[str, int], instruction_index: int) -> bytes:
    mnemonic = parsed_line.mnemonic
    operands = parsed_line.operands
    line_number = parsed_line.line_number

    if mnemonic == "HALT":
        _require_operand_count(line_number, mnemonic, operands, 0)
        return _encode_word(0x0)
    if mnemonic == "NOP":
        _require_operand_count(line_number, mnemonic, operands, 0)
        return _encode_word(0x1)
    if mnemonic == "MOV":
        _require_operand_count(line_number, mnemonic, operands, 2)
        return _encode_word(0x2, _parse_register(operands[0], line_number), _parse_register(operands[1], line_number))
    if mnemonic == "ADD":
        _require_operand_count(line_number, mnemonic, operands, 2)
        return _encode_word(0x3, _parse_register(operands[0], line_number), _parse_register(operands[1], line_number))
    if mnemonic == "JMP":
        _require_operand_count(line_number, mnemonic, operands, 1)
        target = _parse_jump_target(operands[0], labels, line_number)
        return _encode_word(0x4, (target >> 4) & 0xF, target & 0xF)

    raise AssembleError(f"line {line_number}: unknown instruction '{mnemonic}'")


def _require_operand_count(line_number: int, mnemonic: str, operands: list[str], expected: int) -> None:
    if len(operands) != expected:
        raise AssembleError(
            f"line {line_number}: instruction '{mnemonic}' expects {expected} operand(s), got {len(operands)}"
        )


def _parse_register(token: str, line_number: int) -> int:
    register_index = REGISTER_NAMES.get(token.lower())
    if register_index is None:
        raise AssembleError(f"line {line_number}: invalid register '{token}'")
    return register_index


def _parse_jump_target(token: str, labels: dict[str, int], line_number: int) -> int:
    if token in labels:
        return labels[token]

    try:
        if token.lower().startswith("0x"):
            value = int(token, 16)
        else:
            value = int(token, 10)
    except ValueError as exc:
        raise AssembleError(f"line {line_number}: invalid jump target '{token}'") from exc

    if value < 0 or value > 0xFF:
        raise AssembleError(f"line {line_number}: jump target out of range '{token}'")
    return value


def _encode_word(opcode: int, a: int = 0, b: int = 0, c: int = 0) -> bytes:
    instruction = ((opcode & 0xF) << 12) | ((a & 0xF) << 8) | ((b & 0xF) << 4) | (c & 0xF)
    return instruction.to_bytes(2, byteorder="little")
