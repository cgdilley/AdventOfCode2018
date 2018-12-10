import re

REGEX = re.compile(r".*<\s*([-\d]+),\s*([-\d]+)>.*<\s*([-\d]+),\s*([-\d]+)>")

def main():
    with open("../input/day10.txt", "r") as f:
        lines = f.readlines()

    coords = [read_coord(l.strip()) for l in lines]

    iterate(coords)


def read_coord(line):
    match = REGEX.match(line)
    return {
        "x": int(match.group(1)),
        "y": int(match.group(2)),
        "xv": int(match.group(3)),
        "yv": int(match.group(4))
    }


def iterate(coords):
    for _ in range(100000):
        map_by_col = dict()
        map_by_row = dict()

        for c in coords:
            c["x"] += c["xv"]
            c["y"] += c["yv"]
            if c["x"] not in map_by_col:
                map_by_col[c["x"]] = [c]
            else:
                map_by_col[c["x"]].append(c)
            if c["y"] not in map_by_row:
                map_by_row[c["y"]] = [c]
            else:
                map_by_row[c["y"]].append(c)

        if len(map_by_row.keys()) < 30:
            minx = min(map_by_col.keys())
            maxx = max(map_by_col.keys())
            print_stars(map_by_row, minx, maxx)
            input("Press enter to continue.")
            print("Continuing...")


def print_stars(row_map, minx, maxx):

    stretch = 2
    print("\n")
    for row in sorted(list(row_map.keys())):
        stars = row_map[row]
        output = "_"*stretch*(maxx + 1 - minx)
        for star in stars:
            x = (star["x"] - minx)*stretch
            output = output[:x] + "O"*stretch + output[x+stretch:]

        print(output)
    print()


#

main()
