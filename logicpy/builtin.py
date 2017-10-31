
import operator

from logicpy.structure import Structure, MultiArg, BinaryArg
from logicpy.data import Compound


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
            dbg.proven(self, mgu)
            yield mgu

DoMgu = DoMgu()


class unify_nomgu(BinaryArg):
    op = '=='
    
    @property
    def args(self):
        return (self.left, self.right)
    
    def prove(self, result, dbg, newleft=None, newright=None):
        result = result | {(newleft or self.left, newright or self.right)}
        yield result


class unify(unify_nomgu):
    def prove(self, result, dbg):
        result = result | {(self.left, self.right)}
        dbg.prove(self, result)
        return DoMgu.prove(result, dbg.next())


class EvalException(Exception):
    pass


class Eval(unify):
    op = '@='
    
    operations = {
        1: {
            '-': operator.neg,
            '+': operator.pos,
        },
        2: {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '//': operator.floordiv,
            '%': operator.mod,
            '@': operator.matmul,
            '**': operator.pow,
            '<<': operator.lshift,
            '>>': operator.rshift,
        }
    }
    
    def prove(self, result, dbg):
        dbg.prove(self, result)
        try:
            res = self.calculate(self.right)
            yield from super().prove(result, dbg.next(), newright=res)
        except MathException as e:
            dbg.output(f"Eval failed {e}")

    def calculate(self, expr):
        if isinstance(expr, Compound):
            try:
                op = self.operations[len(expr.children)][expr.name]
            except KeyError as e:
                raise EvalException("Couldn't find operation: " + str(e))
            
            try:
                return op(*(self.calculate(c) for c in expr.children))
            except EvalException as e:
                raise e  # rethrow
            except Exception as e:
                raise EvalException("Couldn't do operation: " + str(e))
        else:
            return expr

