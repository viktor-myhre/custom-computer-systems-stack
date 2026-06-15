# 0002 Initial ISA Shape

Status: accepted

## Context

The first ISA draft needs to be simple enough to support a small emulator and assembler, while still being expressive enough to execute short programs and demonstrate instruction decoding, register state updates, arithmetic, and control flow.

An excessively small ISA would delay useful programs. An overly ambitious ISA would add complexity before the toolchain is ready to support it.

## Decision

The initial ISA shape uses:

- a byte-addressed memory model
- a small general-purpose register file
- a dedicated program counter
- fixed-width instructions
- explicit opcodes and operand fields
- a halted execution state
- absolute control transfer expressed as instruction-index targets in the first jump form

The first instruction set should include:

- `HALT`
- `NOP`
- register move
- integer add
- unconditional jump

Conditional branches, memory load/store, flags, stack behavior, and trap handling may be introduced after the first execution path is working.

## Consequences

The first decoder and emulator loop can remain compact and deterministic.

The assembler can target a stable, easy-to-explain binary layout.

The first jump encoding can stay small without mixing byte-address semantics and instruction-address semantics in assembly source.

The first example programs can demonstrate:

- program termination
- register state changes
- arithmetic
- control flow

The first ISA draft intentionally delays richer features such as stack frames, subroutine calls, and syscalls until the base execution model is validated.
