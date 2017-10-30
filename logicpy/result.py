
from logicpy.data import Variable, BasicTerm
from logicpy.debug import NoDebugger

class MartelliMontanariFail(Exception):
    pass


class Result(frozenset):
    
    # Act like a proper set ...............................
    
    # Binary operations
    for fname in ['__and__', '__rand__', '__or__', '__ror__', '__xor__', '__rxor__', '__sub__', '__rsub__',
                  'intersection', 'difference', 'symmetric_difference', 'union']:
        def passthrough(self, other, f = getattr(frozenset, fname)):
            return Result(f(self, other))
        locals()[fname] = passthrough
    
    # Unary operations: only copy
    def copy(self):
        return Result(super().copy())
    
    
    # Representation and easy usage ......................
    
    def __str__(self):
        if len(self) == 0:
            return 'ok'
        return '{' + ', '.join(f"{L} = {R}" for L, R in self) + '}'
    
    def easy_dict(self):
        return {L.name: R for L, R in self if isinstance(L, Variable) and L.scope is None}
    
    
    # Prolog additions ....................................
    
    def mgu(self, dbg=NoDebugger()):
        try:
            return Result(Result.martelli_montanari(set(self)))
        except MartelliMontanariFail as e:
            dbg.output(f"MM failed: {e}")
            return None
    
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
            #print(f"unify {A!r}, {B!r}")
             
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
                    raise MartelliMontanariFail(f"Conflict {A}, {B}")
            elif isinstance(A, Variable) and A != B:
                # substitute
                if B.has_occurence(A):
                    raise MartelliMontanariFail(f"Occurs check {A}, {B}")
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
