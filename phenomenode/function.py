# -*- coding: utf-8 -*-
"""
"""
from .quantity import Quantity
import phenomenode as phn

__all__ = ('functions',)

class Function(Quantity):
    __slots__ = ('name', 'context', '_hash')
    
    def __init__(self, name, context=None):
        self.name = name
        self.context = phn.ContextStack() if context is None else context
        
    def __or__(self, context):
        return Function(self.name, self.context + context)
    
    def __call__(self, *args):
        return FunctionCall(self, args)
    
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
        fmt = phn.preferences.context_format
        name = self.name
        context = self.context
        if not context: return name
        if fmt == -1:
            return f"{name}|{context(fmt)}"
        else:
            return f"{name}|{context(fmt)}]"
    
    def show(self, fmt=None):
        return print(self)
    _ipython_display_ = show


class FunctionCall:
    __slots__ = ('function', 'parameters', '_hash')
    
    def __init__(self, function, parameters):
        self.function = function
        self.parameters = parameters
        
    def __hash__(self):
        try:
            return self._hash
        except:
            self._hash = hash(
                (self.function, self.parameters)
            )
            return self._hash
        
    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.function == other.function and self.parameters is other.parameters
        
    def __str__(self):
        parameters = ', '.join([str(i) for i in self.parameters])
        return f"{self.function}({parameters})"
        
    def __repr__(self):
        return f"{type(self).__name__}({self.function!r}, {self.parameters!r})"
    
    def show(self):
        return print(self)
    _ipython_display_ = show


class Functions:
    
    def __init__(self, **functions):
        self.__dict__.update(functions)
        
    def __repr__(self):
        return f"{type(self).__name__}({', '.join([f'{i}={j!r}' for i, j in self.__dict__])})"
    
    
functions = Functions(
    sum=Function('Σ'),
    product=Function('Π'),
    vle=Function('vle'),
    lle=Function('lle'),
    enthalpy=Function('enthalpy'),
)