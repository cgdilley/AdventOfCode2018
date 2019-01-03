INPUT = "077201"


def main():

    recipes = bake_until_match(INPUT)

    print("The recipe sequence '%s' first appears after %d recipes." %
          (INPUT, recipes.find(INPUT)))


def bake_until_match(pattern: str) -> str:
    recipes = "37"
    elf1 = 0
    elf2 = 1

    while not end_matches_pattern(recipes, pattern):
        recipe1 = int(recipes[elf1])
        recipe2 = int(recipes[elf2])

        score = recipe1 + recipe2
        recipes += str(score)

        count = len(recipes)
        elf1 = (elf1 + 1 + recipe1) % count
        elf2 = (elf2 + 1 + recipe2) % count

        mod = count % 1000000
        if mod == 0 or mod == 1:
            print("Made %d recipes. Last 30: %s" % (count, recipes[-30:]))

    return recipes


def end_matches_pattern(recipes, pattern):
    if len(recipes) < len(pattern):
        return False

    end = recipes[-(len(pattern) + 1):]

    return end.startswith(pattern) or end.endswith(pattern)


#

main()
