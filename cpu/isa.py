class Instruction:
    def __init__(self, opcode, rd=None, rs1=None, rs2=None, imm=None):
        self.opcode = opcode  # e.g., 'ADD', 'LD', 'BEQ', 'INT'
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2
        self.imm = imm
        self.result = 0