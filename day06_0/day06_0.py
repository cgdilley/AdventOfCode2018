import re

COORD = re.compile(r'(\d+), (\d+)')


def main():
    with open("../input/day6.txt") as f:
        lines = [read_coord(l) for l in f.readlines()]

    limits = find_limits(lines)
    bounds = build_bounds(lines, limits)

    print_bounds(lines, bounds, limits)

    count = count_bounds_sizes(bounds, limits)

    biggest = max(count.values())

    print("The biggest area is: %d" % biggest)


def read_coord(s):
    match = COORD.match(s)
    return int(match.group(1)), int(match.group(2))


def build_bounds(coords, limits):
    
    ownership = dict()
    for x in range(limits["left"], limits["right"] + 1):
        for y in range(limits["top"], limits["bottom"] + 1):
            min_dist = -1
            min_id = -1
            for i in range(len(coords)):
                coord = coords[i]
                dist = abs(coord[0] - x) + abs(coord[1] - y)
                if min_dist < 0 or dist < min_dist:
                    min_dist = dist
                    min_id = i
                elif min_dist == dist:
                    min_id = -1
            ownership[(x, y)] = min_id
            
    return ownership
                               

# def build_bounds(coords, limits):
#     considered = set(coords)
#     ownership = dict()
# 
#     dist = 0
# 
#     while len(considered) > 0 and dist < 1000:
#         to_add_ownership = {}
# 
#         for i in range(len(coords)):
#             coord = coords[i]
# 
#             box = find_box_around_coord(coord, dist)
#             for b in box:
#                 if not is_within_limits(b, limits):
#                     if coord in considered:
#                         considered.remove(coord)
#                     continue
# 
#                 if b in to_add_ownership:
#                     to_add_ownership[b].append(i)
#                 else:
#                     to_add_ownership[b] = [i]
# 
#         expanded = set()
#         for coord, items in to_add_ownership.items():
#             if coord not in ownership:
#                 if len(items) == 1:
#                     ownership[coord] = items[0]
#                     expanded.add(coords[items[0]])
#                 else:
#                     ownership[coord] = -1
# 
#         considered = considered.intersection(expanded)
#         dist += 1
# 
#     return ownership


def count_bounds_sizes(ownership, limits):
    count = dict()
    for owner in ownership.values():
        if owner < 0:
            continue
        if owner not in count:
            count[owner] = 1
        else:
            count[owner] += 1

    edges = draw_box(limits["left"], limits["right"], limits["top"], limits["bottom"])
    for edge_coord in edges:
        if ownership[edge_coord] in count:
            del count[ownership[edge_coord]]

    return count


def print_bounds(coords, ownership, limits):
    names = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for y in range(limits["top"], limits["bottom"] + 1):
        s = ""
        for x in range(limits["left"], limits["right"] + 1):
            if (x, y) not in ownership:
                s += " "
            elif ownership[(x, y)] < 0:
                s += "."
            elif coords[ownership[(x, y)]] == (x, y):
                s += "°"
            else:
                s += names[ownership[(x, y)]]
        print(s)


def find_limits(coords):
    limits = dict()
    for coord in coords:
        if "left" not in limits or coord[0] < limits["left"]:
            limits["left"] = coord[0]
        if "right" not in limits or coord[0] > limits["right"]:
            limits["right"] = coord[0]
        if "top" not in limits or coord[1] < limits["top"]:
            limits["top"] = coord[1]
        if "bottom" not in limits or coord[1] > limits["bottom"]:
            limits["bottom"] = coord[1]

    return limits


def is_within_limits(coord, limits):
    return limits["left"] <= coord[0] <= limits["right"] and \
           limits["top"] <= coord[1] <= limits["bottom"]


def find_box_around_coord(coord, dist):
    return draw_box(coord[0] - dist, coord[0] + dist, coord[1] - dist, coord[1] + dist)
    

def draw_box(left, right, top, bottom):
    box_coords = set()
    
    for x in range(left, right + 1):
        for y in [top, bottom]:
            box_coords.add((x, y))
    for x in [left, right]:
        for y in range(top, bottom + 1):
            box_coords.add((x, y))

    return box_coords


main()
