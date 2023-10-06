# -*- coding: utf-8 -*-
"""
"""
from .context import ContextStack, Chemical, Phase
from .quantity import Quantity
from .preferences import preferences

__all__ = ('Variable', 'Variables', 'variable_index')

class Variable(Quantity):
    __slots__ = ('name', 'context', '_hash')
    
    def __init__(self, name, context=None):
        self.name = name
        self.context = ContextStack() if context is None else context
        
    def __hash__(self):
        try:
            return self._hash
        except:
            self._hash = hash(
                (self.name, self.context)
            )
            return self._hash
        
    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.name == other.name and self.context is other.context
        
    def __repr__(self):
        return f"{type(self).__name__}({self.name!r}, {self.context!r})"
    
    def __str__(self):
        fmt = preferences.context_format
        name = self.name
        context = self.context
        if not context: return name
        if fmt == -1:
            return f"{name}{context}"
        else:
            return f"{name}[{context}]"
    
    def framed(self, context=None):
        return Variable(self.name, self.context + context)
    
    def show(self):
        return print(self)
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
    T = Variable('T') # Temperature [K]
    P = Variable('P') # Pressure [Pa]
    H = Variable('H') # Enthalpy [kJ]
    S = Variable('S') # Entropy [kJ]
    G = Variable('G') # Gibbs free energy [kJ]
    A = Variable('A') # Helmholtz free energy [kJ]
    V = Variable('V') # Vapor fraction [by mol]
    L = Variable('L') # Extract fraction [by mol]
    F = Variable('F') # Flow rate [by mol]
    Q = Variable('Q') # Duty [kJ]
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
