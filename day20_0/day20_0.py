X = 0
Y = 1


def main():
    with open("../input/day20.txt", "r") as f:
        directions = f.read().strip()[1:-1]

    base_map, ending_locations = build_base_map(directions)

    print_base_map(base_map)

    path = path_to_most_distant_room(base_map, ending_locations)

    print("The shortest distance to the furthest room is to the room at %s: %d doors" %
          (str(path[-1]), len(path) - 1))


def print_base_map(base_map: dict) -> None:
    """
    Prints the contents of the base map to console.

    :param base_map: The base map to print
    :return: None
    """
    bounds = get_bounds(base_map)

    for y in range(bounds["top"], bounds["bottom"] + 1):
        # Render the North and West doors (or walls) as specified by
        # each room.  Since doors are reciprocal with neighbors, this
        # is sufficient to render all doors (and the rightmost and
        # bottommost edge are assumed to be walls)
        s = ["", ""]
        for x in range(bounds["left"], bounds["right"] + 1):
            if (x, y) not in base_map:
                s[0] += "##"
                s[1] += "##"
            else:
                s[0] += "#-" if base_map[(x, y)]["N"] else "##"
                s[1] += "|." if base_map[(x, y)]["W"] else "#."
        s[0] += "#"
        s[1] += "#"
        print(s[0])
        print(s[1])

    # Draw the bottom wall
    print("#" * (((1 + bounds["right"] - bounds["left"]) * 2) + 1))


def get_bounds(base_map: dict) -> dict:
    """
    Find the upper and lower bounds in both the X and Y directions for the
    given base map.

    :param base_map: The base map.
    :return: An object representing the bounds of the base map, in the form:
    {
        "left": 0,
        "right": 0,
        "top": 0,
        "bottom": 0
    }
    """
    bounds = {"left": None, "right": None, "top": None, "bottom": None}
    for loc in base_map.keys():
        if bounds["left"] is None or bounds["left"] > loc[X]:
            bounds["left"] = loc[X]
        if bounds["right"] is None or bounds["right"] < loc[X]:
            bounds["right"] = loc[X]
        if bounds["top"] is None or bounds["top"] > loc[Y]:
            bounds["top"] = loc[Y]
        if bounds["bottom"] is None or bounds["bottom"] < loc[Y]:
            bounds["bottom"] = loc[Y]
    return bounds


def in_bounds(bounds: dict, location: tuple) -> bool:
    """
    Determines whether the given location falls within the given bounds

    :param bounds: A bounds object, as created by get_bounds()
    :param location: The location to test
    :return: True if the given location is within the given bounds, false otherwise.
    """
    return bounds["left"] <= location[X] <= bounds["right"] and \
           bounds["top"] <= location[Y] <= bounds["bottom"]


def build_base_map(directions: str) -> (dict, list):
    """
    Constructs the base map with the given pathing regex directions

    :param directions: A pathing regex of all directions (the puzzle input)
    :return: The fully constructed base map
    """

    # Start the recursive process of reading the directions
    base_map = dict()
    location = (0, 0)
    ending_locations = follow_directions(base_map, {location}, directions)
    return base_map, ending_locations


def follow_directions(base_map: dict, start_locations: set, directions: str) -> set:
    """
    Recursively operates on the given directions for all of the given locations
    on the given base map.

    :param base_map: The base map as constructed thus far.
    :param start_locations: A set of coordinates of current operating locations
    for path-forming operations.
    :param directions: A string containing directions
    :return: The ending locations resulting from processing all of the given start_locations
    through the given directions.  The number of ending locations may be larger than the
    number of starting locations.
    """

    # The strategy here is as follows:
    # Start with a set of locations to operate on.  To begin with, this will be a set containing
    # just the coordinate (0, 0).
    # Iterate through all of the instructions one by one.
    # For normal movement instructions, perform the movement on all of the coordinates in the
    # set of current coordinates.  Add rooms to the base map if a room at the coordinates has
    # not yet been encountered, and then indicate for each room that a door exists between
    # them.
    #
    # If encountering an opening parenthesis, find the corresponding closing parenthesis, and then
    # recursively call this function on the substring bound by the 2 parentheses, operating on all
    # of the current locations and returning them.  Then continue processing with the
    # instructions immediately after the closing parenthesis as normal.
    #
    # If encountering a bar |, recursively call this function with the remaining string following
    # the bar, but passing the initially-given set of start coordinates rather than the set of
    # current coordinates.  The ending coordinates produced by this recursive call are unioned into
    # the set of current coordinates; this is how the number of current coordinates can grow.
    #
    # After reaching the end of the directions, the base map will be fully constructed, and the
    # finalized set of current coordinates is returned.

    #

    string_pos = 0
    # Copy the start locations
    curr_locations = {l for l in start_locations}

    # Iterate through all instructions
    while string_pos < len(directions):

        # Get the current instruction
        char = directions[string_pos]

        # If the character is an opening parenthesis, find the substring bound by it and its
        # corresponding closing parenthesis and recursively operate on it, allowing the
        # current coordinates to be updated.
        if char == "(":
            sub = get_parentheses_substring(directions, string_pos)
            curr_locations = follow_directions(base_map, curr_locations, sub)
            string_pos += len(sub) + 1

        # If the character is a bar, recursively operate on the remainder of the string, adding
        # the branched locations it generated to the set of current coordinates, then immediately
        # return them.
        elif char == "|":
            branched_locations = follow_directions(base_map, start_locations, directions[string_pos + 1:])
            curr_locations = curr_locations.union(branched_locations)
            return set(curr_locations)

        # Otherwise, add a door to the current room in the specified direction, move that direction, then
        # add a door on this new room in the opposite direction (connecting to the original room) in order
        # to satisfy reciprocity.
        else:
            new_locations = set()
            for loc in curr_locations:
                add_door(base_map, loc, char)
                new_loc = move(loc, char)
                new_locations.add(new_loc)
                add_door(base_map, new_loc, opposite(char))
            curr_locations = new_locations

        # Advance to next instruction
        string_pos += 1

    # Return the final set of current locations
    return curr_locations


def add_door(base_map: dict, location: tuple, side: str) -> None:
    """
    Adds the door in the specified direction to the specified location.
    If the location does not yet exist in the given base map, creates the
    room first.

    :param base_map: The base map
    :param location: The location to add a door to
    :param side: The direction of the door to add ("E", "S", "W", "N")
    :return: None
    """
    if location not in base_map:
        base_map[location] = {side: False for side in "EWNS"}

    base_map[location][side] = True


def opposite(side: str) -> str:
    """
    Returns the direction that is opposite the given direction.

    :param side: The direction to find the opposite of.
    :return: The opposite of the given direction.
    """
    return {
        "E": "W",
        "W": "E",
        "N": "S",
        "S": "N"
    }[side]


def move(location: tuple, direction: str) -> tuple:
    """
    Generates a new coordinate tuple that represents moving the given direction
    from the given location.
    :param location: The location to move from
    :param direction: The direction to move towards
    :return: The coordinate result of the movement
    """
    return {
        "E": (location[X] + 1, location[Y]),
        "W": (location[X] - 1, location[Y]),
        "N": (location[X], location[Y] - 1),
        "S": (location[X], location[Y] + 1)
    }[direction]


def get_parentheses_substring(string: str, start_pos: int) -> str:
    """
    Identifies the substring bound by an opening parenthesis at the given location
    and its corresponding closing parenthesis.

    :param string: The string to get the substring from
    :param start_pos: The location of the opening parenthesis
    :return: The substring bound by an opening parenthesis at the given location
    and its corresponding closing parenthesis.
    """
    layer = 1
    parent_pos = start_pos + 1
    while parent_pos < len(string):
        c = string[parent_pos]
        if c == "(":
            layer += 1
        elif c == ")":
            layer -= 1
        if layer == 0:
            break
        parent_pos += 1
    return string[start_pos + 1: parent_pos]


def path_to_most_distant_room(base_map, ending_locations):

    longest_path = None

    for loc in ending_locations:
        # if longest_path is not None and manhattan((0, 0), loc) < len(longest_path):
        #     continue

        path = get_path(base_map, (0, 0), loc)
        if longest_path is None or len(path) > len(longest_path):
            longest_path = path

    return longest_path


###############################################
# PATHFINDING
###############################################

def get_path(base_map, start, end):
    """
    Calculates the shortest path between the given start and end points, all A* style.

    :param base_map: The base map
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
        current = get_lowest({c: f[c] for c in available})[0]

        # TERMINAL CASE:
        # If we found a path to the end already, and the f-score of the currently-selected
        # square (which should be the lowest f-score out of the still-available squares)
        # is higher than that of the final square, then we must have already found all
        # of the possible shortest paths (and came_from will have been updated to
        # represent the best of them).  Build the path and return it!
        if found_end is not None and found_end < f[current]:
            return build_path(came_from, start, end)

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
        pathable_neighbors = get_neighbors(base_map, current)
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
            if neighbor not in g or g[neighbor] > g_score:
                g[neighbor] = g_score
                came_from[neighbor] = current
                f[neighbor] = g_score + manhattan(neighbor, end)

    # If we never reached the end before exhausting all options, no path was found.  Return None.
    return None


def build_path(came_from: dict, start: tuple, end: tuple) -> list:
    """
    Determines the path between the start and end node based on the given came_from mapping

    :param came_from: A dictionary that maps coordinates to adjacent coordinates that bring them
    closest to the starting point
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
        current = came_from[current]
    path.append(start)

    path.reverse()
    return path


def get_neighbors(base_map: dict, location: tuple) -> list:
    return [move(location, d) for d in "EWNS" if base_map[location][d]]


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


#

main()
