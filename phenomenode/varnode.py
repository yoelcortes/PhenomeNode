# -*- coding: utf-8 -*-
"""
"""
from .variable import Variables, variable_index
from .context import Outlet, Inlet
from collections import deque
import phenomenode as phn

__all__ = ('VarNode',)

class VarNode:
    __slots__ = ('variable', 'sources', 'sinks', 'variable', '_number')
        
    def __init__(self, variable, sources=None, sinks=None):
        self.sources = deque() if sources is None else deque(sources)
        self.sinks = deque() if sinks is None else deque(sinks)
        self.variable = variable
    
    @property
    def number(self):
        try:
            return self._number
        except:
            parent = (
                (self.sources and self.sources[-1])
                or (self.sinks and self.sinks[-1])
            )
            if not parent: return None
            ancestor = parent.ancestry[-1]
            if ancestor.phenomena:
                varnodes = sum([i.varnodes for i in ancestor.nested_phenomena if not i.phenomena], [])
            else:
                varnodes = ancestor.varnodes
            varnode_set = set()
            n = 0
            variable = self.variable
            for i in varnodes:
                if i in varnode_set: continue
                if i.variable == variable and not any([j.phenomena for j in (*i.sources, *i.sinks)]): 
                    i._number = n
                    n += 1
                varnode_set.add(i)
            if n <= 1: self._number = None
            return self._number
            
    @property
    def sink(self):
        sinks = self.sinks
        return sinks[0] if sinks else None
    
    @property
    def source(self): 
        sources = self.sources
        return sources[0] if sources else None
    
    @property
    def neighbors(self):
        return self.sinks + self.sources
    
    def label(self):
        return self.get_tooltip_string('n')
    
    def vizoptions(self):
        tooltip = self.get_tooltip_string(phn.preferences.label_format)
        options = {
            'gradientangle': '0',
            'width': '0.5' if phn.preferences.label_nodes else '0.1',
            'height': '0.5' if phn.preferences.label_nodes else '0.1',
            'orientation': '0.0',
            'peripheries': '1',
            'margin': '0',
            'fontname': 'Arial',
            'fillcolor': 'none',
            'shape': 'circle' if phn.preferences.label_nodes else 'point',
            'style': 'filled',
            'color': '#b4b1ae',
            'tooltip': tooltip,
            'label': tooltip if phn.preferences.label_nodes else '',
            'name': str(hash(self)),
        }
        # if 'texlbl' not in options:
        #     options['texlbl'] = self.get_tooltip_string('l')
        return options
    
    def get_full_context(self):
        sources = self.sources
        sinks = self.sinks
        if sources:
            for source in sources:
                if source.phenomena: 
                    unit = True
                    break
            else:
                 source = sources[0]
                 unit = False
            if unit:
                for n, i in enumerate(source.outs):
                    if self in i.varnodes: break
                context = Outlet(n) + source.ancestry[:-1]
            else:
                if len(source.ancestry) > 1:
                    n = self.number
                    if n is None:
                        context = source.ancestry[1:-1]
                    else:
                        context = phn.Number(n) + source.ancestry[1:-1]
                else:
                    context = None
        elif sinks:
            for sink in sinks:
                if sink.phenomena: 
                    unit = True
                    break
            else:
                 sink = sinks[0]
                 unit = False
            if unit:
                for n, i in enumerate(sink.ins):
                    if self in i.varnodes: break
                context = Inlet(n) + sink.ancestry[:-1]
            else:
                if len(sink.ancestry) > 1:
                    n = self.number
                    if n is None:
                        context = sink.ancestry[1:-1]
                    else:
                        context = phn.Number(n) + sink.ancestry[1:-1]
                else:
                    context = None
            
        else:
            context = None
        return context
    
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
    