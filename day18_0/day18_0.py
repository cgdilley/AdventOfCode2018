X = 0
Y = 1
OPEN = "."
TREE = "|"
LUMBERYARD = "#"


def main():
    with open("../input/day18.txt", "r") as f:
        lines = [l.strip() for l in f.readlines()]

    lumber_map = load_lumber_map(lines)

    lumber_map = iterate_lumber_map(lumber_map, 10)

    groups = group_squares(lumber_map.values())

    print("The final map has %d trees and %d lumberyards.\nThe resource value is: %d" %
          (groups[TREE], groups[LUMBERYARD], groups[TREE] * groups[LUMBERYARD]))


def load_lumber_map(lines):
    lumber_map = dict()
    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            lumber_map[(x, y)] = char
    return lumber_map


def update_lumber_map(lumber_map):
    new_lumber_map = dict()

    for location, char in lumber_map.items():
        neighbors = get_adjacent_squares(lumber_map, location)
        neighbor_group = group_squares(get_values_for_locations(lumber_map, neighbors))

        if char == OPEN and neighbor_group[TREE] >= 3:
            new_lumber_map[location] = TREE
        elif char == TREE and neighbor_group[LUMBERYARD] >= 3:
            new_lumber_map[location] = LUMBERYARD
        elif char == LUMBERYARD and (neighbor_group[TREE] == 0 or neighbor_group[LUMBERYARD] == 0):
            new_lumber_map[location] = OPEN
        else:
            new_lumber_map[location] = char

    return new_lumber_map


def iterate_lumber_map(lumber_map, minutes):

    for _ in range(minutes):
        lumber_map = update_lumber_map(lumber_map)

    return lumber_map


def get_adjacent_squares(lumber_map, location):
    neighbors = []
    for x_mod in [-1, 0, 1]:
        for y_mod in [-1, 0, 1]:
            if x_mod == y_mod == 0:
                continue
            x = location[X] + x_mod
            y = location[Y] + y_mod
            if (x, y) in lumber_map:
                neighbors.append((x, y))
    return neighbors


def get_values_for_locations(lumber_map, locations):
    return [lumber_map[l] for l in locations]


def group_squares(squares):
    groups = {
        LUMBERYARD: 0,
        TREE: 0,
        OPEN: 0
    }
    for square in squares:
        groups[square] += 1
    return groups


#

main()
