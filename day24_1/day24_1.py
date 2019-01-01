import re
import math

GROUP_REGEX = re.compile(r"^(\d+) units each with (\d+) hit points (\(.+\) )?with an attack that "
                         r"does (\d+) ([^\s]+) damage at initiative (\d+)$")
EFFECTIVENESS_REGEX = re.compile(r"^(weak|immune) to ([^;]+)$")


def main():
    with open("../input/day24.txt", "r") as f:
        lines = [l.strip() for l in f.readlines()]

    immune, infect = parse_groups(lines)

    print_groups(immune, infect)
    print()

    # I ran a binary search on different boost values until I came into this area.
    # At 40/41 it reached an unresolveable battle state... the last remaining
    # groups couldn't deal enough damage to one another to actually kill any
    # units.  So I started just manually testing values until I got an answer

    boost = 42
    state = conduct_battle(immune, infect, boost=boost)
    # boost, state = search_minimum_boost(immune, infect)
    remaining_groups = state["immune"] + state["infect"]

    print("%s wins after %d rounds, with %d units remaining (in %d groups).  "
          "The immune system had a boost of %d." %
          (remaining_groups[0].side,
           state["rounds"],
           sum(u.count for u in remaining_groups),
           len(remaining_groups),
           boost))


def print_groups(immune: list, infect: list) -> None:
    print("IMMUNE:\n%s\n\nINFECT:\n%s" %
          ("\n".join([str(i) for i in immune]), "\n".join([str(i) for i in infect])))


def parse_groups(lines: list) -> (list, list):
    """
    Reads through the input lines, parsing the groups that belong to the immune
    system and the infection, and returning the parsed groups as two separate
    lists.

    :param lines: The input lines to process
    :return: A tuple containing two lists: The first one containing the Groups
    belonging to the immune system, the second one containing the Groups belonging
    to the infection.
    """
    immune = []
    infect = []
    mode = "IMMUNE"
    for line in lines:
        if line.startswith("Immune"):
            mode = "IMMUNE"
        elif line.startswith("Infection"):
            mode = "INFECT"
        elif len(line) > 1:
            g = Group.parse(line, mode)
            if mode == "IMMUNE":
                immune.append(g)
            else:
                infect.append(g)

    return immune, infect


def search_minimum_boost(immune, infect) -> (int, dict):
    """
    Conducts a binary search of boost values that results in the closest possible immune
    system victory.  Some boost values might result in infinite battles, so this
    should probably be accounted for if I cared more.
    :param immune: The immune system groups
    :param infect: The infection groups
    :return: A tuple containing 2 values: The lowest boost amount that results in an immune
    system victory, and the battle state resulting from conducting the battle at that boost level.
    """
    lower = 0
    upper = 1000
    mid = math.ceil((upper + lower) / 2)

    while mid != upper:
        b_state = conduct_battle([i.copy() for i in immune], [i.copy() for i in infect], boost=mid)
        if len(b_state["immune"]) > 0:
            upper = mid
        else:
            lower = mid
        mid = math.ceil((upper + lower) / 2)

    return mid, conduct_battle([i.copy() for i in immune], [i.copy() for i in infect], boost=mid)


def conduct_battle(immune: list, infect: list, boost: int = 0) -> dict:
    """
    Conducts the battle between the given immune system and infection groups with the given
    immune system boost.  Continues to perform each round of combat repeatedly until all units
    from one side have been eliminated.

    :param immune: The immune system groups
    :param infect: The infection groups
    :param boost: The amount to boost the immune system by
    :return: The battle state that results from conducting the battle
    """
    battle_state = {
        "immune": immune,
        "infect": infect,
        "rounds": 0
    }
    while len(immune) > 0 and len(infect) > 0:
        battle_state["rounds"] += 1
        # print("Round %d, FIGHT!" % battle_state["rounds"])
        perform_round(battle_state, boost)

    return battle_state


def perform_round(battle_state: dict, boost: int = 0) -> None:
    """
    Performs a single round of combat, involving combat select, attacking,
    and clean-up of dead groups.  Updates the given battle state in-place.
    :param battle_state: The battle state to update with a single round of combat
    :param boost: The amount to boost the immune system by
    :return: None
    """
    targeting = select_targets(battle_state, boost)
    perform_attacks(targeting, boost)
    clean_up_dead(battle_state)


def select_targets(battle_state: dict, boost: int = 0) -> dict:
    """
    Follows the specified rules to systematically choose targets for all attacking
    groups.
    :param battle_state: The battle state
    :param boost: The amount to boost the immune system by
    :return: The targeting dictionary resulting from this target selection process.
    Keys represent targets, and values are the groups attacking those targets this round.
    """
    targeting = dict()
    immune = battle_state["immune"]
    infect = battle_state["infect"]

    # Sort all units by effective power (accounting for immune system boost), breaking
    # ties with initiative
    all_units = immune + infect
    all_units = sorted(all_units,
                       key=lambda g: g.effective_power(boost) * 100 + g.initiative,
                       reverse=True)

    # Iterate through all units in the sorted order
    for unit in all_units:
        # Calculate the effective power of this unit
        power = unit.effective_power(boost)
        max_damage = 0
        target = None

        # Iterate through all available attackable targets for this unit
        options = immune if unit.side == "INFECT" else infect
        for t in options:

            # If this potential target has already been selected as a target by a different
            # group, ignore it
            if t in targeting:
                continue

            # Calculate the damage that this unit would do to this potential target, and keep
            # track of which target this unit would deal the most damage (breaking ties
            # with the target's effective power, and breaking those ties with initiative)
            # Targets that would take 0 damage are ignored and not selected, even if it is the
            # maximum value.
            damage = t.effective_damage_taken(power, unit.atk_type)
            if damage > max_damage:
                max_damage = damage
                target = t
            elif damage == max_damage and damage > 0:
                max_power = target.effective_power(boost)
                t_power = t.effective_power(boost)
                if max_power < t_power or \
                        (max_power == t_power and t.initiative > target.initiative):
                    target = t

        # If a target was selected for this unit to attack, mark it in the targeting dictionary
        if target is not None:
            targeting[target] = unit

    # Return the targeting results
    return targeting


def perform_attacks(targeting: dict, boost: int = 0) -> None:
    """
    Performs all attacks based on the given targeting dictionary as generated by
    select_targets(), mapping targets to their attackers.
    Updates the Groups in the targeting dictionary in-place.

    :param targeting: The targeting dictionary
    :param boost: The immune system boost to apply
    :return: None
    """

    # Swap the keys and values of the targeting dictionary to map attackers to targets
    attacking = {attacker: target for target, attacker in targeting.items()}

    # Sort attackers by initiative order
    order = sorted(attacking.keys(), key=lambda g: g.initiative, reverse=True)

    # Conduct each attack in order
    for attacker in order:

        # If an attacker was killed by a group with higher initiative, don't perform
        # its attack
        if attacker.is_dead():
            continue

        # Have the attacker attack the target!
        target = attacking[attacker]
        attacker.attack(target, boost)


def clean_up_dead(battle_state: dict) -> None:
    """
    Removes all dead groups from the battle state
    :param battle_state: The battle state to update in-place
    :return: None
    """
    for side in ["immune", "infect"]:
        pos = 0
        while pos < len(battle_state[side]):
            if battle_state[side][pos].is_dead():
                del battle_state[side][pos]
            else:
                pos += 1


class Group:
    def __init__(self, count: int, hp: int, weaknesses: iter, immunities: iter,
                 atk_damage: int, atk_type: str, initiative: int, side: str):
        self.count = count
        self.hp = hp
        self.weaknesses = set(weaknesses)
        self.immunities = set(immunities)
        self.atk_damage = atk_damage
        self.atk_type = atk_type
        self.initiative = initiative
        self.side = side

    def __str__(self):
        return "[%s] %d units each with %d hit points (weak: [%s]; immune: [%s]) with an attack that does " \
               "%d %s damage at initiative %d" % \
               (self.side, self.count, self.hp,
                ", ".join(self.weaknesses), ", ".join(self.immunities),
                self.atk_damage, self.atk_type, self.initiative)

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(self.initiative)

    def effective_power(self, boost: int = 0) -> int:
        """
        Calculates the effective power of this Group, factoring in the immune system boost
        if this is an immune system Group
        :param boost: The immune system boost to apply, if any
        :return: The effective power of this Group
        """
        boost = boost if self.side == "IMMUNE" else 0
        return self.count * (self.atk_damage + boost)

    def take_damage(self, amount: int, atk_type: str) -> None:
        """
        Deals the given amount of damage to this unit based on the given attack type,
        killing the appropriate amount of units in this group as a result.

        :param amount: The base amount of damage to deal, before applying weaknesses
        and immunities
        :param atk_type: The attack type of the attack being performed
        :return: None
        """
        amount = self.effective_damage_taken(amount, atk_type)

        killed = math.floor(amount / self.hp)
        self.count -= killed

    def attack(self, target, boost: int = 0) -> None:
        """
        Causes this Group to attack the given Group, dealing damage to it.
        :param target: The target Group to attack
        :param boost: The immune system boost to apply
        :return: None
        """
        # Calculate this Group's effective power and have the target
        # take that much damage (modified by this Group's attack type)
        target.take_damage(self.effective_power(boost), self.atk_type)

    def effective_damage_taken(self, power: int, atk_type: str) -> int:
        """
        Calculates how much damage this Group would take if the given attack power
        with the given attack type attacked this Group.
        :param power: The base attack power of the attack
        :param atk_type: The attack type
        :return: The amount of damage this Group would take were the described attack
        were to take place.
        """
        if atk_type in self.immunities:
            return 0
        elif atk_type in self.weaknesses:
            return power * 2
        else:
            return power

    def is_dead(self) -> bool:
        """
        Determines whether or not this Group is considered dead.
        :return: True if this Group is dead, false otherwise.
        """
        return self.count <= 0

    def copy(self):
        return Group(self.count, self.hp, [w for w in self.weaknesses],
                     [i for i in self.immunities], self.atk_damage,
                     self.atk_type, self.initiative, self.side)

    @staticmethod
    def parse(line, side):
        """
        Reads a line of input, parsing it and returning a Group object
        that represents the input line.

        :param line: The line of input to parse
        :param side: The side that the group belongs to ("IMMUNE" or "INFECT")
        :return: The newly-constructed Group
        """
        # Perform the base regex matching
        m = GROUP_REGEX.match(line)

        weaknesses = []
        immunities = []

        # Pull out the text that describes weaknesses and immunities for the Group, if any
        effects_group = m.group(3)
        if effects_group is not None and len(effects_group) > 0:
            # Remove extra characters from ends of the text, and then split by semicolon.
            # The semicolon splits descriptions of weaknesses and immunities if the Group
            # has both.
            effects = [e.strip() for e in effects_group[1:-2].split(";")]

            # Parse the split segments to identify whether segment describes a weakness or
            # immunity, and then parse the comma-separated list of attack types
            for fx in effects:
                em = EFFECTIVENESS_REGEX.match(fx)
                types = [t.strip() for t in em.group(2).split(",")]
                if em.group(1) == "weak":
                    weaknesses.extend(types)
                else:
                    immunities.extend(types)

        # Construct the group based on the information parsed, including the weaknesses
        # and immunities
        return Group(int(m.group(1)),
                     int(m.group(2)),
                     weaknesses,
                     immunities,
                     int(m.group(4)),
                     m.group(5),
                     int(m.group(6)),
                     side)


#

main()
