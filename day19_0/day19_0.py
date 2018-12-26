import common.elfcode as elfcode
import re


def main():
    with open("../input/day19.txt", "r") as f:
        lines = f.readlines()
        ip_reg = lines[0]
        lines = lines[1:]

    ip_reg = int(re.match(r"#ip (\d+)", ip_reg).group(1))
    commands = load_commands(lines)

    registers = [0] * 6
    registers = execute_program(commands, registers, ip_reg)

    print("The state of the registers after execution: %s" % str(registers))


def load_commands(lines):
    return [elfcode.Command.parse(l) for l in lines]


def execute_program(commands, registers, ip_reg):

    # copy, just because
    registers = [r for r in registers]
    while True:
        pos = registers[ip_reg]
        before = [r for r in registers]
        if not (0 <= pos < len(commands)):
            break

        com = commands[pos]
        elfcode.run_command(registers, com)
        registers[ip_reg] += 1
        # print("Before: %s, POS: %d, Command: %s --- After: %s, POS: %d" % (
        #     str(before),
        #     pos,
        #     str(com),
        #     str(registers),
        #     registers[ip_reg]
        # ))

    return registers


main()
