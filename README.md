# Custom Computer Systems Stack

A first-principles implementation of a minimal computer systems stack, built layer by layer from a custom ISA to higher-level system software.

The purpose of this project is to understand the complete path from source code to machine execution, and then continue upward into runtime, kernel, userland, filesystem, shell, and graphical experiments.

## Project Scope

This repository is intended to grow into a complete, inspectable stack:

1. A custom instruction set architecture.
2. A CPU emulator for the custom machine code.
3. An assembler and binary format.
4. A small programming language.
5. A compiler targeting the custom ISA.
6. A runtime and kernel layer.
7. User programs, a filesystem, shell, and later GUI experiments.

The project prioritizes education, architecture, correctness, clarity, deterministic behavior, and traceable design decisions over performance or feature completeness.

## Current Status

The project is in its initial planning and scaffolding phase.

The first implementation milestone is expected to focus on:

- Defining a minimal ISA.
- Documenting instruction encoding and memory behavior.
- Building a small CPU emulator.
- Adding executable examples and tests for the first instructions.

## Design Principles

- Keep each layer small and understandable.
- Treat specifications as the source of truth for implementation behavior.
- Prefer explicit binary formats, memory layouts, and calling conventions.
- Make programs easy to inspect at every stage: source, assembly, machine code, and execution trace.
- Keep examples readable and update them when the architecture changes.
- Avoid premature optimization until the core system is correct and testable.

## Planned Repository Structure

```text
docs/
  decisions/
  isa.md
  memory.md
  binary-format.md
  calling-convention.md
  roadmap.md

examples/
  asm/
  lang/
  programs/

src/
  isa/
  emulator/
  assembler/
  language/
  compiler/
  runtime/
  kernel/
  tools/

tests/
  isa/
  emulator/
  assembler/
  compiler/
  integration/
```

This structure may evolve as the implementation language and build system are chosen, but the conceptual layer boundaries should remain clear.

## Documentation

Documentation is treated as part of the system design.

Important design choices should be recorded in `docs/decisions/` as short decision records. Specifications such as the ISA, binary format, memory model, and calling convention should be kept close to the code they govern.

All repository documentation should be written in English.

## Early Roadmap

1. Define the first ISA draft.
2. Specify registers, memory model, instruction encoding, and halt behavior.
3. Implement a CPU emulator with deterministic stepping.
4. Add assembly examples for arithmetic, branching, and memory access.
5. Build a minimal assembler.
6. Add integration tests that assemble and execute complete programs.
7. Design the first tiny language and compiler path.

## Non-Goals

The early phases are not trying to provide:

- A production operating system.
- POSIX compatibility.
- Sophisticated optimization.
- A large standard library.
- A stable ABI before the fundamentals are understood.
- A complete GUI system before the lower layers exist.

Those areas can be explored later once the core source-to-machine execution chain is reliable.

## License

This project is licensed under the Apache License 2.0.
