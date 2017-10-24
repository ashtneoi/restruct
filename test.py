#!/usr/bin/env python3


class Restructor(object):
    def __init__(self):
        self.rules = {}

    def __str__(self):
        return "\n".join(repr(rule) for rule in self.rules.values())

    def add(self, target, prereqs, recipe):
        self.rules[target] = Rule(target, prereqs, recipe)

    def do(self, target):
        for rule in self.rules.values():
            for i, prereq in enumerate(rule.prereqs):
                if isinstance(prereq, str):
                    x = self.rules.get(prereq, None)
                    if x is not None:
                        print(x)
                        rule.prereqs[i] = x
        raise Exception("lazy cat")


class Rule(object):
    def __init__(self, target, prereqs, recipe):
        self.target = target
        self.prereqs = list(prereqs)
        self.recipe = recipe

    def __repr__(self):
        return "{} -> {}".format(repr(self.prereqs), self.target)


GCC1 = 'gcc -std=c99 -pedantic -Wall -Wextra -Werror'


r = Restructor()
r.add('foo', ('foo.c', 'foo.h'), GCC1 + ' -o foo foo.c')
r.add('foo.h', ('foo.h.in',), 'cp foo.h.in foo.h')
print(r)
try:
    r.do('hey')
except: pass
print(r)
