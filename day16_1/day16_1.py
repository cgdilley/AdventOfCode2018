import re
import copy

OP = 0
A = 1
B = 2
C = 3

REGISTERS = re.compile(r"\w+: +\[(\d+), (\d+), (\d+), (\d+)\]")

# noinspection SpellCheckingInspection
OPCODES = ["addr", "addi", "mulr", "muli", "banr", "bani", "borr", "bori", "setr", "seti", "gtir", "gtri",
           "gtrr", "eqir", "eqri", "eqrr"]


def main():
    with open("../input/day16.txt", "r") as f:
        all_lines = f.readlines()
        sample_lines = [l.strip() for l in all_lines[:3188]]
        code_lines = [l.strip() for l in all_lines[3190:]]

    samples = read_samples(sample_lines)

    guesses = guess_opcodes(samples)
    print(guesses)

    opcode_map = solve_opcodes(guesses)
    print(opcode_map)

    commands = read_commands(code_lines)
    registers = execute_commands(commands, opcode_map)

    print("Final register values: %s" % registers)
    pass


def read_samples(lines):
    samples = []
    for row in range(0, len(lines), 4):
        before_match = REGISTERS.match(lines[row])
        after_match = REGISTERS.match(lines[row + 2])
        samples.append({
            "before": [int(before_match.group(i + 1)) for i in range(4)],
            "after": [int(after_match.group(i + 1)) for i in range(4)],
            "command": [int(x) for x in lines[row + 1].split(" ")]
        })
    return samples


def read_commands(lines):
    return [[int(x) for x in line.split(" ")] for line in lines]


def execute_commands(commands, opcode_map):
    registers = [0, 0, 0, 0]
    for command in commands:
        run_command(registers, opcode_map[command[OP]], command)
    return registers


def test_each_sample(samples):
    results = []
    for sample in samples:
        suitable = test_opcodes(sample, OPCODES)
        results.append(suitable)
    return results


def test_opcodes(sample, opcodes):
    suitable = set()
    for op in opcodes:
        if is_suitable_op(op, sample):
            suitable.add(op)
    return suitable


def guess_opcodes(samples):
    guesses = {i: set(OPCODES) for i in range(len(OPCODES))}

    for sample in samples:
        suitable = test_opcodes(sample, guesses[sample["command"][0]])
        guesses[sample["command"][0]] = suitable

    return guesses


def solve_opcodes(guesses):
    node = build_solve_tree(guesses, dict(), None)
    while len(node["children"]) > 0:
        node = node["children"][0]
    return node["solved"]


def build_solve_tree(guesses, solved, parent):
    """
    Doing this as a tree turned out to be unnecessary because each iteration leaves at least one
    opcode number with only one possible opcode.  I still liked the idea anyway, thought it seemed
    cool.

    The IDEA was that you would start with te results from guess_opcodes(), which provides a map of all
    opcode numbers to all of the possible commands that fit all of the samples, and we start with all of
    the opcodes being unsolved (represented by an empty dictionary).

    We then first sort all of the opcode numbers by the number of possible commands they have.  We then
    create branches in the tree for each of that opcode number's possible commands, which represent
    what-if scenarios... all children of these nodes will assume the selected command is "solved", and
    the command is removed from the possibilities for all other opcode numbers. These
    children will then recursively create trees of their own with their new assumptions about the solved
    state.  These subtrees go through the same process of sorting the opcode possibilities and generating
    children subtrees.

    This recursive process repeats along each branch until one of the "base cases" are reached:
     - All 16 opcodes are considered solved.  This final child node is then returned as representing
       the solved state.
     - The possibility set for one of the opcodes is empty.  This means that the possibility tree up to
       this point is invalid.  None is returned.
     - After iterating through all possible children, if no children were valid, returns None.

    Any time None is returned by any of these recursive calls, that branch is entirely discarded and is
    not added to the tree.  This means in the end all invalid branches will be automatically pruned,
    and in the end the "tree" will actually just be one continuous branch that leads to the final
    solved state (unless there happens to be multiple solutions).

    :param guesses: A dictionary of guesses for the opcodes, mapping opcode numbers to a set of all
    possible commands for that opcode.
    :param solved: A dictionary that represents a particular "solved" state, mapping an opcode number to a
    command that is considered to be the "correct" pairing.
    :param parent: The node that will be the parent of the node generated by this function
    :return: The root node of the possibility tree for the given guesses and solved state
    """

    # Sort the guesses by their number of possibilities, ignoring those that have been solved
    # Note: With the current state of this code, an O(nlogn) sort is unnecessary when a O(n) min
    #       search would be fine, but it made sense before and I don't feel like changing it
    guesses_sorted = sorted([(k, v) for k, v in guesses.items() if k not in solved], key=lambda i: len(i[1]))

    # Build the node with the given solved state
    node = {
        "guesses": guesses_sorted,
        "solved": solved,
        "children": [],
        "parent": parent
    }

    # BASE CASE: If we've solved opcodes, return this node as the final solved state node
    if len(guesses_sorted) == 0:
        return node

    # Grab the first opcode number (with the lowest number of possibilities)
    num, codes = guesses_sorted[0]

    # If the possibility set is empty, this solved state is invalid.  Return None.
    if len(codes) == 0:
        return None

    # Iterate through all possibilities to create possibility trees for them
    for code in codes:
        # Copy the solved state and the guesses, removing the selected command
        # from the possibility sets for all opcode numbers
        new_solved = solved.copy()
        new_solved[num] = code

        new_guesses = copy.deepcopy(guesses)
        for guess_num, guess_codes in new_guesses.items():
            if code in guess_codes:
                guess_codes.remove(code)

        # RECURSION: Build the child node with this new solved state
        child = build_solve_tree(new_guesses, new_solved, node)

        # If the subtree was successfully built, add it as a child to this node
        if child is not None:
            node["children"].append(child)

    # If this node doesn't have any children, it is invalid.  Return None.
    if len(node["children"]) == 0:
        return None

    # Return the constructed node (along with all of its children)
    return node


def is_suitable_op(op, sample):
    return sample["after"][sample["command"][C]] == get_command_value(sample["before"], op, sample["command"])


def run_command(registers, op, com):
    registers[com[C]] = get_command_value(registers, op, com)


# noinspection SpellCheckingInspection
def get_command_value(registers, op, com):
    if op == "addr":
        return registers[com[A]] + registers[com[B]]
    elif op == "addi":
        return registers[com[A]] + com[B]
    elif op == "mulr":
        return registers[com[A]] * registers[com[B]]
    elif op == "muli":
        return registers[com[A]] * com[B]
    elif op == "banr":
        return registers[com[A]] & registers[com[B]]
    elif op == "bani":
        return registers[com[A]] & com[B]
    elif op == "borr":
        return registers[com[A]] | registers[com[B]]
    elif op == "bori":
        return registers[com[A]] | com[B]
    elif op == "setr":
        return registers[com[A]]
    elif op == "seti":
        return com[A]
    elif op == "gtir":
        return 1 if com[A] > registers[com[B]] else 0
    elif op == "gtri":
        return 1 if registers[com[A]] > com[B] else 0
    elif op == "gtrr":
        return 1 if registers[com[A]] > registers[com[B]] else 0
    elif op == "eqir":
        return 1 if com[A] == registers[com[B]] else 0
    elif op == "eqri":
        return 1 if registers[com[A]] == com[B] else 0
    elif op == "eqrr":
        return 1 if registers[com[A]] == registers[com[B]] else 0
    else:
        raise Exception("lolwut")


#

main()