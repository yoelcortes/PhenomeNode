# -*- coding: utf-8 -*-
"""
"""
from .variable import variable_index
from .context import ContextItem, ContextStack
from .gate import Inlets, Outlets
from .registry import Registry

__all__ = ('PhenomeNode', 'Node',)

class PhenomeNode(ContextItem, tag='n'):
    __slots__ = ('ins', 'outs', 'nodes', 'index')
    registry = Registry()
    n_ins = 0
    n_outs = 0
    
    def __new__(cls, name=None, ins=None, outs=None, index=None):
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
        if context is None:
            head = f"{type(self).__name__}({self.name}): "
        else:
            head = f"{self.tag}={type(self).__name__}({self.name}): "
        if start is None:
            dlim = '\n' + len(head) * ' '
            start = '  '
        else:
            dlim = '\n' + start + len(head) * ' '
            start += '  '
        return head, dlim, start
    
    def equations(self, fmt=None, context=None, start=None, stack=None, inbound=None):
        head, dlim, start = self._equations_format(context, start)
        if stack: context = self.contextualize(context)
        dlim = ('\n' + start)
        return head + dlim + dlim.join([i.equations(fmt, context, start, stack, inbound) for i in self.nodes])
    
    def show(self, fmt=None, context=None, start=None, stack=None, inbound=None):
        return print(self.equations(fmt, context, start, stack, inbound))
    
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