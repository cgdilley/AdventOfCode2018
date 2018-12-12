import re
RULE = re.compile(r"([.#]{5}) => ([.#])")


def main():
    with open("../input/day12.txt", "r") as f:
        contents = f.readlines()

    initial_state = re.match(r".*: (.*)", contents[0].strip()).group(1)
    initial_state = {i: initial_state[i] for i in range(len(initial_state))}

    rules = process_rules(contents[2:])

    final_state = simulate(initial_state, rules, 20)

    result = sum(0 if v == "." else k for k, v in final_state.items())

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

    for gen in range(generations):
        print_state(working_state)
        next_state = dict()

        pot_index = 0
        pots = list(working_state.keys())
        while pot_index < len(pots):
            pot = pots[pot_index]
            pot_index += 1

            rep_string = ""
            for i in range(pot - 2, pot + 3):
                if i not in working_state:
                    if working_state[pot] == "#":
                        working_state[i] = "."
                        pots.append(i)
                    rep_string += "."
                else:
                    rep_string += working_state[i]

            next_state[pot] = rules[rep_string] if rep_string in rules else "."
        working_state = next_state

    return working_state


def print_state(state):
    s = ""
    for i in sorted(state.keys()):
        s += state[i]
    print(s)











main()
