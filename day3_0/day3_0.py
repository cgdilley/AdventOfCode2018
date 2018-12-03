import re

with open("../input/day3.txt", "r") as f:
    lines = [l.strip() for l in f.readlines()]

REGEX = re.compile(r'^#(\d+) @ (\d+),(\d+): (\d+)x(\d+)$')


def build_rect(s):
    match = REGEX.match(s)

    return {
        "id": int(match.group(1)),
        "left": int(match.group(2)),
        "top": int(match.group(3)),
        "width": int(match.group(4)),
        "height": int(match.group(5))
    }


def aggregate(input_list):

    master = {}
    for line in input_list:
        rect = build_rect(line)

        for x in range(rect["left"], rect["left"] + rect["width"]):
            for y in range(rect["top"], rect["top"] + rect["height"]):
                if (x, y) in master:
                    master[(x, y)].append(rect["id"])
                else:
                    master[(x, y)] = [rect["id"]]

    return master


def count_overlaps(aggregation):
    count = 0
    for info in aggregation.values():
        if len(info) >= 2:
            count += 1
    return count


print(count_overlaps(aggregate(lines)))



