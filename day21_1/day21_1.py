import common.elfcode as elfcode


def main():
    with open("../input/day21.txt", "r") as f:
        lines = [l.strip() for l in f.readlines()]

    ip_reg = elfcode.parse_instruction_register(lines[0])

    commands = [elfcode.Command.parse(l) for l in lines[1:]]

    registers = [0] * 6
    registers[0] = 0
    registers, history = execute_program(commands, registers, ip_reg)

    print("Program halted after %d iterations when the value of %d was placed in register 0." %
          (len(history), registers[0]))


def execute_program(commands, registers, ip_reg):

    history = []

    # copy, just because
    registers = [r for r in registers]
    while True:
        pos = registers[ip_reg]
        if not (0 <= pos < len(commands)):
            break

        com = commands[pos]

        hist_obj = {
            "com": com,
            "pos": pos,
            "before": [r for r in registers]
        }

        elfcode.run_command(registers, com)
        registers[ip_reg] += 1

        hist_obj["after"] = [r for r in registers]
        history.append(hist_obj)

        if hist_obj["pos"] == 3:
            print("%s" % hist_obj)

    return registers, history

#


main()
