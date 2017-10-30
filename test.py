#!/usr/bin/env python3


import os
from datetime import datetime
from math import inf


class Restructor(object):
    def __init__(self, shell='bash'):
        self.rules = {}

    def add(self, target, prereqs, recipe=None):
        """Need an indirect rule? Just omit the recipe."""
        if target in self.rules:
            raise Exception("Target '{}' already has a rule".format(target))
        self.rules[target] = Rule(target, prereqs, recipe)

    def get_stamp(self, x):
        try:
            return os.stat(x.target).st_mtime
        except FileNotFoundError:
            return -inf

    def get_order(self, target):
        for rule in tuple(self.rules.values()):
            for i, prereq in enumerate(rule.prereqs):
                if isinstance(prereq, str):
                    prereq_name = prereq
                    prereq = self.rules.get(prereq_name)
                    if prereq is None:
                        prereq = self.rules[prereq_name] = Leaf(prereq_name)
                    rule.prereqs[i] = prereq
                prereq.products.add(rule)

        start = self.rules[target]
        order = {}
        frontier = {start}
        visited = set()
        d = 0
        while frontier:
            next_frontier = set()
            for rule in frontier:
                print(" " + repr(rule))
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

    def do(self, target, *, dryrun=True):
        if not dryrun:
            raise Exception("very lazy cat")

        order = self.get_order(target)
        now = datetime.now().timestamp()

        dirty = set()
        for rule in order:
            if rule in dirty or any(
                    self.get_stamp(rule) < self.get_stamp(prereq)
                    for prereq in rule.prereqs
            ):
                print(rule)
                dirty.update(rule.products)


class Node(object):
    def __hash__(self):
        return hash(self.target)

    def __eq__(self, other):
        return self.target == other.target


class Rule(Node):
    def __init__(self, target, prereqs, recipe=None):
        self.target = target
        self.prereqs = list(prereqs)
        self.products = set()  # opposite of prereqs
        self.recipe = recipe

    def __repr__(self):
        return "<" + repr(self.target) + ">"

    def __str__(self):
        return "{} -> {}".format(repr(self.prereqs), repr(self.target))


class Leaf(Node):
    prereqs = ()

    def __init__(self, target):
        self.target = target
        self.products = set()

    def __repr__(self):
        return "<" + repr(self.target) + ">"


GCC1 = 'gcc -std=c99 -pedantic -Wall -Wextra -Werror'


def test_order():
    r = Restructor()
    r.add('c', ('b', 'a'))
    r.add('b', ('a',))
    print(r.get_order('c'))

def test_stat():
    r = Restructor()
    r.add('c', ('b', 'a'))
    r.add('b', ('a',))
    r.do('c')

test_stat()
