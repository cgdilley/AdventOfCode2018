import common.elfcode as elfcode
import re


def main():
    # with open("../input/day19.txt", "r") as f:
    #     lines = f.readlines()
    #     ip_reg = lines[0]
    #     lines = lines[1:]
    #
    # ip_reg = int(re.match(r"#ip (\d+)", ip_reg).group(1))
    # commands = load_commands(lines)
    #
    # registers = [1, 0, 0, 0, 0, 0]
    # registers = execute_program(commands, registers, ip_reg)
    #
    # print("The state of the registers after execution: %s" % str(registers))

    # Hey, I actually did it this year!  The stupid "read the fake program" problem.
    #
    # So, I pieced together the program line by line.  It appeared that the only
    # difference between part one and part two is that the latter lines in the program
    # are executing, causing the value in register 1 to grow super huge and make the
    # program infeasible to run.
    #
    # Then I tried working backwards from the escape condition in part one, which apparently
    # was when hitting the command 'mulr 3 3 3' (line 18 in the input).  This line apparently
    # is only reached when the value of register 5 is greater than the value in register 1.
    # It seems the only thing that modifies register 5 is the line 'addi 5 1 5', which increments it.
    # This line is only reached if the line a few lines up, 'gtrr 4 1 2' puts a value 1 in register 2,
    # meaning that 5 is incremented whenever the value in 4 is greater than the value in register 1...
    # and similarly the value in register 4 is only incremented.  Then after the value of reg 5 is
    # incremented, register 4 is reset to 1 and starts counting up again.
    #
    # This means that the main loop of the program will execute a number of times equal to register 1
    # squared... it is essentially:
    # for reg5 in range(1, reg1_value+1):
    #  for reg4 in range(1, reg1_value+1):
    #    ....
    # And since register 1 ends up as 10551300, that is infeasible to execute.
    #
    # Buuuut we can see what is modifying register 0.  The line that modifies register 0 is 'addr 5 0 0',
    # adding the value of register 5 to register 0.  This line is only reached, apparently, if the
    # values in register 5 and register 4 multiplied together equal the value in register 1, because of the
    # following lines:
    # mulr 5 4 2
    # eqrr 2 1 2
    # addr 2 3 3
    #
    # So my intuition became that it must be summing together the divisors of the number in register one.
    # Tested this with part one's register 1 number (900), and this checked out.  So I tried part two's
    # value for register 1 (10551300), and it turned out the answer was correct.
    #
    # Thank.  Fucking.  God.
    #
    # So the pseudocode must be something like
    #
    # reg1 := 10551300
    # reg0 := 0
    # for reg5=1; reg5 <= reg1; reg5++:
    #  for reg4=1; reg4 <= reg1; reg4++:
    #   if (reg5 * reg4) == reg1:
    #     reg0 += reg5
    #
    # ... more or less
    #
    s = sum(find_divisors(10551300))
    print(s)


def load_commands(lines):
    return [elfcode.Command.parse(l) for l in lines]


def find_divisors(num):
    d = []
    for i in range(1, num + 1):
        if num % i == 0:
            d.append(i)
    return d


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
        if before[4] != registers[4]:
            registers[4] = registers[1] + 1
        if before[0] != registers[0]:
            print("CHANGED: %s --> %s" % (str(before), str(registers)))
        if before[5] != registers[5]:
            registers[5] = registers[1] + 1


    return registers


main()
