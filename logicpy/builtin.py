
import operator
from functools import wraps

from logicpy.structure import Structure, MultiArg, BinaryArg, MonoArg
from logicpy.data import Compound, EvalCompound, Variable, instantiate
from logicpy.result import ResultException, UnificationFail


class TrueCls(Structure):
    def prove(self, result, dbg):
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
        return and_(*(self.args + (other,)))
    
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
        for new_result in arg.prove(result, dbg.from_next()):
            yield from self.prove_arg(n+1, new_result, dbg)


class or_(MultiArg):
    op = '|'
    
    def __or__(self, other):
        return or_(*(self.args + (other,)))
    
    def prove(self, result, dbg):
        dbg.prove(self, result)
        for arg in self.args:
            yield from arg.prove(result, dbg.next())


class unify(BinaryArg):
    op = '=='
    
    @property
    def args(self):
        return (self.left, self.right)
    
    def prove(self, result, dbg):
        result = result | {(self.left, self.right)}
        try:
            mgu = result.mgu()
            dbg.proven(self, mgu)
            yield mgu
        except UnificationFail as e:
            dbg.output(f"Unification failed: {e}")
    
    def __bool__(self):
        if isinstance(self.left, Term):
            return self.left.really_equal(self.right)
        else:
            return self.right.really_equal(self.left)


class PredicateCut(Exception):
    pass


class _Cut(Structure):
    def prove(self, result, dbg):
        dbg.output("Cut!")
        yield result
        raise PredicateCut()

cut = _Cut()


class neg(MonoArg):
    def prove(self, result, dbg):
        for _ in self.arg.prove(result, dbg.next()):
            return
        yield result


# Builtin operator support (mainly math)
# --------------------------------------

class EvalException(Exception):
    pass


def evaluate(expr):
    if isinstance(expr, EvalCompound):
        try:
            return expr.func(*(evaluate(c) for c in expr.children))
        except EvalException as e:
            raise e  # rethrow
        except Exception as e:
            raise EvalException("Couldn't do operation: " + str(e))
    else:
        return expr


class Evaluation(BinaryArg):
    op = '<<'
    
    def prove(self, result, dbg):
        dbg.prove(self, result)
        try:
            res = evaluate(instantiate(self.right, result))
            result = result | {(self.left, res)}
            mgu = result.mgu()
            dbg.proven(self, mgu)
            yield mgu
        except (EvalException, ResultException) as e:
            dbg.output(f"Eval failed: {e}")


class Comparison(BinaryArg):
    def prove(self, result, dbg):
        dbg.prove(self, result)
        try:
            l = evaluate(instantiate(self.left, result))
            r = evaluate(instantiate(self.right, result))
            if self.compare(l, r):
                dbg.proven(self, result)
                yield result
        except (EvalException, Uninstantiated) as e:
            dbg.output(f"Comparison failed: {e}")
        


class Lower(Comparison):
    op = '<'
    compare = lambda s, l, r: l < r


class LowerOrEqual(Comparison):
    op = '<='
    compare = lambda s, l, r: l <= r


class Greater(Comparison):
    op = '>'
    compare = lambda s, l, r: l > r


class GreaterOrEqual(Comparison):
    op = '>='
    compare = lambda s, l, r: l >= r


def evaluated(func):
    "Turns a function into a term that is evaluated at runtime"
    @wraps(func)
    def wrapper(*args):
        return EvalCompound(func.__name__, func, args)
    return wrapper


@evaluated
def max_(x, y):
    return max(x, y)


@evaluated
def min_(x, y):
    return min(x, y)

@evaluated
def abs_(x):
    return abs(x)

