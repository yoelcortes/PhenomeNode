# -*- coding: utf-8 -*-
"""
"""
from .context import ContextStack, Chemical, Phase

__all__ = ('Variable', 'ActiveVariables', 'variable_index')

class Variable:
    __slots__ = ('name', 'context', '_hash')
    
    def __init__(self, name, context=None):
        self.name = name
        self.context = ContextStack() if context is None else context
        
    def __hash__(self):
        try:
            return self._hash
        except:
            self._hash = hash = (self.__class__, self.name, self.context).__hash__()
            return hash
        
    def __eq__(self, other):
        return self.name == other.name and self.context == other.context
        
    def __call__(self, fmt=None, context=None):
        name = self.name
        context = context + self.context
        if not context: return name
        if fmt == -1:
            return f"{name}{context(fmt)}"
        else:
            return f"{name}[{context(fmt)}]"
    
    def __repr__(self):
        return f"{type(self).__name__}({self.name!r}, {self.context!r})"
    
    def __str__(self):
        return self()
    
    def framed(self, context=None):
        return Variable(self.name, self.context + context)
    
    def show(self, fmt=None):
        return print(self(fmt))
    _ipython_display_ = show


class ActiveVariables(frozenset):
    
    def __new__(cls, *variables):
        self = super().__new__(cls, variables)
        for i in variables: setattr(self, i(-1), i)
        return self
    
    def framed(self, context=None):
        if context is None: return self
        return ActiveVariables(*[i.framed(context) for i in self])
    
    def __str__(self):
        return f"{', '.join([str(i) for i in self])}"
    
    def show(self, fmt=None):
        variables = f"{', '.join([i(fmt) for i in self])}"
        return print(variables)
    _ipython_display_ = show

default_chemicals = Chemical.family(['Water'])
default_phases = Phase.family(['g', 'l'])

class VariableIndex:
    T = Variable('T')
    P = Variable('P')
    H = Variable('H')
    S = Variable('S')
    G = Variable('G')
    A = Variable('A')
    V = Variable('V')
    F = Variable('F')
    
    def load(self, chemicals=None, phases=None):
        if chemicals is None: chemicals = default_chemicals
        if phases is None: phases = default_phases
        self.chemicals = chemicals
        self.phases = phases
        self.Fcp = Variable('F', ContextStack(chemicals, phases))
        self.Fc = Variable('F', chemicals)
        self.KVc = Variable('KV', chemicals)
        self.KLc = Variable('KL', chemicals)

variable_index = VariableIndex()
variable_index.load()
