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
    
    def label(self):
        label = ' '.join([
            format(variable, 's') for variable in self.variables
        ])
        if len(label) > 15: label = label[:12] + '...'
        return label
    
    def describe(self, fmt=None, formal=None):
        if fmt is None: fmt = phn.preferences.context_format
        if self.sink: 
            intext = Inlet(self.sink.ins.index(self))
        else:
            intext = phn.ContextStack()
        if self.source: 
            outext = Outlet(self.source.outs.index(self))
        else:
            outext = phn.ContextStack()
        if intext and outext:
            x = f"{outext:{fmt}} -> {intext:{fmt}}"
        elif intext:
            x = f"{intext:{fmt}}"
        elif outext:
            x = f"{outext:{fmt}}"
        if formal:
            x = f"{type(self).__name__}({x}): "
        return x
    
    def get_tooltip_string(self, fmt=None, dlim=None, formal=None):
        head = self.describe(fmt, formal)
        if dlim is None: 
            dlim = '\n' + len(head) * ' ' if formal else '\n'
        if fmt is None: fmt = phn.preferences.context_format
        vars = sorted(
            [format(variable, fmt) for variable in self.variables],
            key=lambda x: -len(x)
        )
        return head + dlim.join(vars) if formal else head + dlim + dlim.join(vars)
    
    def framed_variables(self, context=None):
        return self.variables.framed(context)
    
    def __str__(self):
        return f"{self.describe()}"
    
    def show(self, fmt=None):
        return print(self.get_tooltip_string(fmt, formal=True))
    _ipython_display_ = show

    def __repr__(self):
        return f"{type(self).__name__}({self.sources!r}, {self.sinks!r})"
    