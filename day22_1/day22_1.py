import re
X = 0
Y = 1
TOOL = 2

ROCKY = 0
WET = 1
NARROW = 2

GEAR = 2
TORCH = 1
NEITHER = 0


def main():
    with open("../input/day22.txt", "r") as f:
        lines = f.readlines()
        depth = int(re.match(r"depth: (\d+)", lines[0]).group(1))
        target = tuple([int(c) for c in re.match(r"target: (\d+),(\d+)", lines[1]).groups()])

    cave_map = build_cave_map(depth, target)

    print_cave_map(cave_map, target)

    # Hey, check it out, more A*
    # This time I treat it as 3-dimensional pathfinding, where the tools represent the 3rd
    # dimension.  This means two adjacent squares may not have a connection between them due
    # to incompatible equipped tool, but we can move along this 3rd tool dimension (with an
    # additional movement cost), and then the adjacent square may be pathable.
    # This will automatically find the best path including tool switches without much tweaking
    # to the pathfinding necessary.
    route, g = find_route(cave_map, target)

    # The g cost in the final square will represent the number of minutes travelled
    minutes = g[(target[X], target[Y], TORCH)]
    print("The shortest route has %d steps, taking %d minutes.  This involves %d tool changes." %
          (len(route), minutes, (minutes - len(route)) / 7))


def print_cave_map(cave_map, target, extras=None):

    for x in range(target[X] + 1):
        s = ""
        for y in range(target[Y] + 1):
            if extras is not None and (x, y) in extras:
                s += extras[(x, y)]
            elif x == 0 and y == 0:
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
    cave_map["_target"] = target
    cave_map["_depth"] = depth

    for y in range(target[Y] + 1):
        for x in range(target[X] + 1):
            fill_in_cave_square(cave_map, (x, y))

    return cave_map


def fill_in_cave_square(cave_map: dict, location: tuple) -> None:
    """
    Simply executes the specified rules for building the cave map, nothing
    much fancy here.

    :param cave_map:
    :param location:
    :return:
    """
    x = location[X]
    y = location[Y]
    if x == 0 and y == 0:
        geo_index = 0
    elif x == 0:
        geo_index = y * 48271
    elif y == 0:
        geo_index = x * 16807
    else:
        geo_index = get_cave_square(cave_map, (x - 1, y))["erosion"] * \
                    get_cave_square(cave_map, (x, y - 1))["erosion"]

    erosion = calc_erosion(geo_index, cave_map["_depth"])
    cave_map[(x, y)] = {"erosion": erosion, "geo_index": geo_index, "terrain": terrain(erosion)}


def get_cave_square(cave_map: dict, location: tuple) -> dict:
    """
    Retrieves an existing cave square if it exists, otherwise generates it (which may entail
    recursion).
    :param cave_map: The cave map
    :param location: The coordinate of the cave square to retrieve
    :return: The cave square at the specified coordinate
    """
    if location not in cave_map:
        fill_in_cave_square(cave_map, location)

    return cave_map[location]


def calc_erosion(geo_index, depth):
    return (geo_index + depth) % 20183


def terrain(erosion):
    return erosion % 3


def find_route(cave_map, target):
    return get_path(cave_map, (0, 0, TORCH), (target[X], target[Y], TORCH))

###############################################
# PATHFINDING
###############################################


def get_path(cave_map, start, end):
    """
    Calculates the shortest path between the given start and end points, all A* style.

    :param cave_map: The cave map
    :param start: The starting point of the path
    :param end: The ending point of the path
    :return: A list of coordinate tuples marking the shortest path between start and end.
    If no path could be found, returns None.
    If a path was found, the first element of the list (0) will always be the start coord,
    and the last element (-1) will always be the end coord.
    """

    # The set of coordinates that have already been checked
    closed = set()

    # A dictionary that maps coordinates to their G values (shortest distance to start)
    g = {start: 0}

    # The set of coordinates that are due to be checked
    available = set(g.keys())

    # A dictionary that maps coordinates to their F values (the g value, plus the manhattan
    # distance to the end coordinate (plus a tool change, if necessary)
    f = {loc: h_score(loc, end) + g for loc, g in g.items()}

    # While we have not yet exhausted all search options
    while len(available) != 0:

        # Find the lowest F-score out of the available coordinates
        # ============= NOTE:
        # This seems to be a processing bottleneck.  Maybe something like a heap would be nice.  Dunno
        current = get_lowest({c: f[c] for c in available})[0]

        # TERMINAL CASE:
        # If the coordinate we're looking at is the end coordinate, then we've found a path.
        # It is guaranteed to be *a* shortest path between the two, but not necessarily *the*
        # shortest path.  For the purposes of this exercise, this is sufficient.  Build the
        # path and return it
        if current == end:
            return build_path(cave_map, g, start, end), g

        # Remove coordinate from available list and mark it as having been checked
        available.remove(current)
        closed.add(current)

        # Get a collection of all neighbors that are pathable with the current tool, as well
        # as "neighbors" that involve tool switches, and iterate through them
        pathable_neighbors = get_neighbors(cave_map, current)
        for neighbor in pathable_neighbors:

            # If this neighbor has already been evaluated, ignore it
            if neighbor in closed:
                continue

            # Calculate movement cost
            cost = 1 if neighbor[TOOL] == current[TOOL] else 7

            # Calculate the g-score of this neighbor if we were to come through the current square
            g_score = g[current] + cost

            # Add the neighbor to the set of available coordinates for the next iteration
            available.add(neighbor)

            # Update the g-score for the neighbor if one of the following is true:
            #  - The neighbor does not yet have a g-score
            #  - The neighbor's existing g-score is higher than it would be if coming from the current square
            if neighbor not in g or g[neighbor] > g_score:
                g[neighbor] = g_score
                # came_from[neighbor] = current
                f[neighbor] = g_score + h_score(neighbor, end)

    # If we never reached the end before exhausting all options, no path was found.  Return None.
    return None, g


def h_score(current, target):
    # Uses manhattan distance and incorporates tool changes
    return manhattan(current[:2], target[:2]) + (7 if current[TOOL] != target[TOOL] else 0)


def build_path(base_map: dict, g: dict, start: tuple, end: tuple) -> list:
    """
    Determines the path between the start and end node based on the given came_from mapping

    :param base_map: The base map
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
        current = get_lowest({c: g[c] for c in get_neighbors(base_map, current)
                              if c in g})[0]
    path.append(start)

    path.reverse()
    return path


def get_neighbors(cave_map: dict, location: tuple) -> list:
    """
    Retrieves the list of pathable neighbor moves, including tool changes
    :param cave_map: The cave map
    :param location: The location to find neighbors for
    :return: A list of all pathable neighbors
    """
    # So basically this simply tests moving in the 4 basic directions in order
    # to see which are accessible with the current tool.  Then also it adds
    # the tool change as a movement option.  Only one tool change is possible
    # on any given square.
    moves = []

    curr_tool = location[TOOL]
    curr_terrain = cave_map[location[:2]]["terrain"]

    for d in "EWNS":
        loc = move(location, d)
        if loc[X] < 0 or loc[Y] < 0:
            continue

        square = get_cave_square(cave_map, loc[:2])
        if square["terrain"] in valid_terrain(curr_tool):
            moves.append(loc)

    moves.append((location[X], location[Y], other_tool(curr_terrain, curr_tool)))

    return moves


def valid_tools(terr: int) -> list:
    return {
        ROCKY: [GEAR, TORCH],
        WET: [GEAR, NEITHER],
        NARROW: [TORCH, NEITHER]
    }[terr]


def other_tool(terr: int, tool: int) -> int:
    tools = valid_tools(terr)
    tools.remove(tool)
    return tools[0]


def valid_terrain(tool: int) -> list:
    return {
        GEAR: [ROCKY, WET],
        TORCH: [ROCKY, NARROW],
        NEITHER: [WET, NARROW]
    }[tool]


def manhattan(coord1: tuple, coord2: tuple) -> int:
    """
    Determines the manhattan distance between the two coordinates
    :param coord1:
    :param coord2:
    :return:
    """
    return abs(coord1[X] - coord2[X]) + abs(coord1[Y] - coord2[Y])


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


def move(location: tuple, direction: str) -> tuple:
    """
    Generates a new coordinate tuple that represents moving the given direction
    from the given location.
    :param location: The location to move from
    :param direction: The direction to move towards
    :return: The coordinate result of the movement
    """
    return {
        "E": (location[X] + 1, location[Y], location[TOOL]),
        "W": (location[X] - 1, location[Y], location[TOOL]),
        "N": (location[X], location[Y] - 1, location[TOOL]),
        "S": (location[X], location[Y] + 1, location[TOOL])
    }[direction]


#


main()
