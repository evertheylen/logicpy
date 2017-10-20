

class Structure:
    # builtin operators, see below
    
    def set_scope(self, scope):
        # By default, don't do anything
        pass
    
    def occurences(self, O):
        pass
    
    def __and__(self, other):
        return and_(self, other)
    
    def __or__(self, other):
        return or_(self, other)
    
    def __eq__(self, other):
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
