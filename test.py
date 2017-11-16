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
            for node in frontier:
                order[node] = max(d, order.get(node, -1))
                next_frontier.update(node.prereqs)
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

        for rule in order:
            rule.stamp = self.get_stamp(rule)
            rule.thresh = max(rule.stamp, max(
                (prereq.stamp for prereq in rule.prereqs), default=-inf
            ))
            print(rule.target, rule.stamp, rule.thresh)
        todo_rev = []
        order[-1].need = True
        for rule in reversed(order):
            if rule.need and (rule.stamp < rule.thresh or rule.stamp == -inf):
                todo_rev.append(rule)
                for prereq in rule.prereqs:
                    prereq.need = True

        todo = reversed(todo_rev)

        print(tuple(todo))
        #for rule in todo:
            #rule.do()


class Node(object):
    need = False

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



def test_stat():
    r = Restructor()
    r.add('c', ('b', 'a'))
    r.add('b', ('a',))
    print('a:', r.get_order('a'))
    print('b:', r.get_order('b'))
    print('c:', r.get_order('c'))
    r.do('c')

test_stat()
