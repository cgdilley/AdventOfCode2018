import re

X = 0
Y = 1
CLAY = 0
WATER = 1
SPRING = 2
RANGE = re.compile(r"(\d+)\.\.(\d+)")


def main():
    with open("../input/day17.txt", "r") as f:
        lines = [l.strip() for l in f.readlines()]

    ground_map, bounds = build_ground_map(lines)

    print_map(ground_map, bounds)

    water_squares, flowing = flow_from_source(ground_map, bounds, (500, 0))

    print_map(ground_map, bounds, flowing=flowing)

    print("After flowing completely, %d squares are saturated with water." % water_squares)

    for flow in flowing:
        del ground_map[flow]

    print_map(ground_map, bounds, flowing=set())

    print("After the spring runs dry, %d squares of water will be retained." % count_water(ground_map, bounds))


def build_ground_map(lines):
    x_re = re.compile(r"x=(.+?)(,|$)")
    y_re = re.compile(r"y=(.+?)(,|$)")
    ground_map = dict()
    bounds = {
        "x_min": 500,
        "y_min": None,
        "x_max": 500,
        "y_max": None
    }

    for line in lines:
        x_match = x_re.search(line)
        y_match = y_re.search(line)

        x_range = extract_range(x_match.group(1))
        y_range = extract_range(y_match.group(1))

        if bounds["x_min"] is None or bounds["x_min"] > x_range[0]:
            bounds["x_min"] = x_range[0]
        if bounds["x_max"] is None or bounds["x_max"] < x_range[-1]:
            bounds["x_max"] = x_range[-1]
        if bounds["y_max"] is None or bounds["y_max"] < y_range[-1]:
            bounds["y_max"] = y_range[-1]
        if bounds["y_min"] is None or bounds["y_min"] > y_range[0]:
            bounds["y_min"] = y_range[0]

        for x in x_range:
            for y in y_range:
                ground_map[(x, y)] = CLAY

    ground_map[(500, 0)] = SPRING

    return ground_map, bounds


def extract_range(range_string):
    match = RANGE.match(range_string)

    if match is None:
        return [int(range_string)]
    else:
        return list(range(int(match.group(1)), int(match.group(2)) + 1))


def print_map(ground_map, bounds, flowing=None, extras=None):
    for y in range(0, bounds["y_max"] + 1):
        line = ""
        for x in range(bounds["x_min"], bounds["x_max"] + 1):
            if extras is not None and (x, y) in extras:
                line += extras[(x, y)]
            elif (x, y) in ground_map:
                t = ground_map[(x, y)]
                if t == CLAY:
                    line += "#"
                elif t == SPRING:
                    line += "*"
                elif t == WATER:
                    if flowing is None:
                        line += "O"
                    elif (x, y) in flowing:
                        line += "|"
                    else:
                        line += "~"
            else:
                line += "."
        print(line)
    print()


def in_bounds(bounds, location, ignore_x=False):
    return (ignore_x or bounds["x_min"] <= location[X] <= bounds["x_max"]) and \
           bounds["y_min"] <= location[Y] <= bounds["y_max"]


def flow_from_source(ground_map, bounds, source):
    sources = [source]
    flowing = {source}

    while len(sources) > 0:
        source = sources[0]
        sources = sources[1:]

        # Sometimes a square that was previously flagged as being a source was then made to be
        # settled water by a different source.  Skip these sources
        if source not in flowing:
            continue

        print("Processing source at %s.  Current water count: %d" % (str(source),
                                                                     count_water(ground_map, bounds)))

        settle_source = flow_downwards(ground_map, bounds, source, flowing)
        if settle_source is None:
            continue

        settling = True
        while settling:
            new_sources = flow_sideways(ground_map, settle_source, flowing)

            # if settle_source[Y] > 50:
            #     print_map(ground_map, bounds, flowing=flowing, extras={source: "X", settle_source: "+"})
            #     do_nothing = True

            if len(new_sources) == 0:
                settle_source = (settle_source[X], settle_source[Y] - 1)
            else:
                sources.extend(new_sources)
                settling = False

    return count_water(ground_map, bounds), flowing


def flowable(ground_map, location, flowing):
    return location not in ground_map or \
           (ground_map[location] != CLAY and (location in flowing or ground_map[location] != WATER))


def flow_downwards(ground_map, bounds, source, flowing):

    location = (source[X], source[Y] + 1)

    while flowable(ground_map, location, flowing) and location[Y] <= bounds["y_max"]:
        ground_map[location] = WATER
        flowing.add(location)
        location = (location[X], location[Y] + 1)

    if not in_bounds(bounds, location):
        return None

    else:
        return location[X], location[Y] - 1


def flow_sideways(ground_map, source, flowing):

    new_sources = []

    if source not in ground_map:
        ground_map[source] = WATER
        flowing.add(source)

    left = (source[X] - 1, source[Y])
    right = (source[X] + 1, source[Y])

    spread = set()
    bounded_left = False
    bounded_right = False
    while flowable(ground_map, left, flowing) \
            and not flowable(ground_map, (left[X], left[Y] + 1), flowing):
        spread.add(left)
        ground_map[left] = WATER
        left = (left[X] - 1, left[Y])
    if left in ground_map and ground_map[left] == CLAY:
        bounded_left = True
    else:
        ground_map[left] = WATER
        flowing.add(left)
        new_sources.append(left)

    while flowable(ground_map, right, flowing) \
            and not flowable(ground_map, (right[X], right[Y] + 1), flowing):
        spread.add(right)
        ground_map[right] = WATER
        right = (right[X] + 1, right[Y])
    if right in ground_map and ground_map[right] == CLAY:
        bounded_right = True
    else:
        ground_map[right] = WATER
        flowing.add(right)
        new_sources.append(right)

    if bounded_right and bounded_left:
        spread.add(source)
        for s in spread:
            if s in flowing:
                flowing.remove(s)
    else:
        for s in spread:
            flowing.add(s)

    return new_sources


def count_water(ground_map, bounds):
    return sum([1 if s == WATER else 0 for c, s in ground_map.items() if in_bounds(bounds, c, ignore_x=True)])


#

main()
