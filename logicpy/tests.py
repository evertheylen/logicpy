
import unittest

from logicpy import *

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


class Peano(unittest.TestCase):
    def setUp(self):
        self.u = Universe()
        self.n = self.u.namespace()
        
        self.n.sum[_.zero, _.X, _.X] = True
        self.n.sum[_.s(_.X), _.Y, _.Z] = self.n.sum(_.X, _.s(_.Y), _.Z)
    
    
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


if __name__ == '__main__':
    unittest.main()
