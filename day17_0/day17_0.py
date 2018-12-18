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


def build_ground_map(lines):

    x_re = re.compile(r"x=(.+?)(,|$)")
    y_re = re.compile(r"y=(.+?)(,|$)")
    ground_map = dict()
    bounds = {
        "x_min": 500,
        "y_min": 0,
        "x_max": 500,
        "y_max": 0
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


def print_map(ground_map, bounds):
    for y in range(bounds["y_min"], bounds["y_max"] + 1):
        line = ""
        for x in range(bounds["x_min"], bounds["x_max"] + 1):
            if (x, y) in ground_map:
                line += {
                    CLAY: "#",
                    WATER: "O",
                    SPRING: "*"
                }[ground_map[(x, y)]]
            else:
                line += "."
        print(line)
    print()

#

main()
