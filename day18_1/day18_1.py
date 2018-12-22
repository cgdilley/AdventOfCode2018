X = 0
Y = 1
OPEN = "."
TREE = "|"
LUMBERYARD = "#"
import csv


def main():
    with open("../input/day18.txt", "r") as f:
        lines = [l.strip() for l in f.readlines()]

    lumber_map, bounds = load_lumber_map(lines)

    lumber_map, history = iterate_lumber_map(lumber_map, bounds, 1000)

    # write_history_to_file(history)

    # Turns out the lumber map settles into a stable cycle that repeats
    # every 28 minutes.  This is all very stupid and hacky how I figured
    # this part out, I'm sure I could've done this more elegantly and
    # intelligently but these kind of questions make me cranky

    # I'm sure there's a smarter way to calc this but whatever
    identical_minute = 10 ** 9
    while identical_minute >= 1000:
        identical_minute -= 28 * 10

    groups = history[identical_minute - 1]

    print("The final map has %d trees and %d lumberyards.\nThe resource value is: %d" %
          (groups[TREE], groups[LUMBERYARD], groups[TREE] * groups[LUMBERYARD]))


def load_lumber_map(lines):
    lumber_map = dict()
    bounds = {"_width": len(lines[0]), "_height": len(lines)}
    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            lumber_map[(x, y)] = char
    return lumber_map, bounds


def update_lumber_map(lumber_map):
    new_lumber_map = dict()
    groups = {
        LUMBERYARD: 0,
        TREE: 0,
        OPEN: 0
    }

    for location, char in lumber_map.items():
        neighbors = get_adjacent_squares(lumber_map, location)
        neighbor_group = group_squares(get_values_for_locations(lumber_map, neighbors))

        if char == OPEN and neighbor_group[TREE] >= 3:
            new_char = TREE
        elif char == TREE and neighbor_group[LUMBERYARD] >= 3:
            new_char = LUMBERYARD
        elif char == LUMBERYARD and (neighbor_group[TREE] == 0 or neighbor_group[LUMBERYARD] == 0):
            new_char = OPEN
        else:
            new_char = char

        groups[new_char] += 1
        new_lumber_map[location] = new_char

    return new_lumber_map, groups


def iterate_lumber_map(lumber_map, bounds, minutes):
    history = []
    for minute in range(minutes):
        lumber_map, groups = update_lumber_map(lumber_map)
        history.append(groups)

        if minute % 100 == 0:
            print("Finished minute %d." % minute)
            print("Group counts: %s" % str(groups))
            # print_lumber_map(lumber_map, bounds)

    return lumber_map, history


def print_lumber_map(lumber_map, bounds):
    for y in range(bounds["_height"]):
        line = ""
        for x in range(bounds["_width"]):
            line += lumber_map[(x, y)]
        print(line)
    print()


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


def write_history_to_file(history):
    with open("../input/day18_OUTPUT.csv", "w") as f:
        writer = csv.writer(f, lineterminator='\n')
        for minute in range(len(history)):
            writer.writerow([minute, history[minute][TREE],
                             history[minute][LUMBERYARD],
                             history[minute][OPEN]])



#

main()
