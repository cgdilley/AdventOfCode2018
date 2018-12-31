import re
import math
REGEX = re.compile(r"pos=<([\d\-]+),([\d\-]+),([\d\-]+)>, r=(\d+)")
X = 0
Y = 1
Z = 2


def main():
    with open("../input/day23.txt", "r") as f:
        lines = [l.strip() for l in f.readlines()]

    nanos = parse_nanos(lines)

    # Ok so this solution is kinda cool, I like how it turned out.
    # Credits to my dad for inspiring it... I explained the problem of how big the
    # search space was, and he was like "why don't you scale it down?"
    # At first I was like, well then I'll lose precision that I can't afford to lose,
    # but A-HA!  It can still be helpful for narrowing the search space
    #
    # So here's the basic idea... scale down the entire field of nanobots by a very large
    # factor (in this case, 2^-24).  This puts the coordinates and radii of the "spheres"
    # into single and double digits.  From here, search through all points contained in the
    # spheres to find the one with the most overlapping spheres.  It is guaranteed that when
    # this region is scaled up to full-size, the correct answer will be somewhere inside this
    # region.
    #
    # From there, we double the scale in all directions, meaning this one coordinate now becomes
    # a 2x2x2 region.  We test all 8 of the points in this region, and find the ones that have the
    # most overlapping spheres at this scale.  Then among those that have the most, find which ones
    # are the closest to origin.  If there are ties for the closest, keep track of all of these... they all
    # might contain the solution.  Then the area contained by these regions becomes the search space
    # for the next iteration.
    #
    # We continue doubling the scale, narrowing the search space over and over.  As we approach
    # full scale, the number of regions tied for the most overlapping spheres that are also tied
    # for being closest to the origin will increase significantly, meaning that processing time
    # does scale up over time (in an ideal world, only one point would be closest, and we'd only
    # have to check exactly 8 points each iteration.  In reality, we end up having to test hundreds).
    #
    # Then finally, we arrive at full scale with the search space significantly narrowed, allowing
    # one more pass to find the coordinates for the solution (and the distance they all lie from
    # the origin).  Tada!
    #
    # Even with this optimization this program still takes a good long while to run.  I'm not
    # sure where more optimizations can be found (or, if there is a simple geometric solution).
    # The only thing I had considered was tossing out spheres that we know don't overlap with the
    # solution region.  I implemented this at one point, but it didn't seem to give a meaningful
    # performance increase.  The methodology I employed required a fair bit of memory and overhead,
    # and the solution region always had most spheres overlapping anyway (800+), and it made the
    # code significantly uglier and difficult to read.  I decided it wasn't worth it and discarded it.
    # Perhaps designing with that in mind from the ground up would result in a cleaner, more
    # efficient result.

    # Here are some base+power combos I tried
    # (3, -15), (2, -24), (4, -12)
    result = scale_and_search(nanos, 2, -24)

    print("The closets points are located at:\n%s\nThe distance from origin is: %d" %
          (str(result), manhattan((0, 0, 0), result[0])))


def parse_nanos(lines: list) -> list:
    return [Nanobot.parse(line, number) for number, line in enumerate(lines)]


class Nanobot:
    def __init__(self, x, y, z, r):
        self.pos = (x, y, z)
        self.r = r
        self.number = 0

    def __str__(self):
        return "%s -- %d" % (str(self.pos), self.r)

    def __repr__(self):
        return str(self)

    def set_number(self, number):
        self.number = number
        return self

    @staticmethod
    def parse(line, number):
        m = REGEX.match(line)
        return Nanobot(int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))).set_number(number)


def scale_and_search(nanos: list, base: int, power: int) -> list:
    """
    Identifies the coordinate locations in the nanobot space that have the most overlapping
    signal spheres from the nanobots, and then filters those results down to only include
    the ones that are tied for closest to the origin point (0, 0, 0).

    Starts by scaling the nanobot space by (base ** power), and then increases the scale by
    (base) repeatedly until reaching full scale.

    :param nanos: The nanobots
    :param base: The base value for scaling.  Powers of this value will be used for scaling,
    and each iteration scales up by this amount from the previous iteration.
    :param power: The (negative) power to begin the scaling from.  Represents the number of
    iterations to perform.
    :return:
    """
    # Scale down to the minimum scale
    s_nanos = scale_down_nanos(nanos, base ** power)

    # Do the initial search, only including spaces that are within spheres
    # and finding the sector with the most overlaps closest to origin
    spaces = search_nanos(s_nanos)

    # Iterate through different scale levels (eg 2^-23, 2^-22, etc.)
    for pwr in range(power + 1, 1):

        print("Doing processing at 1/%d (%f) scale -- %d ^ %d" %
              (base ** -pwr, base ** pwr, base, pwr))

        # The spaces to process next iteration
        new_spaces = []

        # Scale the nanobots down to the current scale
        s_nanos = scale_down_nanos(nanos, base ** pwr)

        # Iterate through all known solution spaces (regions where the final
        # solution might be found)
        for space in spaces:
            # Build the search space that scales up the space by the base, resulting
            # in a bounding area that has the dimensions base x base x base
            s_bounds = {
                "min": scale_coord(space, base),
                "max": ((space[X] + 1) * base, (space[Y] + 1) * base, (space[Z] + 1) * base)
            }

            # Find all of the coordinates that have the highest number of overlapping
            # spheres within the specified search space
            s = search_space(s_nanos, s_bounds)

            # Add the found spaces to the set of coordinates
            new_spaces.extend(s)

        # Of the spaces identified that have the highest number of overlapping spheres,
        # identify the ones that are closest to the origin.  Use these as the
        # search spaces for the next iteration.
        closest = []
        closest_dist = None
        for new_space in new_spaces:
            dist = manhattan((0, 0, 0), new_space)
            if closest_dist is None or dist < closest_dist:
                closest = [new_space]
                closest_dist = dist
            elif closest_dist == dist:
                closest.append(new_space)

        spaces = closest

    # The search spaces found at full-scale represent the solution
    return spaces


def search_nanos(nanos: list) -> list:
    """
    Finds the coordinate locations with the most overlapping nanobot signal spheres.
    NOTE:  This alone would find the final solution to the problem if it were feasible
    to execute at full scale (its not).

    :param nanos: The nanobots.
    :return: A list of coordinate locations that have the highest number of overlapping
    nanobot signal spheres.
    """
    counts = dict()
    max_count = 0
    max_coords = []

    # Essentially slices the "sphere" (which is more like a prism) along the X-Y plane, creating
    # new X-Y slices along the Z axis.  Slices further from Z=0 are smaller, so that at Z=0,
    # the slice is ((radius * 2) + 1) by ((radius * 2) + 1), and at Z=radius, the slice is 1 by 1.
    #    O
    #   OOO
    #  OOOOO
    #   OOO
    #    O
    for nb in nanos:
        for z_diff in range(-nb.r, nb.r + 1):
            plane_size = nb.r - abs(z_diff)
            for x in range(nb.pos[X] - plane_size, nb.pos[X] + plane_size + 1):
                for y in range(nb.pos[Y] - plane_size, nb.pos[Y] + plane_size + 1):
                    c = (x, y, nb.pos[Z] + z_diff)
                    if c not in counts:
                        counts[c] = 0
                    else:
                        counts[c] += 1

                    # Keep track of the coordinates with the most overlapping spheres
                    cnt = counts[c]
                    if max_count < cnt:
                        max_count = cnt
                        max_coords = [c]
                    elif max_count == cnt:
                        max_coords.append(c)

    return max_coords


def search_space(nanos: list, bounds: dict) -> list:
    """
    Searches through all points contained in the given bounds, identifying those
    with the highest number of overlapping nanobot signal spheres from the given
    nanobots.
    :param nanos: The nanobots
    :param bounds: The bounds to search, the form:
    {
        "min": (X, Y, Z),
        "max": (X, Y, Z)
    }
    :return: A list of coordinates that have the highest number of overlapping spheres
    """
    max_coords = []
    max_value = 0
    for x in range(bounds["min"][X], bounds["max"][X] + 1):
        for y in range(bounds["min"][Y], bounds["max"][Y] + 1):
            for z in range(bounds["min"][Z], bounds["max"][Z] + 1):
                c = (x, y, z)
                in_range = get_nanos_in_range(nanos, c)
                count = len(in_range)
                if max_value < count:
                    max_coords = [c]
                    max_value = count
                elif max_value == count:
                    max_coords.append(c)
    return max_coords


def scale_down_nanos(nanos: iter, factor: float) -> list:
    """
    Create a copy of the given nanobot space, except it is scaled by the given factor

    :param nanos: The nanobots to scale
    :param factor: The scaling factor
    :return: A list of the given nanobots scaled by the given factor
    """
    return [Nanobot(math.floor(nb.pos[X] * factor),
                    math.floor(nb.pos[Y] * factor),
                    math.floor(nb.pos[Z] * factor),
                    math.ceil(nb.r * factor)).set_number(nb.number)
            for nb in nanos]


def scale_coord(coord: tuple, factor: float) -> tuple:
    return tuple(math.floor(dim * factor) for dim in coord)


def get_nanos_in_range(nanos: iter, location: tuple) -> list:
    return list(filter(lambda nb: manhattan(nb.pos, location) <= nb.r, nanos))


# def scale_bounds(bounds: dict, factor: float) -> dict:
#     return {
#         "min": scale_coord(bounds["min"], factor),
#         "max": scale_coord(bounds["max"], factor)
#     }
#
#
# def find_bounds(nanos: list) -> dict:
#     min_coord = list(nanos[0].pos)
#     max_coord = list(nanos[0].pos)
#     for nano in nanos[1:]:
#         for dim, val in enumerate(nano.pos):
#             if min_coord[dim] > val:
#                 min_coord[dim] = val
#             if max_coord[dim] < val:
#                 max_coord[dim] = val
#
#     return {
#         "min": tuple(min_coord),
#         "max": tuple(max_coord)
#     }


def manhattan(coord1: tuple, coord2: tuple) -> int:
    """
    Hey, I've generalized the manhattan distance calculation for any number of dimensions.
    :param coord1:
    :param coord2:
    :return:
    """
    return sum(abs(c[0] - c[1]) for c in zip(coord1, coord2))


#

main()
