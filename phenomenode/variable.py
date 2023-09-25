# -*- coding: utf-8 -*-
"""
"""
from .context import ContextStack

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
    
    