
import random

from logicpy.data import with_scope, occurences, has_occurence

class Structure:
    # builtin operators, see below
    
    def occurences(self, O):
        pass
    
    def __and__(self, other):
        from logicpy.builtin import and_
        return and_(self, other)
    
    def __or__(self, other):
        from logicpy.builtin import or_
        return or_(self, other)
    
    def with_scope(self, scope):
        return self
    
    @staticmethod
    def scope_id():
        return random.getrandbits(64)


class MultiArg(Structure):
    def __init__(self, *args):
        self.args = args
    
    def __str__(self):
        return '(' + f" {self.op} ".join(map(str, self.args)) + ')'
        
    def __repr__(self):
        return type(self).__name__ + '(' + ', '.join(map(repr, self.args)) + ')'
        
    def with_scope(self, scope):
        args = [with_scope(a, scope) for a in self.args]
        return type(self)(*args)
    
    def occurences(self, O):
        for a in self.args:
            occurences(a, O)
    
    def has_occurence(self, var):
        return any(has_occurence(a, var) for a in self.args)


class BinaryArg(MultiArg):
    def __init__(self, left, right):
        self.left = left
        self.right = right
