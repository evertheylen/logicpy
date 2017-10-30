
class Structure:
    # builtin operators, see below
    
    def set_scope(self, scope):
        # By default, don't do anything
        pass
    
    def occurences(self, O):
        pass
    
    def __and__(self, other):
        from logicpy.builtin import and_
        return and_(self, other)
    
    def __or__(self, other):
        from logicpy.builtin import or_
        return or_(self, other)
    
    def __eq__(self, other):
        from logicpy.builtin import unify
        return unify(self, other)


class MultiArg(Structure):
    def __init__(self, *args):
        self.args = args
    
    def __str__(self):
        return '(' + f" {self.op} ".join(map(str, self.args)) + ')'
    
    def set_scope(self, scope):
        for a in self.args:
            a.set_scope(scope)
    
    def occurences(self, O):
        for a in self.args:
            a.occurences(O)
    
    def has_occurence(self, var):
        return any(a.has_occurence(var) for a in self.args)

    
