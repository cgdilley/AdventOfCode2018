
with open("../../input/day1.txt") as f:
    lines = f.readlines()

nums = [int(line.strip()[1:]) * (1 if line[0] == "+" else -1) for line in lines]


def hunt(numbers):
    seen = {0}
    sum = 0
    while True:
        for num in numbers:
            sum += num
            if sum in seen:
                return sum
            seen.add(sum)


print("The first duplicate sum = %d" % hunt(nums))
