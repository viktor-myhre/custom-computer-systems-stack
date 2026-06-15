# ISA Draft 0

This document defines the initial instruction set architecture draft for the project. The goal of this draft is to support the first complete execution path from machine code to emulator behavior.

The scope of this draft is intentionally narrow. It defines enough structure to execute a minimal program image and a small set of instructions without introducing advanced runtime or operating system concerns.

## Architectural Overview

The ISA is a register-based architecture with byte-addressed memory and fixed-width instructions.

Execution state consists of:

- eight general-purpose 16-bit registers: `r0` through `r7`
- a 16-bit program counter: `pc`
- a halted flag

This draft does not define:

- privilege levels
- traps
- syscalls
- stack conventions
- interrupt handling
- condition flags

## Data Model

- Address size: 16 bits
- Register width: 16 bits
- Memory addressing unit: 8-bit byte
- Integer arithmetic: unsigned 16-bit wraparound unless a later revision defines signed interpretation for specific instructions

All addresses in this draft are byte addresses.

## Memory Model

Memory is modeled as a linear address space of 65,536 bytes.

The initial emulator should assume:

- program images are loaded into memory starting at address `0x0000`
- execution begins at `pc = 0x0000`
- the program counter always points to the first byte of the next instruction

This draft does not yet reserve memory regions for code, data, stack, devices, or kernel services.

## Instruction Encoding

Each instruction is 16 bits wide and occupies exactly 2 bytes in memory.

Instruction bytes are stored in little-endian order:

- low byte at address `pc`
- high byte at address `pc + 1`

Bit layout:

```text
15            12 11             8 7              4 3              0
+---------------+----------------+----------------+----------------+
|    opcode     |       a        |       b        |       c        |
+---------------+----------------+----------------+----------------+
```

Field interpretation depends on the opcode:

- `opcode`: instruction kind
- `a`: primary operand field
- `b`: secondary operand field
- `c`: tertiary operand field or small immediate field

Unless an instruction definition states otherwise, fields marked as ignored or reserved must be encoded as zero. A non-zero reserved field is an invalid instruction in this draft.

This fixed layout is chosen for decoder simplicity in the first implementation. A later draft may introduce wider instruction forms if the first assembler and emulator demonstrate a clear need.

## Registers

The general-purpose register file contains:

- `r0`
- `r1`
- `r2`
- `r3`
- `r4`
- `r5`
- `r6`
- `r7`

No register is reserved in this draft for stack, frame, or zero semantics.

## Execution Rules

Instruction fetch:

1. Read 2 bytes from memory at `pc`.
2. Decode the 16-bit instruction.
3. Execute the instruction semantics.
4. Advance `pc` by 2 unless the instruction explicitly assigns a new value to `pc` or halts execution.

Execution stops when:

- a `HALT` instruction executes
- an invalid opcode is encountered
- an instruction requires an invalid register field
- an instruction fetch reads beyond the valid memory range

The exact reporting mechanism belongs to the emulator, but the architectural result is that execution must stop in one of these states:

- halted successfully
- faulted by decode error
- faulted by memory error

Execution must not continue with undefined behavior after a fault.

## Instruction Set

### `HALT`

Purpose:

Stop execution successfully.

Encoding:

- opcode: `0x0`
- remaining fields must be encoded as zero

Semantics:

- set the halted flag
- leave registers unchanged
- `pc` does not need to advance after halting

Suggested canonical encoding:

```text
0x0000
```

### `NOP`

Purpose:

Perform no state change other than normal instruction sequencing.

Encoding:

- opcode: `0x1`
- remaining fields must be encoded as zero

Semantics:

- no register changes
- no memory changes
- advance `pc` by 2

Suggested canonical encoding:

```text
0x1000
```

### `MOV rd, rs`

Purpose:

Copy a register value.

Encoding:

- opcode: `0x2`
- `a`: destination register index
- `b`: source register index
- `c`: must be encoded as zero

Semantics:

- `rd <- rs`
- advance `pc` by 2

Example:

```text
MOV r1, r3
```

### `ADD rd, rs`

Purpose:

Add one register value into another register.

Encoding:

- opcode: `0x3`
- `a`: destination register index
- `b`: source register index
- `c`: must be encoded as zero

Semantics:

- `rd <- (rd + rs) mod 65536`
- advance `pc` by 2

Example:

```text
ADD r2, r4
```

### `JMP imm8`

Purpose:

Transfer control to a small absolute instruction index during the first ISA phase.

Encoding:

- opcode: `0x4`
- `a` and `b` together form an 8-bit instruction index
- `c`: must be encoded as zero

Immediate construction:

```text
imm8 = (a << 4) | b
```

Semantics:

- `pc <- imm8 * 2`

The immediate operand names an absolute instruction slot, not a raw byte address. The multiply-by-2 rule therefore converts the instruction index into a byte address in memory.

This instruction can currently target instruction slots `0x00` through `0xFF`, which correspond to byte addresses `0x0000` through `0x01FE`.

## Invalid Cases

An instruction is invalid when:

- the opcode is not defined
- a register field names a register outside `r0` through `r7`
- a reserved field that must be zero is encoded as non-zero
- an instruction fetch would read outside the valid memory range

The emulator may report more detailed diagnostics, but it should not continue execution after an invalid instruction.

## Initial Loader Convention

The initial loader convention is intentionally minimal:

- raw instruction bytes
- loaded at address `0x0000`
- execution begins at `pc = 0x0000`

This loader convention is not the same as the ISA itself. It is an initial execution convention for the first emulator phase.

No header, relocation, symbol table, or section structure is defined in this draft.

## First Example Program

The smallest valid program image is a single `HALT` instruction:

```text
0000
```

As bytes in memory:

```text
00 00
```

## Open Questions For Later Drafts

- Whether flags should exist at all in the base ISA
- Whether the architecture should keep fixed-width instructions beyond the first phase
- Whether jump targets should remain absolute or move to relative, register-based, or wider immediate forms
- Which register, if any, should later become a stack pointer by convention
- When memory load/store instructions should enter the base instruction set
