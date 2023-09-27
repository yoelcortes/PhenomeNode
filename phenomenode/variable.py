# -*- coding: utf-8 -*-
"""
"""
from .context import ContextStack, Chemical, Phase

__all__ = ('Variable', 'Variables', 'variable_index')

class Variable:
    __slots__ = ('name', 'context', '_hash')
    
    def __init__(self, name, context=None):
        self.name = name
        self.context = ContextStack() if context is None else context
        
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


class Variables(tuple):
    
    def __new__(cls, *variables):
        self = super().__new__(cls, variables)
        for i in variables: setattr(self, i(-1), i)
        return self
    
    def framed(self, context=None):
        if context is None: return self
        return Variables(*[i.framed(context) for i in self])
    
    def __str__(self):
        return f"Variables({', '.join([str(i) for i in self])})"
    
    def show(self, fmt=None):
        variables = f"({', '.join([i(fmt) for i in self])})"
        return print(variables)
    _ipython_display_ = show

default_chemicals = Chemical.family(['Water'])
default_phases = Phase.family(['g', 'l'])

class VariableIndex:
    T = Variable('T') # Temperature
    P = Variable('P') # Pressure
    H = Variable('H') # Enthalpy
    S = Variable('S') # Entropy
    G = Variable('G') # Gibbs free energy
    A = Variable('A') # Helmholtz free energy
    V = Variable('V') # Vapor fraction [by mol]
    F = Variable('F') # Flow rate [by mol]
    split = Variable('θ') # Split fraction
    
    def load(self, chemicals=None, phases=None):
        if chemicals is None: chemicals = default_chemicals
        if phases is None: phases = default_phases
        self.chemicals = chemicals
        self.phases = phases
        self.Fcp = Variable('F', ContextStack(chemicals, phases))
        self.Fc = Variable('F', chemicals)
        self.KVc = Variable('KV', chemicals)
        self.KLc = Variable('KL', chemicals)
        self.equilibrium = Variables(self.Fcp, self.T, self.P)
        self.bulk = Variables(self.Fc, self.H, self.P)

variable_index = VariableIndex()
variable_index.load()
