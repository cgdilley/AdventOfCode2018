import re

REGEX = re.compile(r"Step (.) .* step (.)")


def main():
    with open("../input/day7.txt", "r") as f:
        lines = [read_instruction(line) for line in f.readlines()]

    lines = merge_instructions(lines)

    ordered = order_instructions(lines)

    print("Result: %s" % "".join([n for n in ordered]))


def read_instruction(s):
    match = REGEX.match(s)
    return {
        "self": match.group(2),
        "parent": match.group(1),
        "children": []
    }


def merge_instructions(instructions):
    instruction_map = dict()

    for inst in instructions:
        if inst["self"] not in instruction_map:
            instruction_map[inst["self"]] = {
                "parents": [inst["parent"]], "self": inst["self"], "children": []
            }
        else:
            instruction_map[inst["self"]]["parents"].append(inst["parent"])

        if inst["parent"] not in instruction_map:
            instruction_map[inst["parent"]] = {
                "parents": [], "self": inst["parent"], "children": [inst["self"]]
            }
        else:
            instruction_map[inst["parent"]]["children"].append(inst["self"])

    return instruction_map


def order_instructions(instructions):
    ordered = []
    remaining_instructions = set(instructions.keys())

    while len(ordered) < len(instructions):
        top_choice = get_next_choice(instructions, remaining_instructions, set(ordered))
        ordered.append(top_choice["self"])
        remaining_instructions.remove(top_choice["self"])

    return ordered


def get_next_choice(instructions, remaining, seen):
    top_choice = None
    for r in remaining:
        inst = instructions[r]
        available = True
        for parent in inst["parents"]:
            if parent not in seen:
                available = False
                break
        if available and (top_choice is None or inst["self"] < top_choice["self"]):
            top_choice = inst
    return top_choice


main()
