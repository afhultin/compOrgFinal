# Mini CPU Simulator & Assembler

A simplified MIPS CPU simulator and two-pass assembler written in Python. Converts MIPS assembly into 32-bit machine code and executes it on a simulated processor with full execution tracing.

## Features

- **Two-pass assembler** — resolves labels, encodes R-type and I-type instructions into 32-bit machine words
- **CPU simulator** — 32 registers, 4KB byte-addressable memory (big-endian), fetch-decode-execute cycle
- **Supported instructions:** `ADD`, `SUB`, `ADDI`, `LW`, `SW`, `BEQ`
- **Execution tracing** — logs every cycle with PC, instruction register, register state, and operation details
- **Hex output** — writes assembled machine code to hex files for inspection

## Usage

```bash
# Assemble and run a program with trace output
python main.py programs/program1.asm --trace

# Run without console trace (still saves to traces/)
python main.py programs/program2.asm
```

Output files are saved to `hex/` (machine code) and `traces/` (execution logs).

## Architecture

| Component | File | Description |
|-----------|------|-------------|
| Assembler | `assembler.py` | Two-pass assembler — pass 1 records labels, pass 2 encodes instructions |
| CPU | `cpu.py` | Simulated processor with registers, memory, and instruction decoder |
| Runner | `main.py` | CLI entry point — assembles, runs, and saves output |

## Example

Given an assembly program that computes a sum:
```asm
ADDI $t0, $zero, 5
ADDI $t1, $zero, 6
ADD  $t2, $t0, $t1
SW   $t2, 0($zero)
```

The simulator produces a cycle-by-cycle trace showing register changes and memory operations, with the final result stored at `mem[0]`.

Built as a Computer Organization final project.
