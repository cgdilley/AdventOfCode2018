import re

REGEX = re.compile(r"^([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)$")

OPCODES = ["addr", "addi", "mulr", "muli", "banr", "bani", "borr", "bori", "setr", "seti", "gtir", "gtri",
           "gtrr", "eqir", "eqri", "eqrr"]


def run_command(registers, com):
    registers[com.c] = get_command_value(registers, com)


# noinspection SpellCheckingInspection
def get_command_value(registers, com):
    if com.op == "addr":
        return registers[com.a] + registers[com.b]
    elif com.op == "addi":
        return registers[com.a] + com.b
    elif com.op == "mulr":
        return registers[com.a] * registers[com.b]
    elif com.op == "muli":
        return registers[com.a] * com.b
    elif com.op == "banr":
        return registers[com.a] & registers[com.b]
    elif com.op == "bani":
        return registers[com.a] & com.b
    elif com.op == "borr":
        return registers[com.a] | registers[com.b]
    elif com.op == "bori":
        return registers[com.a] | com.b
    elif com.op == "setr":
        return registers[com.a]
    elif com.op == "seti":
        return com.a
    elif com.op == "gtir":
        return 1 if com.a > registers[com.b] else 0
    elif com.op == "gtri":
        return 1 if registers[com.a] > com.b else 0
    elif com.op == "gtrr":
        return 1 if registers[com.a] > registers[com.b] else 0
    elif com.op == "eqir":
        return 1 if com.a == registers[com.b] else 0
    elif com.op == "eqri":
        return 1 if registers[com.a] == com.b else 0
    elif com.op == "eqrr":
        return 1 if registers[com.a] == registers[com.b] else 0
    else:
        raise Exception("lolwut")


class Command:
    def __init__(self, op, a, b, c):
        self.op = op
        self.a = a
        self.b = b
        self.c = c

    def __str__(self):
        return "%s %d %d %d" % (self.op, self.a, self.b, self.c)

    def __repr__(self):
        return str(self)

    @staticmethod
    def parse(s: str):
        m = REGEX.match(s)
        return Command(m.group(1),
                       int(m.group(2)),
                       int(m.group(3)),
                       int(m.group(4)))
