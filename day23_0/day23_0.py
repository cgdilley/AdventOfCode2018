import re
REGEX = re.compile(r"pos=<([\d\-]+),([\d\-]+),([\d\-]+)>, r=(\d+)")


def main():
    with open("../input/day23.txt", "r") as f:
        lines = [l.strip() for l in f.readlines()]

    nanos = parse_nanos(lines)

    strongest = get_strongest_nano(nanos)

    print("The strongest Nanobot is: %s" % str(strongest))

    in_range = get_nanos_in_range(nanos, strongest)

    print("There are %d Nanobots in range of the strongest Nanobot, including itself." % len(in_range))


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


def get_strongest_nano(nanos: iter) -> Nanobot:
    max_nano = None
    for nano in nanos:
        if max_nano is None or max_nano.r < nano.r:
            max_nano = nano
    return max_nano


def get_nanos_in_range(nanos: iter, center_bot: Nanobot) -> list:
    return list(filter(lambda nb: manhattan(nb.pos, center_bot.pos) <= center_bot.r, nanos))


def manhattan(coord1: tuple, coord2: tuple) -> int:
    return sum(abs(c[0] - c[1]) for c in zip(coord1, coord2))


#

main()
