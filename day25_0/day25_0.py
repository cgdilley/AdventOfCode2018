X = 0
Y = 1
Z = 2
T = 3


def main():
    with open("../input/day25.txt", "r") as f:
        lines = [l.strip() for l in f.readlines()]

    coords = load_coords(lines)

    constellations = form_constellations(coords, 3)

    unique = get_unique_constellations(constellations)

    print("There are %d constellations." % len(unique))


def load_coords(lines):
    return [tuple([int(dim) for dim in line.split(",")]) for line in lines]


def form_constellations(coords: list, dist: int) -> dict:
    """
    Identifies the constellations that each coordinate belongs to, returning a dictionary
    that maps all the given coordinate positions to lists of coordinates that belong to the
    constellation that that coordinate is in.

    :param coords: The list of spacetime coordinates
    :param dist: The maximum manhattan distance to consider for constellation formation
    :return: A dictionary mapping all coordinates to a list of their constellation coordinates
    """
    constellations = dict()

    # Iterate through all coordinates
    for pos, coord in enumerate(coords):

        # If this coordinate was encountered before, start by using its existing constellation info.  Otherwise,
        # start with a set of just itself.
        nearby = {coord} if coord not in constellations else constellations[coord]

        # Iterate through all other coordinates (that haven't been already encountered by this containing loop)
        others = coords[pos+1:]
        for other in others:

            # If this other coordinate is already in the nearby list for this, don't waste time calculating
            if other in nearby:
                continue

            # Calculate the manhattan distance between the two coordinates
            man = manhattan(coord, other)

            # If the other coordinate is within range, add it and any other coordinates it already shares a
            # constellation with to the list of nearby coordinates
            if man <= dist:
                if other in constellations:
                    nearby = nearby.union(constellations[other])
                else:
                    nearby.add(other)

        # After having collected a set of all nearby coordinates (and the constellations that those coordinates are
        # already in), update the constellations list to ensure that all of the coordinates know that they belong
        # in the same constellation together
        for n in nearby:
            constellations[n] = nearby

    return constellations


def get_unique_constellations(constellations: dict) -> list:
    """
    Given a dictionary that maps coordinates to a list of coordinates it forms a constellation with,
    constructs a list of all unique constellations.

    :param constellations: A constellation dictionary as generated by form_constellations()
    :return: A list of unique constellations
    """

    unique = []
    seen = set()
    for coord, constell in constellations.items():
        if coord in seen:
            continue

        seen = seen.union(constell)
        unique.append(constell)

    return unique

    # unique = set()
    # for c in constellations.values():
    #     unique.add(tuple(sorted(c, key=lambda coord: (coord[X] * 1000) + (coord[Y] * 100) +
    #                                                  (coord[Z] * 10) + coord[T])))
    # return list([list(constellation) for constellation in unique])


def manhattan(coord1: tuple, coord2: tuple) -> int:
    """
    Hey, I've generalized the manhattan distance calculation for any number of dimensions.
    :param coord1:
    :param coord2:
    :return:
    """
    return sum(abs(dim1 - dim2) for dim1, dim2 in zip(coord1, coord2))


#

main()
