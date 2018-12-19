X = 0
Y = 1


def main():
    with open("../input/day15.txt") as f:
        lines = [x.strip() for x in f.readlines()]

    battle_map = load_map(lines)

    elves = count_elves(battle_map)

    rounds = do_battle(battle_map, pause=False, elf_ap=19)

    remaining_elves = count_elves(battle_map)

    print("%d elves died in this combat." % (elves - remaining_elves))

    hp_total = sum([u["hp"] for u in battle_map["_units"].values()])

    print("Battle over after %d rounds, %s win.  Total remaining HP: %d\nSolution = %d" % (
        rounds,
        "elves" if [u["type"] for u in battle_map["_units"].values()][0] == "E" else "goblins",
        hp_total,
        rounds * hp_total
    ))


def count_elves(battle_map):
    return sum([1 if u["type"] == "E" else 0 for u in battle_map["_units"].values()])


def load_map(lines: list) -> dict:
    """
    Creates the battle map object, which stores the locations of all the walls and of all
    the currently-active units.  The object has the following structure:
    {
        # A map of all coordinates to a boolean indicating whether that space is a wall or not
        "_walls": {
            (0, 0): True,
            ...
        },
        # A map of the coordinates that units are on to information about that unit
        "_units": {
            (3, 3): {
                "type": "E",
                "hp": 200
            },
            ...
        },
        # The width and height of the map
        "_width": 32,
        "_height: 32
    }

    :param lines: A list of strings representing the lines of the input to parse
    :return: The battle_map object
    """
    battle_map = {
        "_walls": dict(),
        "_units": dict(),
        "_width": len(lines[0]),
        "_height": len(lines)
    }
    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            if char == '#':
                battle_map["_walls"][(x, y)] = True
            else:
                battle_map["_walls"][(x, y)] = False
                if char == "E" or char == "G":
                    battle_map["_units"][(x, y)] = {
                        "hp": 200,
                        "type": char
                    }
    return battle_map


def print_map(battle_map: dict, extras: dict = None) -> None:
    """
    Prints the contents of the given battle map to the console, and optionally any
    additional information specified.

    :param battle_map: The battle map to print
    :param extras: A dictionary mapping coordinates to values to display at those coordinates
    :return: None
    """
    lines = []
    all_units = []
    for y in range(battle_map["_height"]):
        line = ""
        units = []
        for x in range(battle_map["_width"]):
            if extras is not None and (x, y) in extras:
                line += str(extras[(x, y)])
            elif (x, y) in battle_map["_units"]:
                line += battle_map["_units"][(x, y)]["type"]
                units.append(battle_map["_units"][(x, y)])
            elif battle_map["_walls"][(x, y)]:
                line += "#"
            else:
                line += "."
        all_units.extend(units)
        if len(units) > 0:
            line += "  " + ", ".join(["%s(%d)" % (u["type"], u["hp"]) for u in units])
        lines.append(line)
    print("\n".join(lines))
    # print("\n".join(["%s(%d)" % (u["type"], u["hp"]) for u in all_units]))
    print()


def do_battle(battle_map, pause=False, elf_ap=3):
    """
    Executes a full battle, ending whenever only one side remains.
    Returns the number of rounds that it took.
    Battle map is modified in-place, and will contain the result of the battle after completion.

    :param battle_map: The battle map to process
    :return: The number of rounds the battle lasted
    """
    rounds = 0
    while not is_battle_over(battle_map):
        print("Round %d:" % rounds)
        print_map(battle_map)
        if pause:
            input()
        if execute_round(battle_map, elf_ap=elf_ap):
            break
        rounds += 1
    print_map(battle_map)
    return rounds


def is_battle_over(battle_map: dict) -> bool:
    """
    Determines whether the battle is complete or not (ie. when one side is eliminated)

    :param battle_map: The battle map to evaluate
    :return: True if the battle is over, false otherwise
    """
    seen = None
    for unit_coord, unit in battle_map["_units"].items():
        if seen is None:
            seen = unit["type"]
        elif seen != unit["type"]:
            return False
    return True


def execute_round(battle_map: dict, elf_ap=3) -> bool:
    """
    Executes one full round of combat.  Checks whether or not the battle is finished
    after each individual move.  If the battle is considered over before the last move is made,
    returns True to indicate an early cancellation.  Otherwise, returns False.

    :param battle_map: The battle map to operate on
    :return: True if the round was cancelled early, False otherwise.
    """

    # Sort the units by their read order
    move_order = sorted(battle_map["_units"].keys(),
                        key=lambda c: read_order_value(battle_map, c))

    killed = set()

    # Iterate through all units in order
    for unit_coord in move_order:

        # Cancel round early if battle is over and return True
        if is_battle_over(battle_map):
            return True

        # This catches if a unit has died mid-turn
        if unit_coord not in battle_map["_units"] or unit_coord in killed:
            continue

        # Execute movement for the turn
        unit_coord = move_unit(battle_map, unit_coord)

        # Execute attacks, if any
        kill = execute_attack(battle_map, unit_coord,
                              elf_ap if battle_map["_units"][unit_coord]["type"] == "E" else 3)

        if kill is not None:
            killed.add(kill)

    # If round completed normally, return False
    return False


def move_unit(battle_map: dict, unit_coord: tuple) -> tuple:
    """
    Performs one round of movement for the unit at the given coordinate.

    :param battle_map: The battle map
    :param unit_coord: The coordinate of the unit to move
    :return: The coordinate of the unit after movement.  It's possible this will equal the
    given coordinate if the unit did not move.
    """

    # Identify all squares that are adjacent to enemies, and thus are targets for movement
    attack_squares = get_attack_squares(battle_map, unit_coord)

    # If there are no available attacking squares, or if the unit is already in one, don't move
    if len(attack_squares) == 0 or unit_coord in attack_squares:
        return unit_coord

    # Calculate the paths to all attack squares
    # The paths are calculated "backwards", as in it finds the path from the target square
    # to the unit's square.  This is because the algorithm can optimize to find the route
    # where it can do the optimal path in terms of read-order from the end backwards...
    # so by reversing the search we end up finding the best first step to take based on
    # read-order.
    attack_paths = {square: get_path(battle_map, square, unit_coord) for square in attack_squares}

    # Identify the shortest attack path, prioritizing targets based on read order given ties
    target, dist = get_lowest({c: len(path) for c, path in attack_paths.items()
                               if path is not None},
                              tiebreaker=lambda c: read_order_value(battle_map, c))

    # If no target was found, don't move
    if target is None:
        return unit_coord

    # Select the best path
    path = attack_paths[target]

    # Get the first move of the (reversed) path (path[-1] == unit_coord)
    best_move = path[-2]

    # Replace the unit on the battle map by deleting its old entry and placing a new one
    # at the movement location
    unit = battle_map["_units"][unit_coord]
    del battle_map["_units"][unit_coord]
    unit_coord = best_move
    battle_map["_units"][unit_coord] = unit

    return unit_coord


def execute_attack(battle_map: dict, unit_coord: tuple, damage: int):
    """
    Identifies the highest priority attack target, and if it exists, damages it.
    If a unit is killed by this attack, its coordinate is returned.  Otherwise
    returns None.

    :param battle_map: The battle map
    :param unit_coord: The coordinate of the attacking unit
    :param damage: The damage to deal upon attack
    :return: The coordinate location of a unit that was killed, if any.  Otherwise, None.
    """

    # Identify all adjacent targets
    neighbor_map = {c: battle_map["_units"][c]["hp"] for c in get_neighbors(battle_map, unit_coord)
                    if c in battle_map["_units"]
                    and battle_map["_units"][c]["type"] != battle_map["_units"][unit_coord]["type"]}

    # Identify the lowest HP target.  Given a tie, take the one with the lower read order.
    target, hp = get_lowest(neighbor_map,
                            tiebreaker=lambda c: read_order_value(battle_map, c))

    # If no target was found, simply don't attack
    if target is None:
        return

    # Deal the damage.  If it kills the unit, remove it from the battle map
    hp -= damage
    if hp <= 0:
        del battle_map["_units"][target]
        return target
    else:
        battle_map["_units"][target]["hp"] = hp
        return None


def get_attack_squares(battle_map: dict, unit_coord: tuple) -> set:
    """
    Generates a set of squares adjacent to enemies of the unit at the given coord.

    :param battle_map: The battle map
    :param unit_coord: The coordinate unit to find attack squares for
    :return: A set of attackable squares (coordinate tuples)
    """
    attack_squares = set()
    for enemy_coord, enemy_info in battle_map["_units"].items():
        if enemy_coord == unit_coord or enemy_info["type"] == battle_map["_units"][unit_coord]["type"]:
            continue

        attack_squares = attack_squares.union(filter(lambda c: c not in battle_map["_units"] or c == unit_coord,
                                                     get_neighbors(battle_map, enemy_coord)))

    return attack_squares


def get_path(battle_map, start, end):
    """
    Calculates the shortest path between the given start and end points, all A* style.

    :param battle_map: The battle map
    :param start: The starting point of the path
    :param end: The ending point of the path
    :return: A list of coordinate tuples marking the shortest path between start and end.
    If no path could be found, returns None.
    If a path was found, the first element of the list (0) will always be the start coord,
    and the last element (-1) will always be the end coord.
    """

    # The set of coordinates that have already been checked
    closed = set()

    # The set of coordinates that are due to be checked
    available = {start}

    # A dictionary that maps coordinates of squares to an adjacent square that is one step
    # closer to the starting point
    came_from = dict()

    # A dictionary that maps coordinates to their G values (shortest distance to start)
    g = {start: 0}

    # A dictionary that maps coordinates to their F values (the g value, plus the manhattan
    # distance to the end coordinate
    f = {start: manhattan(start, end)}

    found_end = None

    # While we have not yet exhausted all search options
    while len(available) != 0:

        # Find the lowest F-score out of the available coordinates, prioritizing
        # those with lower read values
        current = get_lowest({c: f[c] for c in available},
                             tiebreaker=lambda c: read_order_value(battle_map, c))[0]

        # TERMINAL CASE:
        # If we found a path to the end already, and the f-score of the currently-selected
        # square (which should be the lowest f-score out of the still-available squares)
        # is higher than that of the final square, then we must have already found all
        # of the possible shortest paths (and came_from will have been updated to
        # represent the best of them).  Build the path and return it!
        if found_end is not None and found_end < f[current]:
            return build_path(battle_map, g, start, end)

        # If the coordinate we're looking at is the end coordinate, then we've found a path.
        # It is guaranteed to be *a* shortest path between the two, but not necessarily *the*
        # shortest path.  We mark a flag here to indicate that we've found a solution, and once
        # we're certain we have the best solution in hand, then we'll call it quits and build
        # the best path here.
        if current == end:
            found_end = f[current]

        # Remove coordinate from available list and mark it as having been checked
        available.remove(current)
        closed.add(current)

        # Get a collection of all neighbors that are pathable (no walls or units) and iterate through them
        pathable_neighbors = filter(lambda c: pathable(battle_map, c) or c == end, get_neighbors(battle_map, current))
        for neighbor in pathable_neighbors:

            # If this neighbor has already been evaluated, ignore it
            if neighbor in closed:
                continue

            # Calculate the g-score of all neighbors if they were to come through the current square
            g_score = g[current] + 1

            # Add the neighbor to the set of available coordinates for the next iteration
            available.add(neighbor)

            # Update the g-score (and came_from coordinate) for the neighbor if one of the following is true:
            #  - The neighbor does not yet have a g-score
            #  - The neighbor's existing g-score is higher than it would be if coming from the current square
            #  - The neighbor's existing g-score is the same as it would be if coming from the current square,
            #    but the current square has a lower read order value
            if neighbor not in g or g[neighbor] > g_score or \
                    (g[neighbor] == g_score and
                     read_order_value(battle_map, current) < read_order_value(battle_map, came_from[neighbor])):
                g[neighbor] = g_score
                came_from[neighbor] = current
                f[neighbor] = g_score + manhattan(neighbor, end)

    # If we never reached the end before exhausting all options, no path was found.  Return None.
    return None


# def build_paths(battle_map: dict, g: dict, start: tuple, end: tuple) -> list:
#
#     if start == end:
#         return [[start]]
#
#     lowest_moves = []
#     lowest_g = None
#     for c in get_neighbors(battle_map, end):
#         if c not in g:
#             continue
#         if lowest_g is None or lowest_g > g[c]:
#             lowest_g = g[c]
#             lowest_moves = [c]
#         elif lowest_g == g[c]:
#             lowest_moves.append(c)
#
#     paths = []
#     for lowest in lowest_moves:
#         subpaths = build_paths(battle_map, g, start, lowest)
#         for subpath in subpaths:
#             paths.append(subpath + [end])
#
#     return paths

def build_path(battle_map: dict, g: dict, start: tuple, end: tuple) -> list:
    """
    Determines the path between the start and end node based on the given came_from mapping

    :param battle_map: The battle map
    :param g: A dictionary that maps coordinate locations to their g-scores in this particular
    routing.
    :param start: The start of the path
    :param end: The end of the path
    :return: A list of coordinate tuples marking the shortest path between start and end.
    If no path could be found, returns None.
    If a path was found, the first element of the list (0) will always be the start coord,
    and the last element (-1) will always be the end coord.
    """

    # Works backwards from the end node, following the came_from directions until reaching the start,
    # appending all visited nodes, then reversing the list at the end
    path = []
    current = end
    while current != start:
        path.append(current)
        current = get_lowest({c: g[c] for c in get_neighbors(battle_map, current)
                              if c in g},
                             tiebreaker=lambda c: read_order_value(battle_map, c))[0]
    path.append(start)

    path.reverse()
    return path


def get_neighbors(battle_map: dict, coord: tuple):
    """
    Get all neighbors to the given coordinate that are not occupied by walls

    :param battle_map: The battle map
    :param coord: The coordinate to find neighbors for
    :return: A collection of wall-free neighbor coordinate tuples
    """
    return filter(lambda c: not battle_map["_walls"][c], [(coord[X] - 1, coord[Y]),
                                                          (coord[X] + 1, coord[Y]),
                                                          (coord[X], coord[Y] - 1),
                                                          (coord[X], coord[Y] + 1)])


def pathable(battle_map: dict, coord: tuple) -> bool:
    """
    Determines whether the given coordinate is pathable (ie. does not contain a wall or a unit)

    :param battle_map: The battle map
    :param coord: The coordinate to test for pathability
    :return: Returns True if the square is pathable, False otherwise
    """
    return not battle_map["_walls"][coord] and coord not in battle_map["_units"]


def crow(coord1: tuple, coord2: tuple) -> float:
    """
    Calculate the "as the crow flies" distance between the two coordinates
    :param coord1:
    :param coord2:
    :return:
    """
    return (((coord1[X] - coord2[X]) ** 2) + ((coord1[Y] - coord2[Y]) ** 2)) ** 0.5


def manhattan(coord1: tuple, coord2: tuple) -> int:
    """
    Determines the manhattan distance between the two coordinates
    :param coord1:
    :param coord2:
    :return:
    """
    return abs(coord1[X] - coord2[X]) + abs(coord1[Y] - coord2[Y])


def read_order_value(battle_map: dict, coord: tuple) -> int:
    """
    Calculate read order value for the given coordinate

    :param battle_map: The battle map
    :param coord: The coordinate to calculate read order for
    :return: The read order value for the given coordinate
    """
    return (coord[Y] * battle_map["_width"]) + coord[X]


def get_lowest(m: dict, tiebreaker=None) -> tuple:
    """
    Identifies the item in the given dictionary with the lowest value.  If a tiebreaker is
    provided, breaks ties according to which item's key maps to a lower value with the given
    tiebreaker lambda

    :param m: The dictionary of key-value pairs to compare the values of
    :param tiebreaker: A lambda function that maps the key type of the given dictionary to
    a comparable value.
    In the event multiple items share the same minimum value and this tiebreaker is defined,
    the tiebreaker is applied to the key values, and the key with the lowest mapped value
    is chosen.

    :return: A tuple containing:
     - 0: The key of the smallest item
     - 1: The value of the smallest item
    """
    min_key = None
    min_value = None
    for key, value in m.items():
        if min_value is None or value < min_value or (tiebreaker is not None and
                                                      value == min_value and
                                                      tiebreaker(key) < tiebreaker(min_key)):
            min_value = value
            min_key = key
    return min_key, min_value


main()
