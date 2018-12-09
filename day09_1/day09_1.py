import re


def main():
    with open("../input/day9.txt", "r") as f:
        info = f.read()
    match = re.match(r'(\d+)[^\d]+(\d+)', info)
    players = int(match.group(1))
    marbles = (int(match.group(2)) * 100) + 1

    results = play_game(players, marbles)

    high_score = max(results.values())

    print("The high score is: %d" % high_score)


class Node:
    def __init__(self, v, prev, next):
        self.v = v
        self.prev = prev
        self.next = next


class LinkedList:
    def __init__(self):
        self.curr = None
        self.size = 0

    def move(self, shift):
        if self.curr is not None:
            if shift < 0:
                for i in range(0, -shift):
                    self.curr = self.curr.prev
            elif shift > 0:
                for i in range(0, shift):
                    self.curr = self.curr.next
        return self

    def pop(self):
        if self.size == 0:
            return None
        if self.size == 1:
            temp = self.curr
            self.curr = None
            self.size = 0
            return temp

        temp = self.curr
        self.curr.prev.next = self.curr.next
        self.curr.next.prev = self.curr.prev
        self.curr = self.curr.next
        self.size -= 1
        return temp

    def push(self, v):
        self.size += 1
        if self.curr is None:
            self.curr = Node(v, None, None)
            self.curr.prev = self.curr
            self.curr.next = self.curr
        else:
            n = Node(v, self.curr.prev, self.curr)
            self.curr.prev.next = n
            self.curr.prev = n
            self.curr = n


def play_game(players, marbles):
    game_state = LinkedList()
    scores = {p: 0 for p in range(players)}
    curr_player = 0

    for marble in range(marbles):

        if is_scoring_marble(marble):
            popped = game_state.move(-7).pop()
            score = marble + popped.v
            scores[curr_player] += score
        else:
            game_state.move(2).push(marble)

        curr_player += 1
        if curr_player >= players:
            curr_player = 0

        if marble % 100000 == 0:
            print("Played marble %d..." % marble)

    return scores


def is_scoring_marble(marble):
    return marble % 23 == 0 and marble != 0


main()
