#!/usr/bin/env python3


class Restructor(object):
    def __init__(self):
        self.rules = {}

    def add(self, target, prereqs, recipe=None):
        """Need an indirect rule? Just give an empty recipe."""
        if target in self.rules:
            raise Exception("Target '{}' already has a rule".format(target))
        self.rules[target] = Rule(target, prereqs, recipe)

    def get_order(self, target):
        for rule in self.rules.values():
            for i, prereq in enumerate(rule.prereqs):
                if isinstance(prereq, str):
                    x = self.rules.get(prereq, None)
                    if x is not None:
                        rule.prereqs[i] = x

        start = self.rules[target]
        order = {}
        frontier = {start}
        visited = set()
        d = 0
        while frontier:
            next_frontier = set()
            for rule in frontier:
                print(" " + repr(rule))
                if isinstance(rule, str):
                    order[rule] = d
                else:
                    if rule not in visited:
                        order[rule] = d
                        next_frontier.update(rule.prereqs)
                    elif rule is start:
                        raise Exception("Prereq cycle")
            visited.update(frontier)
            frontier = next_frontier
            d += 1
        order = [
            x[0]
            for x in sorted(order.items(), key=(lambda x: x[1]), reverse=True)
        ]

        return order


class Rule(object):
    def __init__(self, target, prereqs, recipe=None):
        self.target = target
        self.prereqs = list(prereqs)
        self.recipe = recipe

    def __repr__(self):
        return "<" + repr(self.target) + ">"

    def __str__(self):
        return "{} -> {}".format(repr(self.prereqs), repr(self.target))


GCC1 = 'gcc -std=c99 -pedantic -Wall -Wextra -Werror'


r = Restructor()
r.add('c', ('b', 'a'))
r.add('b', ('a',))
print(r.get_order('c'))
