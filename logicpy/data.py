
import operator


# Free functions to enable working with 'foreign' constants
# ---------------------------------------------------------

def with_scope(obj, scope):
    if hasattr(obj, 'with_scope'):
        return obj.with_scope(scope)
    else:
        return obj


def has_occurence(obj, var):
    if hasattr(obj, 'has_occurence'):
        return obj.has_occurence(var)
    else:
        return False


def occurences(obj, O):
    if hasattr(obj, 'occurences'):
        return obj.occurences(O)


def replace(obj, A, B):
    if obj is A or obj == A:
        return B
    elif hasattr(obj, 'replace'):
        return obj.replace(A, B)
    else:
        return obj


def instantiate(expr, result):
    if hasattr(expr, 'instantiate'):
        return expr.instantiate(result)
    else:
        return expr



# Terms and builtin operations
# ----------------------------


def binary_compounder(name, func):
    def operation(self, other):
        return InfixEvalCompound(name, func, (self, other))
    def rev_operation(self, other):
        return InfixEvalCompound(name, func, (other, self))
    return operation, rev_operation


def unary_compounder(name, func):
    def operation(self):
        return PrefixEvalCompound(name, func, (self,))
    return operation


class Term:
    def __init__(self, been_scoped=False):
        self.been_scoped = been_scoped
    
    def with_scope(self, scope):
        if self.been_scoped:
            return self
        else:
            return type(self)(been_scoped=True)
    
    # Basic operand support ...............................
    
    __add__, __radd__ =            binary_compounder('+', operator.add)
    __sub__, __rsub__ =            binary_compounder('-', operator.sub)
    __mul__, __rmul__ =            binary_compounder('*', operator.mul)
    __div__, __rdiv__ =            binary_compounder('/', operator.truediv)
    __floordiv__, __rfloordiv__ =  binary_compounder('//', operator.floordiv)
    __mod__, __rmod__ =            binary_compounder('%', operator.mod)
    __matmul__, __rmatmul__ =      binary_compounder('@', operator.matmul)
    __pow__, __rpow__ =            binary_compounder('**', operator.pow)
    
    __pos__ = unary_compounder('+', operator.pos)
    __neg__ = unary_compounder('-', operator.neg)
    
    
    # Comparisons .........................................
    
    def __lt__(l, r):
        from logicpy.builtin import Lower
        return Lower(l, r)
    
    def __le__(l, r):
        from logicpy.builtin import LowerOrEqual
        return LowerOrEqual(l, r)
    
    def __gt__(l, r):
        from logicpy.builtin import Greater
        return Greater(l, r)
    
    def __ge__(l, r):
        from logicpy.builtin import GreaterOrEqual
        return GreaterOrEqual(l, r)
    
    
    # Some random operator overloads ......................
    
    def __lshift__(self, other):
        "Replaces is in Prolog"
        from logicpy.builtin import Evaluation
        return Evaluation(self, other)
    
    def __rshift__(self, other):
        from logicpy.builtin import Evaluation
        return Evaluation(other, self)
    
    def __eq__(self, other):
        if self.been_scoped:
            return type(self) == type(other) and self.really_equal(other)
        else:
            from logicpy.builtin import unify
            return unify(self, other)
    
    def __ne__(self, other):
        if self.been_scoped:
            return type(self) != type(other) or (not self.really_equal(other))
        else:
            from logicpy.builtin import unify, neg
            return neg(unify(self, other))



# Subclasses of Term: Atom, Compound, Variable and some shared functionality
# --------------------------------------------------------------------------

class NamedTerm(Term):
    TERM_TYPE = 'Term'
    
    def __init__(self, name, been_scoped=False):
        super().__init__(been_scoped)
        self.name = name
    
    def __str__(self):
        return str(self.name)
    
    def __repr__(self):
        return f"{type(self).__name__}({self.name!r})"
    
    def really_equal(self, other):
        return type(self) == type(other) and self.name == other.name
    
    def __hash__(self):
        return hash(self.name)
    
    def has_occurence(self, var):
        return False  # by default
    
    def occurences(self, O):
        pass
    
    def with_scope(self, scope):
        if self.been_scoped:
            return self
        else:
            return type(self)(self.name, been_scoped=True)


class BasicTerm(NamedTerm):
    pass


class Atom(BasicTerm):
    def __call__(self, *args):
        assert len(args) >= 1, "Creation of Compound needs at least 1 argument"
        return Compound(self.name, args)
    
    children = []


class NotInstantiated(Exception):
    pass


class Compound(BasicTerm):
    def __init__(self, name, children, been_scoped=False):
        super().__init__(name, been_scoped)
        self.children = tuple(children)
    
    def __str__(self):
        return f"{self.name}({', '.join(map(str, self.children))})"
    
    def __repr__(self):
        return f"{type(self).__name__}({self.name!r}, {self.children!r})"
    
    def really_equal(self, other):
        return self.name == other.name and self.children == other.children
    
    def __hash__(self):
        return hash((self.name, self.children))
    
    def has_occurence(self, var):
        return any(has_occurence(c, var) for c in self.children)
    
    def occurences(self, O):
        for c in self.children:
            occurences(c, O)
    
    def replace(self, A, B):
        new_children = tuple(replace(c, A, B) for c in self.children)
        return Compound(self.name, new_children, been_scoped=self.been_scoped)
    
    def with_scope(self, scope):
        return Compound(self.name, tuple(with_scope(c, scope) for c in self.children), been_scoped=True)

    def instantiate(self, result):
        return Compound(self.name, tuple(instantiate(c, result) for c in self.children), been_scoped=self.been_scoped)


class EvalCompound(Compound):
    def __init__(self, name, func, children, been_scoped=False):
        super().__init__(name, children, been_scoped)
        self.func = func
    
    def replace(self, A, B):
        new_children = tuple(replace(c, A, B) for c in self.children)
        return EvalCompound(self.name, self.func, new_children, been_scoped=self.been_scoped)
    
    def with_scope(self, scope):
        return EvalCompound(self.name, self.func, tuple(with_scope(c, scope) for c in self.children), been_scoped=True)

    def instantiate(self, result):
        return EvalCompound(self.name, self.func, tuple(instantiate(c, result) for c in self.children), been_scoped=self.been_scoped)


class InfixEvalCompound(EvalCompound):
    def __str__(self):
        return '(' + f" {self.name} ".join(map(str, self.children)) + ')'


class PrefixEvalCompound(EvalCompound):
    def __str__(self):
        return self.name + " ".join(map(str, self.children))


class Variable(NamedTerm):
    def __init__(self, name, scope=None):
        super().__init__(name, scope is not None)
        self.name = name
        self.scope = scope
    
    def __str__(self):
        if self.scope:
            return f"{self.name}:{self.scope % 997}"
        else:
            return super().__str__()
    
    def __repr__(self):
        if self.scope:
            return f"Variable({self.name!r}, {self.scope})"
        else:
            return f"Variable({self.name!r})"
    
    def really_equal(self, other):
        return self.name == other.name and self.scope == other.scope
    
    def __hash__(self):
        return hash((self.name, self.scope))
    
    def has_occurence(self, var):
        return self == var
    
    def occurences(self, O):
        O.add(self)
    
    def with_scope(self, scope):
        return Variable(self.name, scope)

    def instantiate(self, result):
        return result.get_var(self)

