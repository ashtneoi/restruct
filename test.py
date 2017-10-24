#!/usr/bin/env python3


class Restructor(object):
    def __init__(self):
        self.rules = {}

    def add(self, target, prereqs, recipe):
        self.rules[target] = Rule(target, prereqs, recipe)

    #def add_indirect(self, target, prereqs, recipe):

    def get_order(self, target):
        for rule in self.rules.values():
            for i, prereq in enumerate(rule.prereqs):
                if isinstance(prereq, str):
                    x = self.rules.get(prereq, None)
                    if x is not None:
                        rule.prereqs[i] = x


        start = self.rules[target]
        order = []
        queue = [start]
        visited = set()
        while queue:
            queue2 = []
            for rule in queue:
                if isinstance(rule, str):
                    continue
                if rule not in visited:
                    order.append(rule)
                    queue2.extend(rule.prereqs)
                elif rule is start:
                    raise Exception("Prereq cycle")
            visited.update(queue)
            queue = queue2
        order.reverse()

        return order


class Rule(object):
    def __init__(self, target, prereqs, recipe):
        self.target = target
        self.prereqs = list(prereqs)
        self.recipe = recipe

    def __repr__(self):
        return repr(self.target)

    def __str__(self):
        return "{} -> {}".format(repr(self.prereqs), repr(self.target))


GCC1 = 'gcc -std=c99 -pedantic -Wall -Wextra -Werror'


r = Restructor()
r.add('foo', ('foo.c', 'foo.h'), GCC1 + ' -o foo foo.c')
r.add('foo.h', ('foo.h.in',), 'cp foo.h.in foo.h')
r.add('foo.c', ('foo.h',), '')
#r.add('foo.h.in', ('foo',), 'echo oops')
print(r.get_order('foo'))
