import re

COORD = re.compile(r'(\d+), (\d+)')


def main():
    with open("../input/day6.txt") as f:
        lines = [read_coord(l) for l in f.readlines()]

    limits = find_limits(lines)
    dists = calc_distances(lines, limits)
    count = count_dists_within_range(dists, 10000)

    print("The number of coords with summed distances less than 10000 is: %d" % count)

def calc_distances(coords, limits):
    dists = dict()
    for x in range(limits["left"], limits["right"] + 1):
        for y in range(limits["top"], limits["bottom"] + 1):
            dist_sum = 0
            for coord in coords:
                dist = abs(coord[0] - x) + abs(coord[1] - y)
                dist_sum += dist
            dists[(x, y)] = dist_sum
    return dists


def count_dists_within_range(distances, max_dist):
    count = 0
    for distance in distances.values():
        if distance < max_dist:
            count += 1
    return count


def read_coord(s):
    match = COORD.match(s)
    return int(match.group(1)), int(match.group(2))


def find_limits(coords):
    limits = dict()
    for coord in coords:
        if "left" not in limits or coord[0] < limits["left"]:
            limits["left"] = coord[0]
        if "right" not in limits or coord[0] > limits["right"]:
            limits["right"] = coord[0]
        if "top" not in limits or coord[1] < limits["top"]:
            limits["top"] = coord[1]
        if "bottom" not in limits or coord[1] > limits["bottom"]:
            limits["bottom"] = coord[1]

    return limits


def is_within_limits(coord, limits):
    return limits["left"] <= coord[0] <= limits["right"] and \
           limits["top"] <= coord[1] <= limits["bottom"]


main()
