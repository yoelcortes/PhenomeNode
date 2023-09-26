# -*- coding: utf-8 -*-
"""
"""
from .variable import Variables, variable_index
from .context import Outlet, Inlet

__all__ = ('Edge',)

class Edge:
    __slots__ = ('sources', 'sinks', 'variables', 'index')
        
    def __init__(self, sources=None, sinks=None, index=None, variables=None):
        if index is None: index = variable_index
        if variables is None: variables = Variables(index.Fcp, index.T, index.P)
        self.sources = [] if sources is None else sources
        self.sinks = [] if sinks is None else sinks
        self.variables = variables
        self.index = index
    
    @property
    def sink(self):
        sinks = self.sinks
        return sinks[-1] if sinks else None
    
    @property
    def source(self):
        sources = self.sources
        return sources[-1] if sources else None
    
    def __call__(self, fmt=None, context=None):
        if self.source: 
            context = context + Outlet(self.source.outs.index(self))
        if self.sink: 
            context = context + Inlet(self.sink.ins.index(self))
        return context(fmt)
    
    def get_tooltip_string(self, fmt=None, context=None, dlim=None):
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
            head + self.get_tooltip_string(fmt, dlim=dlim)
        )
    _ipython_display_ = show

    def __repr__(self):
        return f"{type(self).__name__}({self.sources!r}, {self.sinks!r})"
    