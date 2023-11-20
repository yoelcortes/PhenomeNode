# -*- coding: utf-8 -*-
"""
"""
from types import MappingProxyType
from .context import ContextStack, ContextItem, ContextFamily, Chemical, Phase, Inlet, Outlet
from .quantity import Quantity
from .preferences import preferences

__all__ = ('Variable', 'Variables', 'variable_index')

class Variable(Quantity):
    __slots__ = ('name', 'context', '_hash')
    
    def __init__(self, name, context=None):
        self.name = name
        self.context = ContextStack() if context is None else context
        
    def __getitem__(self, index):
        context = self.context
        if isinstance(index, ContextItem):
            tag = index.tag
            if isinstance(context, ContextFamily):
                if context.tag == tag: return Variable(self.name, index)
            elif isinstance(context, ContextStack):
                new_context = []
                for i in context:
                    if isinstance(i, ContextFamily) and i.tag == tag:
                        new_context.append(index)
                    else:
                        new_context.append(i)
                return Variable(self.name, ContextStack(*new_context))
            else:
                raise IndexError(f"{self} has no context family for index {index}")
        elif isinstance(index, ContextStack):
            # TODO: Optimize
            variable = self
            for i in index: variable = variable[i]
            return variable
            
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
    
    def __format__(self, fmt):
        if fmt == '': fmt = preferences.context_format
        name = self.name
        context = self.context
        if not context: return name
        if fmt == 's':
            return f"{name}{context:s}"
        else:
            return f"{name}[{context:{fmt}}]"
        
    def __str__(self):
        return format(self, 's')
        
    def framed(self, context=None):
        return Variable(self.name, self.context + context)
    
    def show(self):
        return print(self)
    _ipython_display_ = show


class Variables(frozenset):
    def __new__(cls, *variables):
        self = super().__new__(cls, variables)
        setattr = super().__setattr__
        setattr(self, 'variables', variables)
        for i in variables: setattr(self, str(i), i)
        return self
    
    def __getitem__(self, index):
        return self.variables[index]
    
    def __iter__(self):
        return iter(self.variables)
    
    def __setattr__(self, name, other):
        raise AttributeError("variables are immutable")
    
    def framed(self, context=None):
        if context is None: return self
        return Variables(*[i.framed(context) for i in self])
    
    def __str__(self):
        return f"Variables({', '.join([str(i) for i in self])})"
    
    def show(self, fmt=None):
        variables = f"({', '.join([format(i, fmt) for i in self])})"
        return print(variables)
    _ipython_display_ = show

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
    chemicals = chemicals = Chemical.family
    phases = phases = Phase.family
    liquid = Phase('L')
    solid = Phase('S')
    gas = Phase('G')
    inlets = Inlet.family
    outlets = Outlet.family
    Fcp = Variable('F', ContextStack(chemicals, phases))
    Fc = Variable('F', chemicals)
    FVc = Variable('F', ContextStack(chemicals, gas))
    FLc = Variable('F', ContextStack(chemicals, liquid))
    KVc = Variable('KV', ContextStack(chemicals, gas))
    KLc = Variable('KL', ContextStack(chemicals, liquid))
    
    def __new__(cls): return cls

variable_index = VariableIndex
