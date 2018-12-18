import re

OP = 0
A = 1
B = 2
C = 3

REGISTERS = re.compile(r"\w+: +\[(\d+), (\d+), (\d+), (\d+)\]")

# noinspection SpellCheckingInspection
OPCODES = ["addr", "addi", "mulr", "muli", "banr", "bani", "borr", "bori", "setr", "seti", "gtir", "gtri",
           "gtrr", "eqir", "eqri", "eqrr"]


def main():
    with open("../input/day16.txt", "r") as f:
        lines = [l.strip() for l in f.readlines()[:3188]]

    samples = read_samples(lines)

    results = test_each_sample(samples)

    print("%d samples conform to 3 or more ops." %
          len(list(filter(lambda r: len(r) >= 3, results))))


def read_samples(lines):
    samples = []
    for row in range(0, len(lines), 4):
        before_match = REGISTERS.match(lines[row])
        after_match = REGISTERS.match(lines[row + 2])
        samples.append({
            "before": [int(before_match.group(i + 1)) for i in range(4)],
            "after": [int(after_match.group(i + 1)) for i in range(4)],
            "command": [int(x) for x in lines[row + 1].split(" ")]
        })
    return samples


def test_each_sample(samples):
    results = []
    for sample in samples:
        suitable = test_opcodes(sample, OPCODES)
        results.append(suitable)
    return results


def test_opcodes(sample, opcodes):
    suitable = set()
    for op in opcodes:
        if is_suitable_op(op, sample):
            suitable.add(op)
    return suitable


# noinspection SpellCheckingInspection
def is_suitable_op(op, sample):
    bef = sample["before"]
    aft = sample["after"]
    com = sample["command"]
    if op == "addr":
        return aft[com[C]] == bef[com[A]] + bef[com[B]]
    elif op == "addi":
        return aft[com[C]] == bef[com[A]] + com[B]
    elif op == "mulr":
        return aft[com[C]] == bef[com[A]] * bef[com[B]]
    elif op == "muli":
        return aft[com[C]] == bef[com[A]] * com[B]
    elif op == "banr":
        return aft[com[C]] == bef[com[A]] & bef[com[B]]
    elif op == "bani":
        return aft[com[C]] == bef[com[A]] & com[B]
    elif op == "borr":
        return aft[com[C]] == bef[com[A]] | bef[com[B]]
    elif op == "bori":
        return aft[com[C]] == bef[com[A]] | com[B]
    elif op == "setr":
        return aft[com[C]] == bef[com[A]]
    elif op == "seti":
        return aft[com[C]] == com[A]
    elif op == "gtir":
        return aft[com[C]] == (1 if com[A] > bef[com[B]] else 0)
    elif op == "gtri":
        return aft[com[C]] == (1 if bef[com[A]] > com[B] else 0)
    elif op == "gtrr":
        return aft[com[C]] == (1 if bef[com[A]] > bef[com[B]] else 0)
    elif op == "eqir":
        return aft[com[C]] == (1 if com[A] == bef[com[B]] else 0)
    elif op == "eqri":
        return aft[com[C]] == (1 if bef[com[A]] == com[B] else 0)
    elif op == "eqrr":
        return aft[com[C]] == (1 if bef[com[A]] == bef[com[B]] else 0)
    else:
        raise Exception("lolwut")


#

main()
