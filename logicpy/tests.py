
import unittest

from logicpy import *

class UniverseAndNamespace(unittest.TestCase):
    def setUp(self):
        self.u = Universe()
        self.n = self.u.namespace()
        self.setup_universe(self.u, self.n)


class Various(unittest.TestCase):
    def test_family(self):
        u, n = Universe().and_namespace()
        
        n.parent[_.alice, _.bob] = True
        n.parent[_.alice, _.charlie] = True
        n.sibling[_.X, _.Y] = n.parent(_.P, _.X) & n.parent(_.P, _.Y)
        
        expected = [
            {'U': _.bob, 'V': _.bob},
            {'U': _.bob, 'V': _.charlie},
            {'U': _.charlie, 'V': _.bob},
            {'U': _.charlie, 'V': _.charlie}
        ]
        
        res = u.simple_query(n.sibling(_.U, _.V))
        self.assertEqual(res, expected)


def peano(x):
    if x == 0: return _.zero
    return _.s(peano(x-1))


def inv_peano(x):
    if x == _.zero: return 0
    return 1 + inv_peano(x.children[0])


class Peano(UniverseAndNamespace):
    def setup_universe(self, u, n):
        n.sum[_.zero, _.X, _.X] = True
        n.sum[_.s(_.X), _.Y, _.Z] = n.sum(_.X, _.s(_.Y), _.Z)
    
    def do_sum(self, a, b):
        res = self.u.simple_query(self.n.sum(peano(a), peano(b), _.X))
        total = inv_peano(res[0]['X'])
        self.assertEqual(total, a+b)
    
    def test_base(self):
        self.do_sum(0, 5)
    
    def test_easy(self):
        self.do_sum(1, 1)
    
    def test_full_accumulate(self):
        self.do_sum(7, 0)
    
    def test_whatever(self):
        self.do_sum(4, 7)


def fib(x):
    return {0: 1, 1: 2}.get(x) or fib(x-1) + fib(x-2)


class Fibonacci(UniverseAndNamespace):
    def setup_universe(self, u, n):
        n.fib[0, 1] = True
        n.fib[1, 2] = True
        n.fib[_.N, _.Res] = and_(
            _.N > 1,
            _.N1 << _.N - 1,
            _.N2 << _.N - 2,
            n.fib(_.N1, _.Res1),
            n.fib(_.N2, _.Res2),
            _.Res << _.Res1 + _.Res2)

    def do_fib(self, x):
        res = self.u.simple_query(self.n.fib(x, _.X))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['X'], fib(x))
    
    def test_basecases(self):
        self.do_fib(0)
        self.do_fib(1)
    
    def test_second(self):
        self.do_fib(2)
    
    def test_lots(self):
        for i in range(3, 7):
            self.do_fib(i)


node = _.node
empty = _.empty

class BalancedTrees(UniverseAndNamespace):
    @classmethod
    def print_tree(cls, tree, level=0):
        if tree.name == 'node':
            l, val, r = tree.children
            print(("  " * level) + str(val))
            cls.print_tree(l, level+1)
            cls.print_tree(r, level+1)
    
    def setup_universe(self, u, n):
        n.depth[empty, 0] = True
        n.depth[node(_.L, _, _.R), _.MaxDepth] = and_(
            n.depth(_.L, _.Ld),
            n.depth(_.R, _.Rd),
            _.MaxDepth << 1 + max_(_.Ld, _.Rd))
        
        n.balanced[empty] = True
        n.balanced[node(_.L, _, _.R)] = and_(
            n.balanced(_.L),
            n.balanced(_.R),
            n.depth(_.L, _.Ld),
            n.depth(_.R, _.Rd),
            1 >= abs_(_.Ld - _.Rd))
        
        n.add_to[empty, _.El, node(empty, _.El, empty)] = True
        
        n.add_to[node(_.L, _.V, _.R), _.El, node(_.AddedLeft, _.V, _.R)] = and_(
            n.depth(_.L, _.Ld),
            n.depth(_.R, _.Rd),
            _.Ld <= _.Rd,
            n.add_to(_.L, _.El, _.AddedLeft))
        
        n.add_to[node(_.L, _.V, _.R), _.El, node(_.L, _.V, _.AddedRight)] = and_(
            n.depth(_.L, _.Ld),
            n.depth(_.R, _.Rd),
            _.Ld > _.Rd,
            n.add_to(_.R, _.El, _.AddedRight))
    
    def test_add(self):
        inp = node(empty,3,node(empty,4,node(empty,2,empty)))
        out = node(node(empty,7,empty),3,node(empty,4,node(empty,2,empty)))
        res = self.u.simple_query(self.n.add_to(node(empty,3,node(empty,4,node(empty,2,empty))), 7, _.X))[0]['X']
        self.assertEqual(inp, out)


if __name__ == '__main__':
    unittest.main()
