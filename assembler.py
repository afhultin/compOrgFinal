"""

Supported instructions:
  R-type:  ADD rd, rs, rt
           SUB rd, rs, rt
  I-type:  ADDI rt, rs, imm
           LW   rt, offset(rs)
           SW   rt, offset(rs)
           BEQ  rs, rt, label

Labels:
  LABEL:   (can be on its own line, or before an instruction on same line)

Comments:
  Anything after '#' is ignored.
"""

import re

# opcodes / funct
R      = 0x00
ADDI   = 0x08
LW     = 0x23
SW     = 0x2B
BEQ    = 0x04

ADD_F  = 0x20
SUB_F  = 0x22

REG_MAP = {
    "$0": 0, "$zero": 0,
    "$t0": 8, "$t1": 9, "$t2": 10,
    # Add more if you want (safe extras):
    "$t3": 11, "$t4": 12, "$t5": 13, "$t6": 14, "$t7": 15,
    "$s0": 16, "$s1": 17, "$s2": 18, "$s3": 19, "$s4": 20, "$s5": 21, "$s6": 22, "$s7": 23,
}

def enc_r(funct, rs, rt, rd, sh=0):
    return ((R & 0x3F) << 26) | ((rs & 0x1F) << 21) | ((rt & 0x1F) << 16) | ((rd & 0x1F) << 11) | ((sh & 0x1F) << 6) | (funct & 0x3F)

def enc_i(op, rs, rt, imm):
    imm &= 0xFFFF
    return ((op & 0x3F) << 26) | ((rs & 0x1F) << 21) | ((rt & 0x1F) << 16) | imm

def _clean(line: str) -> str:
    line = line.split("#", 1)[0]
    return line.strip()

def _split_tokens(line: str):
    # Replace commas with spaces, keep parens for lw/sw parsing
    line = line.replace(",", " ")
    return [t for t in line.split() if t]

def parse_reg(tok: str) -> int:
    tok = tok.strip()
    if tok not in REG_MAP:
        raise ValueError(f"unknown register '{tok}' (supported: {', '.join(sorted(REG_MAP.keys()))})")
    return REG_MAP[tok]

_mem_re = re.compile(r"^(?P<off>[-+]?\d+)\((?P<base>\$\w+|\$0)\)$")

def parse_mem(tok: str):
    m = _mem_re.match(tok.replace(" ", ""))
    if not m:
        raise ValueError(f"bad memory operand '{tok}' (expected offset(base) like 0($zero))")
    off = int(m.group("off"), 10)
    base = parse_reg(m.group("base"))
    return off, base

def assemble_lines(lines):
    """
    Two-pass:
      pass1: record label -> address
      pass2: encode instructions, resolve BEQ label offsets
    Returns (words, labels)
    """
    # Pass 1
    labels = {}
    instr_lines = []
    pc = 0
    for raw in lines:
        line = _clean(raw)
        if not line:
            continue

        # handle label at start
        while True:
            if ":" in line:
                before, after = line.split(":", 1)
                lab = before.strip()
                if not lab or not re.match(r"^[A-Za-z_]\w*$", lab):
                    raise ValueError(f"bad label name '{lab}'")
                if lab in labels:
                    raise ValueError(f"duplicate label '{lab}'")
                labels[lab] = pc
                line = after.strip()
                if not line:
                    break
                # if there's another label on same line, loop again
                continue
            break

        if not line:
            continue

        instr_lines.append((pc, line))
        pc += 4

    # Pass 2
    words = []
    for pc0, line in instr_lines:
        toks = _split_tokens(line)
        if not toks:
            continue
        op = toks[0].upper()

        if op == "ADD":
            # ADD rd, rs, rt
            if len(toks) != 4:
                raise ValueError(f"ADD expects 3 operands: {line}")
            rd = parse_reg(toks[1]); rs = parse_reg(toks[2]); rt = parse_reg(toks[3])
            words.append(enc_r(ADD_F, rs, rt, rd))

        elif op == "SUB":
            if len(toks) != 4:
                raise ValueError(f"SUB expects 3 operands: {line}")
            rd = parse_reg(toks[1]); rs = parse_reg(toks[2]); rt = parse_reg(toks[3])
            words.append(enc_r(SUB_F, rs, rt, rd))

        elif op == "ADDI":
            # ADDI rt, rs, imm
            if len(toks) != 4:
                raise ValueError(f"ADDI expects 3 operands: {line}")
            rt = parse_reg(toks[1]); rs = parse_reg(toks[2]); imm = int(toks[3], 0)
            words.append(enc_i(ADDI, rs, rt, imm))

        elif op == "LW":
            # LW rt, offset(rs)
            if len(toks) != 3:
                raise ValueError(f"LW expects 2 operands: {line}")
            rt = parse_reg(toks[1])
            off, rs = parse_mem(toks[2])
            words.append(enc_i(LW, rs, rt, off))

        elif op == "SW":
            if len(toks) != 3:
                raise ValueError(f"SW expects 2 operands: {line}")
            rt = parse_reg(toks[1])
            off, rs = parse_mem(toks[2])
            words.append(enc_i(SW, rs, rt, off))

        elif op == "BEQ":
            # BEQ rs, rt, label
            if len(toks) != 4:
                raise ValueError(f"BEQ expects 3 operands: {line}")
            rs = parse_reg(toks[1]); rt = parse_reg(toks[2]); target = toks[3]
            if target not in labels:
                raise ValueError(f"unknown label '{target}' in line: {line}")
            target_addr = labels[target]
            # MIPS-style: branch offset is relative to (PC+4), in words
            offset_words = (target_addr - (pc0 + 4)) // 4
            words.append(enc_i(BEQ, rs, rt, offset_words))

        else:
            raise ValueError(f"unknown instruction '{op}' in line: {line}")

    # Append HALT
    words.append(0)
    return words, labels

def assemble_file(path: str):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return assemble_lines(lines)
