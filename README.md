# Mini CPU Simulator & Assembler

MIPS-style CPU simulator and assembler in Python. Reads `.asm` files, assembles them into 32-bit machine code, and runs them on a simulated processor.

The assembler does two passes (first to resolve labels, then to encode instructions), and the CPU runs a basic fetch-decode-execute loop with 32 registers and 4KB of memory.

Supports: `ADD`, `SUB`, `ADDI`, `LW`, `SW`, `BEQ`

## Files

- `assembler.py` - two-pass assembler (labels + encoding)
- `cpu.py` - the CPU simulator (registers, memory, instruction decoding)
- `main.py` - ties it all together
- `programs/` - sample assembly programs
