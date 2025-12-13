Mini CPU Simulator — Design Report
Overview
For this project, I built a simplified CPU simulator based on a small subset of the MIPS architecture. I also wrote a basic assembler that reads .asm files and converts them into 32-bit machine code that the simulator can run.
CPU Design
The simulator uses 4 KB of byte-addressable memory stored in a Python list.
There are 32 registers, each 32 bits wide. Register $zero is always forced to stay at 0.
The program counter (PC) stores the address of the current instruction and normally increases by 4 each cycle.
Supported Instructions
The CPU supports only the instructions required by the handout:
R-Type: ADD, SUB
I-Type: ADDI, LW, SW, BEQ
Instructions are decoded and executed using a basic fetch-decode-execute cycle.
Branching
The BEQ instruction compares two registers and branches if they are equal. The branch offset is calculated relative to PC + 4 and is measured in words, similar to real MIPS behavior.
Assembler
The assembler uses two passes:
The first pass records label addresses.
The second pass converts each instruction into a 32-bit machine code value.
A 0x00000000 instruction is added at the end of the program and is treated as a halt.
Testing
The two sample programs from the handout were tested:
Program 1 stores 11 at memory address 0.
Program 2 stores 15 at memory address 0.
Execution traces and hex output files are included in the repository.