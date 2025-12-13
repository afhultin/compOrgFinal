

# opcodes / funct (MIPS-style)
R      = 0x00
ADDI   = 0x08
LW     = 0x23
SW     = 0x2B
BEQ    = 0x04

ADD_F  = 0x20
SUB_F  = 0x22

# register numbers we use in the sample programs
ZERO = 0
T0   = 8
T1   = 9
T2   = 10


def sext16(x: int) -> int:
    """Sign-extend a 16-bit integer to Python int."""
    x &= 0xFFFF
    return x - 0x10000 if (x & 0x8000) else x


class CPU:
    def __init__(self, mem_size: int = 4096):
        self.mem  = [0] * mem_size  # bytes
        self.regs = [0] * 32
        self.pc   = 0
        self.cyc  = 0

    # ---- memory helpers (big-endian words) ----
    def _check_addr(self, addr: int, nbytes: int = 1):
        if addr < 0 or addr + nbytes > len(self.mem):
            raise IndexError(f"memory address out of range: addr={addr} size={nbytes} (mem={len(self.mem)} bytes)")

    def load_word(self, addr: int) -> int:
        if addr % 4 != 0:
            raise ValueError(f"unaligned LW at address {addr}")
        self._check_addr(addr, 4)
        b0 = self.mem[addr] & 0xFF
        b1 = self.mem[addr+1] & 0xFF
        b2 = self.mem[addr+2] & 0xFF
        b3 = self.mem[addr+3] & 0xFF
        return ((b0 << 24) | (b1 << 16) | (b2 << 8) | b3) & 0xFFFFFFFF

    def store_word(self, addr: int, val: int):
        if addr % 4 != 0:
            raise ValueError(f"unaligned SW at address {addr}")
        self._check_addr(addr, 4)
        val &= 0xFFFFFFFF
        self.mem[addr]   = (val >> 24) & 0xFF
        self.mem[addr+1] = (val >> 16) & 0xFF
        self.mem[addr+2] = (val >> 8)  & 0xFF
        self.mem[addr+3] = val & 0xFF

    # ---- program loading ----
    def load_program(self, words, base: int = 0):
        """Load a list of 32-bit instruction words into memory starting at base (byte address)."""
        if base % 4 != 0:
            raise ValueError("program base must be word-aligned")
        for i, w in enumerate(words):
            self.store_word(base + 4*i, int(w) & 0xFFFFFFFF)
        self.pc = base

    # ---- execution ----
    def step(self, trace: bool = True):
        """Execute one instruction. Returns False on HALT."""
        self.cyc += 1
        pc0 = self.pc
        instr = self.load_word(self.pc)

        # HALT convention: 0 word
        if instr == 0:
            if trace:
                print(f"cycle {self.cyc}: HALT @ {pc0:08X}")
            return False

        # default next PC
        self.pc += 4

        op   = (instr >> 26) & 0x3F
        rs   = (instr >> 21) & 0x1F
        rt   = (instr >> 16) & 0x1F
        rd   = (instr >> 11) & 0x1F
        fn   = instr & 0x3F
        imm  = sext16(instr & 0xFFFF)

        name = "???"
        info = ""

        if op == R:
            if fn == ADD_F:
                old = self.regs[rd]
                self.regs[rd] = (self.regs[rs] + self.regs[rt]) & 0xFFFFFFFF
                name = "ADD"
                info = f"r{rd} {old:#010x}->{self.regs[rd]:#010x}"
            elif fn == SUB_F:
                old = self.regs[rd]
                self.regs[rd] = (self.regs[rs] - self.regs[rt]) & 0xFFFFFFFF
                name = "SUB"
                info = f"r{rd} {old:#010x}->{self.regs[rd]:#010x}"
            else:
                raise ValueError(f"bad funct: {fn:#x}")

        elif op == ADDI:
            old = self.regs[rt]
            self.regs[rt] = (self.regs[rs] + imm) & 0xFFFFFFFF
            name = "ADDI"
            info = f"r{rt} {old:#010x}->{self.regs[rt]:#010x} (imm={imm})"

        elif op == LW:
            addr = (self.regs[rs] + imm)
            val = self.load_word(addr)
            old = self.regs[rt]
            self.regs[rt] = val
            name = "LW"
            info = f"r{rt} {old:#010x}->{val:#010x} from [{addr}]"

        elif op == SW:
            addr = (self.regs[rs] + imm)
            val = self.regs[rt] & 0xFFFFFFFF
            self.store_word(addr, val)
            name = "SW"
            info = f"[{addr}] <- {val:#010x} (from r{rt})"

        elif op == BEQ:
            name = "BEQ"
            taken = (self.regs[rs] == self.regs[rt])
            if taken:
                self.pc = self.pc + imm * 4
            info = f"rs=r{rs} rt=r{rt} imm={imm} taken={taken} nextPC={self.pc:08X}"

        else:
            raise ValueError(f"bad opcode: {op:#x}")

        # enforce $zero
        self.regs[0] = 0

        if trace:
            print(
                f"cycle {self.cyc}: PC={pc0:08X} IR={instr:08X} {name:<4} | "
                f"t0={self.regs[T0]} t1={self.regs[T1]} t2={self.regs[T2]} | {info}"
            )
        return True

    def run(self, limit: int = 500, trace: bool = True):
        for _ in range(limit):
            if not self.step(trace=trace):
                break
