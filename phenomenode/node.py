# -*- coding: utf-8 -*-
"""
"""
import phenomenode as phn
from .variable import Variable, variable_index
from .context import ContextItem, ContextStack
from .gate import Inlets, Outlets
from .registry import Registry
from .graphics import box_graphics
from .utils import AbstractMethod
from typing import Optional

__all__ = ('PhenomeNode', 'Node',)

class PhenomeNode(ContextItem, tag='n'):
    __slots__ = ('ins', 'outs', 'nodes', 'index', 'inbound', 'context')
    graphics = box_graphics
    registry = Registry()
    n_ins = 0
    n_outs = 0
    
    def __new__(cls, ins=None, outs=None, name=None, index=None, **kwargs):
        if index is None: index = variable_index
        self = super().__new__(cls, name)
        self.index = index
        self.prepare(ins, outs, **kwargs)
        self.registry.open_context_level()
        self.load()
        self.nodes = self.registry.close_context_level()
        self.registry.register(self)
        return self
    
    def prepare(self, ins, outs, **kwargs):
        """Initialize edges and any additional parameters. 
        This method is called before `load`"""
        for i, j in kwargs.items(): setattr(self, i, j)
        self.init_ins(ins)
        self.init_outs(outs)
    
    def init_ins(self, ins, variables=None):
        self.ins = Inlets(self, self.n_ins, ins, self.index, variables)
        
    def init_outs(self, outs, variables=None):
        self.outs = Outlets(self, self.n_outs, outs, self.index, variables)
    
    #: Abstract method for loading subnodes. This method is called after `init`
    load = AbstractMethod
    
    #: Abstract method for generating a list of equations.
    equations = AbstractMethod
    
    def get_tooltip_string(self):
        equations = self.describe()
        try:
            index = equations.index('\n')
        except:
            return equations
        else:
            return equations[index + 1:]
    
    def vizoptions(self):
        """Return node attributes for graphviz."""
        options = self.graphics.get_options(self)
        options['tooltip'] = self.get_tooltip_string()
        return options

    def contextualize(self, context):
        return ContextStack() if context is None else self + context
    
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
        for i in feeds: i.sinks.append(self)
        for i in products: i.sources.append(self)
        if exception: raise exception
    
    def _equations_format(self, context, start):
        head = f"{type(self).__name__}({self:n}):"
        if start is None:
            dlim = '\n'
            start = '  '
        else:
            dlim = '\n' + start 
            start += '  '
        return head, dlim, start
    
    def variable(self, name):
        return Variable(name, self.context)
    
    def inlet_variables(self, family=None):
        return self.ins.framed_variables(self.context, family=family)
    
    def outlet_variables(self, family=None):
        return self.outs.framed_variables(self.context, family=None, inbound=self.inbound)
    
    def describe(self, context=None, start=None, stack=None, inbound=None, right=None):
        first = start is None
        head, dlim, start = self._equations_format(context, start)
        if stack: context = self.contextualize(context)
        self.inbound = inbound
        self.context = context
        eqlst = self.equations()
        if right and not first:
            head = '- ' + head
        if eqlst is NotImplemented:
            eqs = head
        else:
            if right:
                if first:
                    spaces = (len(head) + 1) * ' '
                else:
                    spaces = (len(head) - 1) * ' '
                eqdlim = dlim + spaces
                head += ' '
                p = ''
            else:
                if first:
                    head += dlim
                    eqdlim = dlim
                    p = ''
                else:
                    head += dlim[:-2]
                    eqdlim = dlim[:-2]
                    p = '- '
            eqs = head + eqdlim.join([p + str(i) for i in eqlst]) 
        if self.nodes:
            eqs += dlim + dlim.join([i.describe(context, start, stack, inbound, right) for i in self.nodes])
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
    
    def show(self, context_format=None, context=None, start=None, stack=None, inbound=None, right=True):
        with phn.preferences.temporary() as pref:
            if context_format is not None: pref.context_format = context_format
            return print(self.describe(context, start, stack, inbound, right))
    
    _ipython_display_ = show
    
Node = PhenomeNode