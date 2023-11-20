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
        return self.get_tooltip_string('n')
    
    def vizoptions(self):
        options = {
            'shape': 'box',
            'gradientangle': '0',
            'width': '0.1',
            'height': '0.1',
            'orientation': '0.0',
            'peripheries': '0',
            'margin': '0',
            'fontname': 'Arial',
            'fillcolor': 'none',
        }
        options['name'] = str(hash(self))
        if 'label' not in options:
            options['label'] = str(self)
        return options
    
    def get_full_context(self):
        sources = [i for i in self.sources if i.phenomena]
        sinks = [i for i in self.sinks if i.phenomena]
        variable = self.variable
        if sources: 
            n = [i for i in sources[0].outs if i.variable is variable].index(self)
            outext = Outlet(n) + sources[:-1]
        else:
            outext = None
            if sinks:
                n = [i for i in sinks[0].ins if i.variable is variable].index(self)
                intext = Inlet(n) + sinks[:-1]
            else:
                intext = None
        return outext or intext
    
    def get_tooltip_string(self, fmt=None):
        if fmt is None: fmt = phn.preferences.context_format
        label = format(
            self.variable.framed(
                context=self.get_full_context()
            ),
            fmt
        )
        return label
    
    __str__ = label
    
    def show(self, fmt=None):
        return print(self.get_tooltip_string(fmt))
    _ipython_display_ = show

    def __repr__(self):
        return f"{type(self).__name__}({self.variable!r}, {self.sources!r}, {self.sinks!r})"
    