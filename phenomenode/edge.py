# -*- coding: utf-8 -*-
"""
"""
from .context import ContextStack, Chemical, Phase
from .variable import Variable, ActiveVariables, variable_index

__all__ = ('Edge',)

class Edge:
    __slots__ = ('sources', 'sinks', 'variables', 'index')
        
    def __init__(self, sources=None, sinks=None, index=None, variables=None):
        if index is None: index = variable_index
        if variables is None: variables = ActiveVariables(index.Fcp, index.T, index.P)
        self.sources = [] if sources is None else sources
        self.sinks = [] if sinks is None else sinks
        self.variables = variables
        self.index = index
    
    def __call__(self, fmt=None, context=None, dlim=None):
        if dlim is None: dlim = '\n'
        return dlim.join([
            variable(fmt, context)
            for variable in self.variables
        ])
    
    def framed_variables(self, context=None):
        return self.variables.framed(context)
    
    def show(self, fmt=None):
        head = f"{type(self).__name__}: "
        dlim = '\n' + len(head) * ' '
        return print(
            head + self(fmt, dlim=dlim)
        )
    _ipython_display_ = show

    def __repr__(self):
        return f"{type(self).__name__}({self.sources!r}, {self.sinks!r})"
    
