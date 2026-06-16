# Roadmap

This roadmap describes the intended build order for the project. It is a sequencing document, not a long-term promise of exact feature scope.

## Phase 1: Initial Architecture Definition

The first phase establishes the minimum architectural contract required to support machine execution:

Current status:

- Baseline complete
- Define the first ISA draft.
- Define the CPU state model.
- Define the memory model.
- Define the instruction encoding format.
- Define invalid instruction behavior.
- Define the first minimal program image assumptions.

Deliverables:

- `docs/isa.md`
- initial decision records in `docs/decisions/`
- a minimal executable example centered on `HALT`

## Phase 2: Minimal Emulator

The second phase implements a small emulator that executes the initial ISA draft:

Current status:

- Baseline complete
- Model registers, program counter, and halted state.
- Load a program image into memory.
- Step one instruction at a time.
- Detect invalid instructions and out-of-bounds memory access.
- Add optional execution tracing.

Deliverables:

- CPU state implementation
- instruction decoder
- step/execute loop
- emulator tests for the first instruction set

## Phase 3: Minimal Assembler

The third phase introduces assembly source and translation to machine code:

Current status:

- Baseline complete
- Define assembly syntax for the first instructions.
- Support labels and numeric literals.
- Encode instructions according to `docs/isa.md`.
- Add diagnostics for invalid source.

Deliverables:

- assembler parser
- encoder
- assembly fixtures and encoding tests

## Phase 4: Language And Compiler Seed

The fourth phase introduces a very small source language and a direct compilation path:

Current status:

- Not started
- integer literals
- variables
- arithmetic
- conditional control flow
- loops

Deliverables:

- language syntax draft
- parser and semantic checks
- first compiler path to the custom ISA

## Phase 5: Runtime And Kernel Foundations

The fifth phase introduces the first system-level abstractions above machine execution:

Current status:

- Not started
- program startup model
- trap and syscall mechanism
- simple program loading
- early memory services
- basic IO

Deliverables:

- runtime entry conventions
- syscall ABI draft
- first kernel responsibilities

## Phase 6: Userland And Storage

The sixth phase expands the system into a usable software environment:

Current status:

- Not started
- filesystem structures
- shell commands
- utility programs
- loader improvements

Deliverables:

- initial filesystem format
- shell prototype
- user programs that exercise the stack

## Phase 7: Extended Experiments

Later phases may include:

Current status:

- Not started
- richer compiler features
- debugger support
- object format improvements
- process model experiments
- graphical experiments

These areas should remain downstream of a stable source-to-machine execution path.
