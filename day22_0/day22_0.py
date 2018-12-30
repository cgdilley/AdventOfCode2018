import re
X = 0
Y = 1
ROCKY = 0
WET = 1
NARROW = 2


def main():
    with open("../input/day22.txt", "r") as f:
        lines = f.readlines()
        depth = int(re.match(r"depth: (\d+)", lines[0]).group(1))
        target = tuple([int(c) for c in re.match(r"target: (\d+),(\d+)", lines[1]).groups()])

    cave_map = build_cave_map(depth, target)

    print_cave_map(cave_map, target)

    risk = sum(c["terrain"] for c in cave_map.values())

    print("The risk level of this cave region is: %d" % risk)


def print_cave_map(cave_map, target):

    for y in range(target[Y] + 1):
        s = ""
        for x in range(target[X] + 1):
            if x == 0 and y == 0:
                s += "M"
            elif (x, y) == target:
                s += "T"
            else:
                s += {
                    ROCKY: ".",
                    WET: "=",
                    NARROW: "|"
                }[cave_map[(x, y)]["terrain"]]
        print(s)
    print()


def build_cave_map(depth, target):
    cave_map = dict()

    for y in range(target[Y] + 1):
        for x in range(target[X] + 1):

            if x == 0 and y == 0:
                geo_index = 0
            elif x == 0:
                geo_index = y * 48271
            elif y == 0:
                geo_index = x * 16807
            else:
                geo_index = cave_map[(x-1, y)]["erosion"] * cave_map[(x, y-1)]["erosion"]

            erosion = calc_erosion(geo_index, depth)
            cave_map[(x, y)] = {"erosion": erosion, "geo_index": geo_index, "terrain": terrain(erosion)}

    return cave_map


def calc_erosion(geo_index, depth):
    return (geo_index + depth) % 20183


def terrain(erosion):
    return erosion % 3


main()
