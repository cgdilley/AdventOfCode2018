import re
REGEX = re.compile(r"pos=<([\d\-]+),([\d\-]+),([\d\-]+)>, r=(\d+)")


def main():
    with open("../input/day23.txt", "r") as f:
        lines = [l.strip() for l in f.readlines()]

    nanos = parse_nanos(lines)

    # overlaps = count_overlaps(nanos)
    # most = get_most_overlaps(overlaps)
    #
    # print(most)


def parse_nanos(lines: list) -> list:
    return [Nanobot.parse(line) for line in lines]


class Nanobot:
    def __init__(self, x, y, z, r):
        self.pos = (x, y, z)
        self.r = r

    def __str__(self):
        return "%s -- %d" % (str(self.pos), self.r)

    def __repr__(self):
        return str(self)

    @staticmethod
    def parse(line):
        m = REGEX.match(line)
        return Nanobot(int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)))


# def count_overlaps(nanos: list) -> dict:
#     overlaps = {nb.pos: [] for nb in nanos}
#
#     for i in range(len(nanos) - 1):
#         curr = nanos[i]
#
#         for compare in nanos[i+1:]:
#             if nanos_overlap(curr, compare):
#                 overlaps[curr.pos].append(compare)
#                 overlaps[compare.pos].append(curr)
#
#     return overlaps
#
#
# def find_best_square(overlaps: dict, best: list) -> tuple:
#     pass


def get_nanos_in_range(nanos: iter, center_bot: Nanobot) -> list:
    return list(filter(lambda nb: manhattan(nb.pos, center_bot.pos) <= center_bot.r, nanos))

#
# def nanos_overlap(nano1: Nanobot, nano2: Nanobot) -> bool:
#     return manhattan(nano1.pos, nano2.pos) <= nano1.r + nano2.r


def get_most_overlaps(overlaps: dict) -> list:
    max_coords = []
    max_overlaps = None
    for coord, overlaps in overlaps.items():
        count = len(overlaps)
        if max_overlaps is None or count > max_overlaps:
            max_coords = [coord]
            max_overlaps = count
        elif count == max_overlaps:
            max_coords.append(coord)

    return max_coords


def manhattan(coord1: tuple, coord2: tuple) -> int:
    return sum(abs(c[0] - c[1]) for c in zip(coord1, coord2))


#

main()
