INPUT = 77201


def main():

    count = 10

    recipes = bake_until_limit(INPUT + count)

    print("The next %d recipes after the first %d is: %s" %
          (count, INPUT, "".join([str(d) for d in recipes[INPUT:INPUT + 10]])))


def bake_until_limit(limit: int) -> list:
    recipes = [3, 7]
    elf1 = 0
    elf2 = 1

    while len(recipes) < limit:
        recipe1 = recipes[elf1]
        recipe2 = recipes[elf2]

        score = recipe1 + recipe2
        new_recipes = [int(digit) for digit in str(score)]

        recipes.extend(new_recipes)

        elf1 = (elf1 + 1 + recipe1) % len(recipes)
        elf2 = (elf2 + 1 + recipe2) % len(recipes)

    return recipes


#

main()
