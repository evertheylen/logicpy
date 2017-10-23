
from logicpy.structure import Structure, MultiArg
from logicpy.data import Variable, BasicTerm


class TrueCls(Structure):
    def prove(self, bindings):
        yield bindings

    __repr__ = __str__ = lambda s: "True"

True_ = TrueCls()


class FailCls(Structure):
    def prove(self, bindings):
        return
        yield
    
    __repr__ = __str__ = lambda s: "Fail"

Fail = FailCls()


class and_(MultiArg):
    op = '&'
    
    def __and__(self, other):
        self.args = self.args + (other,)
        return self
    
    def prove(self, bindings):
        # Backtracking implementation!
        return self.prove_arg(0, bindings)
    
    def prove_arg(self, n, bindings):
        if n >= len(self.args):
            yield bindings
            return
        
        arg = self.args[n]
        for new_binding in arg.prove(bindings):
            yield from self.prove_arg(n+1, new_binding)


class or_(MultiArg):
    op = '|'
    
    def __or__(self, other):
        self.args = self.args + (other,)
        return self
    
    def prove(self, bindings):
        for arg in self.args:
            yield from arg.prove(bindings)


class unify(Structure):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def __str__(self):
        return f"({self.left} == {self.right})"
    
    def set_scope(self, scope):
        left.set_scope(scope)
        right.set_scope(scope)
    
    def prove(self, bindings):
        E = set(bindings.items())
        E.add((self.left, self.right))
        try:
            new_E = self.martelli_montanari(E)
        except Exception as e:
            print(f"MM failed: {e}")
            return  # failure --> don't yield
        yield dict(new_E)
    
    @staticmethod
    def simple_unify(bindings):
        E = set(bindings.items())
        return dict(unify.martelli_montanari(E))
    
    @staticmethod
    def martelli_montanari(E):
        from logicpy.core import Underscore
        
        if len(E) == 0:
            return E
        
        did_a_thing = True
        tried = set()
        
        while True:
            untried = E - tried
            if len(untried) == 0: break
            (A, B) = untried.pop()
            E.remove((A, B))
            did_a_thing = True  # Assume and unset later
             
            if not isinstance(A, Variable) and isinstance(B, Variable):
                # switch
                E.add((B, A))
            elif isinstance(A, Underscore) or isinstance(B, Underscore) or A == B:
                # remove (do nothing)
                pass
            elif isinstance(A, BasicTerm) and isinstance(B, BasicTerm):
                # peel
                if A.name == B.name and len(A.children) == len(B.children):
                    E.update(zip(A.children, B.children))
                else:
                    raise Exception(f"Conflict {A}, {B}")
            elif isinstance(A, Variable) and A != B:
                # substitute
                if B.has_occurence(A):
                    raise Exception("Occurs check")
                # While elegant, this is somewhat slow...
                replaced_E = {(X.replace(A, B), Y.replace(A, B)) for (X,Y) in E}
                if E == replaced_E:
                    did_a_thing = False
                else:
                    E = replaced_E
                E.add((A, B))  # Add it back
            else:
                did_a_thing = False
            
            if did_a_thing:
                tried.clear()
            else:
                # Add it back
                E.add((A, B))
                tried.add((A, B))
        
        return E
