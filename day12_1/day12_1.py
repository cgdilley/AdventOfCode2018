import re
RULE = re.compile(r"([.#]{5}) => ([.#])")


def main():
    # with open("../input/day12.txt", "r") as f:
    #     contents = f.readlines()
    #
    # initial_state = re.match(r".*: (.*)", contents[0].strip()).group(1)
    #
    # rules = process_rules(contents[2:])
    #
    # final_state, pot_shift = simulate(initial_state, rules, 50000000)

    # It became clear in seeing the sims that this state was stable, and shifting to the right
    # by one each generation, and that pot_shift was equal to generation - 34
    final_state = "###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###..###..###"
    pot_shift = (50 * 10**9) - 34

    result = 0
    for c in range(len(final_state)):
        if final_state[c] == "#":
            result += c + pot_shift

    print_state(final_state)
    print("The result is: %d" % result)


def process_rules(lines):
    rules = dict()
    for line in lines:
        match = RULE.match(line)
        if match:
            rules[match.group(1)] = match.group(2)
    return rules


def simulate(initial_state, rules, generations):
    working_state = initial_state

    gen = 0
    pot_shift = 0
    while gen < generations:

        gen += 1

        next_state = ""

        pot_index = 2
        working_state = "...." + working_state + "...."
        pot_shift -= 2
        rep_string = "....."
        while pot_index < len(working_state)-2:

            rep_string = rep_string[1:] + working_state[pot_index + 2]

            next_state += rules[rep_string] if rep_string in rules else "."
            pot_index += 1

        left_start = next_state.find("#")
        pot_shift += left_start
        working_state = next_state[left_start:next_state.rfind("#") + 1]
        if gen % 100000 == 0:
            print("Finished gen %d: %s (shifted %d)" % (gen, working_state, pot_shift))


    return working_state, pot_shift


def print_state(state):
    print(state)











main()
