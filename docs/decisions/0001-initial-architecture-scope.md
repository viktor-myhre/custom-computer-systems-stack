# 0001 Initial Architecture Scope

Status: accepted

## Context

The project needs a narrow first milestone that produces a complete path from specification to execution without prematurely designing the full operating system and language stack.

Without an explicit scope boundary, the early architecture work could spread into unrelated concerns such as multitasking, complex linking, or advanced runtime behavior before the foundational machine model is stable.

## Decision

The initial architecture milestone is limited to the smallest useful execution core:

- a first ISA draft
- a CPU state model
- a minimal memory model
- a fixed instruction encoding format
- a program counter and halted state
- a minimal emulator
- a minimal assembler

The first milestone does not include:

- multitasking
- virtual memory
- dynamic linking
- a large standard library
- a stable syscall ABI
- a GUI system

## Consequences

The first phase can focus on a short chain from specification to execution.

The emulator and assembler can be implemented against a small, explicit contract.

Later layers such as the compiler, runtime, kernel, filesystem, and shell will build on a clearer foundation.

Some redesign is expected once the first execution path exists, but the redesign surface should remain concentrated in the ISA and emulator layers rather than scattered across the full stack.
