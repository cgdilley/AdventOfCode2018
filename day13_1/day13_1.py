# Some constants for readability

# Directions are numbered in clockwise order.  Incrementing a direction (mod 4)
# indicates a clockwise turn, and conversely decrementing a direction (mod 4)
# indicates a counterclockwise turn.
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

# The turning instructions, in order.  After one is reached, the turn instruction
# can be incremented by one (and modded by 3) to get the next turn instruction.
TURN_LEFT = 0
GO_STRAIGHT = 1
TURN_RIGHT = 2


def main():
    with open("../input/day13.txt", "r") as f:
        # Strip newlines
        contents = [line[:-1] for line in f.readlines()]

    # Load the map
    carts, tracks = load_map(contents)

    last_cart = run(carts, tracks)[0]

    print("The last cart standing is: %s" % str(last_cart))


def load_map(contents):
    """
    Loads the map containing all carts and tracks from the given list of input lines.
    Returns both a list of cart objects and a dictionary of all track segments.

    Cart objects are represented by a dictionary structured as follows:
    {
        "x": 0,                 # The X coord
        "y": 0,                 # The Y coord
        "id": 0,                # The unique cart ID
        "dir": LEFT,            # The cart's current direction
        "next_turn": TURN_LEFT  # The next turn instruction to execute upon reaching an intersection
    }

    The tracks dictionary simply maps a tuple of coordinates to the symbol representing the track
    segment at those coordinates.  Eg:
    {
        (0, 0): "/",
        (0, 1): "|",
        (0, 2): "+",
        ...
    }

    :param contents: A list of strings representing the map to load
    :return: A tuple containing a list of cart objects and a dictionary of
    all track segments.
    """
    carts = []
    tracks = {"_width": len(contents[0]), "_height": len(contents)}
    cart_id = 0

    for y, line in enumerate(contents):
        # Keep track of the width and height of the board.  This is relevant for two things:
        # Makes sorting carts by (x,y) coordinates easier, and helps format output
        # in print_map()
        if len(line) > tracks["_width"]:
            tracks["_width"] = len(line)

        # Iterate through all characters in the line, ignoring spaces
        for x, char in enumerate(line):
            if char == " ":
                continue

            # If this space indicates a cart, add it to the carts list and infer
            # the track that is beneath it
            if char in ["<", ">", "^", "v"]:
                direction = parse_cart_direction(char)
                carts.append({
                    "id": cart_id,
                    "dir": direction,
                    "x": x,
                    "y": y,
                    "next_turn": TURN_LEFT
                })
                cart_id += 1
                tracks[(x, y)] = "-" if direction in [LEFT, RIGHT] else "|"

            # Otherwise just add the track
            else:
                tracks[(x, y)] = char
    return carts, tracks


def parse_cart_direction(char):
    """
    Converts a cart character (<>v^) into the corresponding direction identifier

    :param char: The character to convert
    :return: An integer value corresponding to a direction constant
    """
    return {
        "<": LEFT,
        ">": RIGHT,
        "^": UP,
        "v": DOWN
    }[char]


def process_tick(carts, tracks):
    """
    Updates all carts in the defined left->right, top->bottom order, moving them along the
    track and turning them if necessary.  Any collisions that occur mid-tick are collected
    in a list and returned.

    :param carts: The carts to process
    :param tracks: The tracks that the carts follow
    :return: A list of coordinates of any collisions that occurred mid-tick
    """
    cart_order = sorted(carts, key=lambda x: x["x"] + (x["y"] * tracks["_width"]))
    collisions = {}

    for cart in cart_order:
        if cart["id"] in collisions:
            continue

        # Move the cart
        move(cart)
        # Get the track segment under the card and turn it as necessary
        track_segment = tracks[(cart["x"], cart["y"])]
        process_track(cart, track_segment)

        # Check for any collisions.  Collisions may occur mid-tick with carts that haven't moved yet,
        # so this has to be checked after every move
        for other_cart in carts:
            if cart["x"] == other_cart["x"] and cart["y"] == other_cart["y"] and cart["id"] != other_cart["id"]:
                collisions[cart["id"]] = (cart["x"], cart["y"])
                collisions[other_cart["id"]] = (cart["x"], cart["y"])

    return collisions


def run(carts, tracks):
    """
    Repeated process ticks of movement until a collision occurs, then return the first collision

    :param carts: The carts to process
    :param tracks: The tracks that the carts follow
    :return: The coordinate location of the first collision
    """
    tick = 0
    while True:
        collisions = process_tick(carts, tracks)
        # print_map(carts, tracks)
        if len(collisions) > 0:
            carts = [c for c in carts if c["id"] not in collisions]

            print("Collisions occurred!  %d carts removed, %d remain." % (len(collisions), len(carts)))
            if len(carts) <= 1:
                return carts
        tick += 1


def move(cart):
    """
    Moves the cart one space based on its current direction

    :param cart: The card to move
    :return: None
    """
    if cart["dir"] == LEFT:
        cart["x"] -= 1
    elif cart["dir"] == RIGHT:
        cart["x"] += 1
    elif cart["dir"] == UP:
        cart["y"] -= 1
    elif cart["dir"] == DOWN:
        cart["y"] += 1


def process_track(cart, track_segment):
    """
    Updates the direction of the cart based on the track segment that is beneath it.

    :param cart: The cart to update
    :param track_segment: The track segment it is on
    :return: None
    """
    # Reached a corner, turn appropriately
    if track_segment == "/":
        if cart["dir"] == LEFT or cart["dir"] == RIGHT:
            turn(cart, TURN_LEFT)
        else:
            turn(cart, TURN_RIGHT)
    # Reached a different corner, turn appropriately
    elif track_segment == "\\":
        if cart["dir"] == LEFT or cart["dir"] == RIGHT:
            turn(cart, TURN_RIGHT)
        else:
            turn(cart, TURN_LEFT)
    # Reached an intersection, follow its turn instructions and then update
    # its turn instructions
    elif track_segment == "+":
        turn(cart, cart["next_turn"])
        cart["next_turn"] = (cart["next_turn"] + 1) % 3

    # If on a straight piece of track, make sure something didn't get screwed up
    # (probably an unnecessary, paranoid check)
    elif track_segment == "|":
        if cart["dir"] != DOWN and cart["dir"] != UP:
            raise Exception("Something went wrong on the tracks.")
    elif track_segment == "-":
        if cart["dir"] != LEFT and cart["dir"] != RIGHT:
            raise Exception("Something went wrong on the tracks.")


def turn(cart, turn_type):
    """
    Update the cart's direction by following the given turn instruction

    :param cart: The cart to turn
    :param turn_type: The turn instruction (TURN_LEFT, TURN_RIGHT, GO_STRAIGHT)
    :return: None
    """
    if turn_type == TURN_LEFT:
        cart["dir"] = (cart["dir"] - 1) % 4
    elif turn_type == TURN_RIGHT:
        cart["dir"] = (cart["dir"] + 1) % 4
    elif turn_type == GO_STRAIGHT:
        pass


def print_map(carts, tracks):
    """
    Prints the current board state to console

    :param carts: The carts
    :param tracks: The tracks
    :return: None
    """
    board = [" " * tracks["_width"] for _ in range(tracks["_height"])]

    for coord, track in tracks.items():
        if len(coord) == 2:
            board[coord[1]] = board[coord[1]][:coord[0]] + track + board[coord[1]][coord[0] + 1:]

    for cart in carts:
        symbol = {
            LEFT: "<",
            RIGHT: ">",
            UP: "^",
            DOWN: "v"
        }[cart["dir"]]
        board[cart["y"]] = board[cart["y"]][:cart["x"]] + symbol + board[cart["y"]][cart["x"] + 1:]

    print("\n".join(board))
    print()


#

#

main()
