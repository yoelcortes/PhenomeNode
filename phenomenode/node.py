# -*- coding: utf-8 -*-
"""
"""
import phenomenode as phn
from .variable import variable_index
from .context import ContextItem, ContextStack
from .gate import Inlets, Outlets
from .registry import Registry
from .graphics import box_graphics
from typing import Optional

__all__ = ('PhenomeNode', 'Node',)

class PhenomeNode(ContextItem, tag='n'):
    __slots__ = ('ins', 'outs', 'nodes', 'index')
    graphics = box_graphics
    registry = Registry()
    n_ins = 0
    n_outs = 0
    
    def __new__(cls, ins=None, outs=None, name=None, index=None):
        if index is None: index = variable_index
        self = super().__new__(cls, name)
        self.index = index
        self.ins = Inlets(self, self.n_ins, ins, index)
        self.outs = Outlets(self, self.n_outs, outs, index)
        self.registry.open_context_level()
        self.load()
        self.nodes = self.registry.close_context_level()
        self.registry.register(self)
        return self
    
    def get_tooltip_string(self):
        equations = self.equations()
        return equations[equations.index('\n') + 1:]
    
    def vizoptions(self):
        """Return node attributes for graphviz."""
        options = self.graphics.get_options(self)
        options['tooltip'] = self.get_tooltip_string()
        return options

    def contextualize(self, context):
        return ContextStack() if context is None else context + self
    
    def load(self): pass
    
    def __enter__(self):
        if self.nodes or self.ins or self.outs:
            raise RuntimeError("only empty nodes can enter `with` statement")
        self.registry.open_context_level()
        return self

    def __exit__(self, type, exception, traceback):
        if self.nodes or self.ins or self.outs:
            raise RuntimeError('node was modified before exiting `with` statement')
        self.nodes = nodes = tuple(self.registry.close_context_level())
        inlets = sum([i.ins for i in nodes], [])
        feeds = [i for i in inlets if not i.sources]
        outlets = sum([i.outs for i in nodes], [])
        products = [i for i in outlets if not i.sinks]   
        self.ins.edges[:] = feeds
        self.outs.edges[:] = products
        for i in feeds: i.sinks.insert(0, self)
        for i in products: i.sources.insert(0, self)
        if exception: raise exception
    
    def _equations_format(self, context, start):
        head = f"{self}:"
        if start is None:
            dlim = '\n'
            start = '  '
        else:
            dlim = '\n' + start 
            start += '  '
        return head, dlim, start
    
    def equation_list(self, fmt=None, context=None, stack=None, inbound=None):
        return []
    
    def equations(self, fmt=None, context=None, start=None, stack=None, inbound=None, right=None):
        head, dlim, start = self._equations_format(context, start)
        if stack: context = self.contextualize(context)
        eqlst = self.equation_list(fmt, context, stack, inbound)
        if right and start != '  ':
            head = '- ' + head
        if eqlst:
            if right:
                eqdlim = dlim + (len(head) - 1) * ' '
                head += ' '
                p = ''
            else:
                head += dlim
                eqdlim = dlim
                p = '- '
            eqs = head + eqdlim.join([p + i for i in eqlst]) 
        else:
            eqs = head
        if self.nodes:
            eqs += dlim + dlim.join([i.equations(fmt, context, start, stack, inbound, right) for i in self.nodes])
        return eqs
    
    def diagram(self, file: Optional[str]=None, 
                format: Optional[str]=None,
                display: Optional[bool]=True,
                context_format: Optional[int]=None,
                **graph_attrs):
        """
        Display a `Graphviz <https://pypi.org/project/graphviz/>`__ diagram
        of the node.
        
        Parameters
        ----------
        file : 
            Must be one of the following:
            
            * [str] File name to save diagram.
            * [None] Display diagram in console.
            
        format : 
            Format of file.
        display : 
            Whether to display diagram in console or to return the graphviz 
            object.
        
        """
        with phn.preferences.temporary() as pref:
            if context_format is not None:
                pref.context_format = context_format
            f = phn.digraph_from_node(self, title=str(self), **graph_attrs)
            if display or file:
                def size(node):
                    nodes = node.nodes
                    N = len(nodes)
                    for n in nodes: N += size(n)
                    return N
                N = size(self)
                if N < 3:
                    size_key = 'node'
                elif N < 8:
                    size_key = 'network'
                else:
                    size_key = 'big-network'
                height = (
                    phn.preferences.graphviz_html_height
                    [size_key]
                    [phn.preferences.tooltips_full_results]
                )
                phn.finalize_digraph(f, file, format, height)
            else:
                return f
    
    def show(self, fmt=None, context=None, start=None, stack=None, inbound=None, right=True):
        return print(self.equations(fmt, context, start, stack, inbound, right))
    
    # def equations(self, fmt=None, context=None, dlim=None):
    #     if dlim is None: dlim = '\n'
    #     return dlim.join([i.equations(fmt, context + i, dlim) for i in self.nodes])
    
    # def show(self, fmt=None):
    #     head = f"{type(self).__name__}({self.name}): "
    #     dlim = '\n' + len(head) * ' '
    #     print(
    #         head + self.equations(fmt, dlim=dlim)
    #     )
    _ipython_display_ = show
    
Node = PhenomeNode