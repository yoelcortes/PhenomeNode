# -*- coding: utf-8 -*-
"""
"""
from .variable import Variables, variable_index
from .context import Outlet, Inlet
from collections import deque
import phenomenode as phn

__all__ = ('Edge',)

class Edge:
    __slots__ = ('sources', 'sinks', 'variables', 'index')
        
    def __init__(self, sources=None, sinks=None, index=None, variables=None):
        if index is None: index = variable_index
        if variables is None: variables = index.equilibrium
        self.sources = deque() if sources is None else deque(sources)
        self.sinks = deque() if sinks is None else deque(sinks)
        self.variables = variables
        self.index = index
    
    @property
    def sink(self):
        sinks = self.sinks
        return sinks[0] if sinks else None
    
    @property
    def source(self):
        sources = self.sources
        return sources[0] if sources else None
    
    def describe(self, fmt=None, context=None):
        if self.source: 
            context = Outlet(self.source.outs.index(self)) + context
        if self.sink: 
            context = Inlet(self.sink.ins.index(self)) + context
        return format(context, 'n')
    
    def get_tooltip_string(self, fmt=None, dlim=None):
        if dlim is None: dlim = '\n'
        if fmt is None: fmt = phn.preferences.context_format
        return dlim.join([
            format(variable, fmt) for variable in self.variables
        ])
    
    def framed_variables(self, context=None):
        return self.variables.framed(context)
    
    def show(self, fmt=None):
        head = f"{type(self).__name__}: "
        dlim = '\n' + len(head) * ' '
        return print(
            head + self.get_tooltip_string(fmt, dlim)
        )
    _ipython_display_ = show

    def __repr__(self):
        return f"{type(self).__name__}({self.sources!r}, {self.sinks!r})"
    