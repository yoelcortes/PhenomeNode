# -*- coding: utf-8 -*-
"""
"""
from .variable import Variables, variable_index
from .context import Outlet, Inlet
from collections import deque
import phenomenode as phn

__all__ = ('VarNode',)

class VarNode:
    __slots__ = ('variable', 'sources', 'sinks', 'variable')
        
    def __init__(self, variable, sources=None, sinks=None):
        self.sources = deque() if sources is None else deque(sources)
        self.sinks = deque() if sinks is None else deque(sinks)
        self.variable = variable
    
    @property
    def sink(self): # Parent sink
        sinks = self.sinks
        return sinks[0] if sinks else None
    
    @property
    def source(self): # Parent source
        sources = self.sources
        return sources[0] if sources else None
    
    @property
    def neighbors(self):
        return self.sinks + self.sources
    
    def label(self):
        return self.get_tooltip_string('s')
    
    def get_tooltip_string(self, fmt=None):
        if fmt is None: fmt = phn.preferences.context_format
        sources = [i for i in self.sources if i.phenomena]
        sinks = [i for i in self.sinks if i.phenomena]
        if sinks:
            intext = Inlet(sinks[0].ins.index(self)) + sinks
        else:
            intext = None
            if sources: 
                outext = Outlet(sources[0].outs.index(self)) + sources
            else:
                outext = phn.ContextStack()
        label = format(
            self.framed_variable(
                context=intext or outext
            ),
            fmt
        )
        if len(label) > 15: label = label[:12] + '...'
        return label
    
    def framed_variable(self, context=None):
        return self.variable.framed(context)
    
    __str__ = label
    
    def show(self, fmt=None):
        return print(self.get_tooltip_string(fmt))
    _ipython_display_ = show

    def __repr__(self):
        return f"{type(self).__name__}({self.variable!r}, {self.sources!r}, {self.sinks!r})"
    