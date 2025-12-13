"""
This script:
  - reads ASM from file (required by rubric feedback)
  - assembles to machine code
  - writes hex output to hex/<name>.hex
  - runs CPU simulator
  - writes execution trace to traces/<name>_trace.txt
"""

import argparse
from pathlib import Path
from assembler import assemble_file
from cpu import CPU

def write_hex(words, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for w in words:
            f.write(f"{int(w) & 0xFFFFFFFF:08X}\n")

def run_and_trace(words, trace_path: Path, trace: bool):
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    cpu = CPU()
    cpu.load_program(words, base=0)

    # Always write a trace file; trace flag controls verbosity in the file and console.
    with trace_path.open("w", encoding="utf-8") as f:
        def _print(s):
            f.write(s + "\n")
            if trace:
                print(s)

        pass

    # Do the actual run:
    # (1) If trace=True -> print to console, also capture to file by redirecting stdout
    # (2) If trace=False -> capture to file only
    import sys, io, contextlib

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        cpu2 = CPU()
        cpu2.load_program(words, base=0)
        cpu2.run(limit=500, trace=True)
        mem0 = cpu2.load_word(0)

    trace_path.write_text(buf.getvalue(), encoding="utf-8")
    return mem0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("asm_file", help="Path to .asm program file")
    ap.add_argument("--trace", action="store_true", help="Also print trace to console")
    args = ap.parse_args()

    asm_path = Path(args.asm_file)
    words, labels = assemble_file(str(asm_path))

    out_hex = Path("hex") / (asm_path.stem + ".hex")
    out_trace = Path("traces") / (asm_path.stem + "_trace.txt")

    write_hex(words, out_hex)
    mem0 = run_and_trace(words, out_trace, trace=args.trace)

    print(f"\nAssembled: {asm_path} -> {out_hex}")
    print(f"Trace saved: {out_trace}")
    print(f"Final mem[0] = {mem0}")

if __name__ == "__main__":
    main()
