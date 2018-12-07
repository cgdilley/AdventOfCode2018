import re

REGEX = re.compile(r"Step (.) .* step (.)")
SECONDS = {val: index + 61 for index, val in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")}


def main():
    with open("../input/day7.txt", "r") as f:
        lines = [read_instruction(line) for line in f.readlines()]

    lines = merge_instructions(lines)

    ordered = execute_build(lines, 5)

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


def execute_build(instructions, worker_count):
    workers = [[] for _ in range(worker_count)]
    time = 0
    available = set(instructions.keys())
    completed = []

    while len(completed) < len(instructions):

        while True:
            top_choice = get_next_choice(instructions, available, completed)
            if top_choice is None:
                break

            queued = queue_instruction(workers, top_choice["self"], time)
            if queued:
                available.remove(top_choice["self"])
            else:
                break

        time += 1
        for worker in workers:
            if len(worker) == time and worker[-1] != "-":
                completed.append(worker[-1])

    duration = max([len(worker) for worker in workers])
    print("Total duration = %d" % duration)
    # for i in range(duration):
    #     s = ""
    #     for worker in workers:
    #         s += "-" if len(worker) <= i else worker[i]
    #     print(s)

    return completed


def queue_instruction(workers, next_instruction, time):
    for worker in workers:
        if len(worker) <= time:
            worker += ['-'] * (time - len(worker))
            worker += [next_instruction] * SECONDS[next_instruction]
            return True
    return False


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
