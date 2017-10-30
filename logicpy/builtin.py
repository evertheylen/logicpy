
from logicpy.structure import Structure, MultiArg


class TrueCls(Structure):
    def prove(self, result, dbg):
        dbg.prove(self, result)
        dbg.proven(self, result)
        yield result

    __repr__ = __str__ = lambda s: "True"

True_ = TrueCls()


class FailCls(Structure):
    def prove(self, result, dbg):
        dbg.prove(self, result)
        return
        yield
    
    __repr__ = __str__ = lambda s: "Fail"

Fail = FailCls()


class and_(MultiArg):
    op = '&'
    
    def __and__(self, other):
        return and_(self.args + (other,))
    
    def prove(self, result, dbg):
        # Backtracking implementation!
        dbg.prove(self, result)
        return self.prove_arg(0, result, dbg)
    
    def prove_arg(self, n, result, dbg):
        if n >= len(self.args):
            dbg.proven(self, result)
            yield result
            return
        
        arg = self.args[n]
        for new_result in arg.prove(result, dbg.next()):
            yield from self.prove_arg(n+1, new_result, dbg)


class or_(MultiArg):
    op = '|'
    
    def __or__(self, other):
        return or_(self.args + (other,))
    
    def prove(self, result, dbg):
        dbg.prove(self, result)
        for arg in self.args:
            yield from arg.prove(result, dbg.next())


class SimpleOperation(Structure):
    def __str__(self):
        return type(self).__name__


class DoMgu(SimpleOperation):
    def prove(self, result, dbg):
        dbg.prove(self, result)
        mgu = result.mgu(dbg)
        if mgu:
            dbg.proven(self, result)
            yield mgu

DoMgu = DoMgu()


class unify(MultiArg):
    def __init__(self, left, right, do_mgu=True):
        self.left = left
        self.right = right
        self.do_mgu = do_mgu
    
    def __str__(self):
        return f"({self.left} == {self.right})"
    
    @property
    def args(self):
        return (self.left, self.right)

    def prove(self, result, dbg):
        dbg.prove(self, result)
        result = result | {(self.left, self.right)}
        if self.do_mgu:
            yield from DoMgu.prove(result, dbg.next())
        else:
            yield result

