# -*- coding: utf-8 -*-
"""
"""
import phenomenode as phn
from .variable import Variable, variable_index
from .context import ContextItem, ContextStack, Contexts
from .gate import Inlets, Outlets
from .registry import Registry
from .graphics import material_graphics
from .utils import AbstractMethod
from typing import Optional, Mapping

__all__ = ('PhenomeNode',)

class DefaultSequence:
    __slots__ = ('sequence', 'default')
    
    def __init__(self, sequence=(), default=None):
        self.sequence = sequence
        self.default = default
    
    def __iter__(self):
        yield from self.sequence
        while True: yield self.default
        
    def __repr__(self):
        return f"{type(self).__name__}({self.sequence!r}, {self.default!r})"


def default_variables(variables, default_sequence):
    if variables is None: 
        return default_sequence.sequence
    else:
        if isinstance(variables, str) or not hasattr(variables, '__iter__'): variables = [variables]
        new_variables = []
        for i, d in zip(variables, default_sequence):
            if i is None and d is not None:
                new_variables.append(d)
            elif isinstance(i, str):
                new_variables.append(getattr(variable_index, i))
            elif isinstance(i, (phn.Variable, phn.VarNode)) or hasattr(i, 'varnodes'):
                new_variables.append(i)
            else:
                raise ValueError('inlets and outlets must be variables or variable nodes')
        return new_variables

class PhenomeNode(ContextItem, tag='n'):
    __slots__ = ('ins', 'outs', 'phenomena', 'inbound', 'context')
    graphics = material_graphics
    registry = Registry()
    default_ins = DefaultSequence()
    default_outs = DefaultSequence()
    
    def __init_subclass__(cls, tag=None, priority=None):
        if priority is None:
            cls.priority += 1
        else:
            cls.priority += priority
        cls.ticket = 0
        name = cls.__name__
        if cls.load:
            if tag is None:
                tag = name[0].lower()
            elif not isinstance(tag, str):
                raise ValueError('tag must be a string')
            elif len(tag) != 1:
                raise ValueError('tag must be a (roman or greek) letter')
            if tag in cls.registered_tags: 
                raise ValueError(f'tag {tag!r} already used')
            cls.tag = tag
            cls.registered_tags.add(tag)
        else:
            cls.tag = None
        if not isinstance(cls.default_ins, DefaultSequence):
            if isinstance(cls.default_ins, Mapping):
                cls.default_ins = DefaultSequence(**cls.default_ins)
            elif isinstance(cls.default_ins, str):
                cls.default_ins = DefaultSequence((getattr(variable_index, cls.default_ins),) )
            elif hasattr(cls.default_ins, '__iter__'):
                cls.default_ins = DefaultSequence(
                    tuple([
                        getattr(variable_index, i) if isinstance(i, str) else i 
                        for i in cls.default_ins
                    ])
                )
        if not isinstance(cls.default_outs, DefaultSequence):
            if isinstance(cls.default_outs, Mapping):
                cls.default_outs = DefaultSequence(**cls.default_outs)
            elif isinstance(cls.default_outs, str):
                cls.default_outs = DefaultSequence((getattr(variable_index, cls.default_outs),) )
            elif hasattr(cls.default_outs, '__iter__'):
                cls.default_outs = DefaultSequence(
                    tuple([
                        getattr(variable_index, i) if isinstance(i, str) else i 
                        for i in cls.default_outs
                    ])
                )
        Contexts.append(cls)
    
    def __new__(cls, ins=None, outs=None, name=None, **kwargs):
        self = super().__new__(cls, name)
        self.prepare(ins, outs, **kwargs)
        self.registry.open_context_level()
        self.load()
        self.phenomena = self.registry.close_context_level()
        for i in self.phenomena: i.ancestry.append(i)
        self.registry.register(self)
        self.ancestry = [self]
        return self
    
    def prepare(self, ins, outs, **kwargs):
        """Initialize edges and any additional parameters. 
        This method is called before `load`"""
        for i, j in kwargs.items(): setattr(self, i, j)
        self.init_ins(ins)
        self.init_outs(outs)
    
    def init_ins(self, ins):
        self.ins = Inlets(
            self, default_variables(ins, self.default_ins)
        )
        
    def init_outs(self, outs):
        self.outs = Outlets(
            self, default_variables(outs, self.default_outs)
        )
    
    @property
    def varnodes(self):
        varnodes = [] 
        for i in self.ins + self.outs:
            if hasattr(i, 'varnodes'):
                varnodes.extend(i.varnodes)
            else:
                varnodes.append(i)
        return varnodes
    
    #: Abstract method for loading phenomena. This method is called after `init`
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
        if context is None: # First context is trivial
            return ContextStack()
        elif self.phenomena and not (isinstance(context, ContextStack) and self in context.stack):
            # Must be a unit operation with internal phenomena
            return self + context
        else: # Must be the phenomenon itself, so it does not need context
            return context
    
    def __enter__(self):
        if self.phenomena or self.ins or self.outs:
            raise RuntimeError("only empty phenomena can enter `with` statement")
        self.registry.open_context_level()
        return self

    def __exit__(self, type, exception, traceback):
        if self.phenomena or self.ins or self.outs:
            raise RuntimeError('node was modified before exiting `with` statement')
        self.phenomena = phenomena = tuple(self.registry.close_context_level())
        inlets = sum([i.ins for i in phenomena], [])
        feeds = [i for i in inlets if not i.sources]
        outlets = sum([i.outs for i in phenomena], [])
        products = [i for i in outlets if not i.sinks]   
        self.ins.edges[:] = feeds
        self.outs.edges[:] = products
        for i in feeds: i.sinks.append(self)
        for i in products: i.sources.append(self)
        if exception: raise exception
    
    def _equations_format(self, start):
        head = f"{type(self).__name__}({self:n}):"
        if start is None:
            dlim = '\n'
            start = '  '
        else:
            dlim = '\n' + start 
            start += '  '
        return head, dlim, start
    
    def inlet_variables(self):
        return self.ins.framed_variables()
    
    def outlet_variables(self):
        return self.outs.framed_variables()
    
    def describe(self, start=None, right=None):
        first = start is None
        head, dlim, start = self._equations_format(start)
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
        if self.phenomena:
            eqs += dlim + dlim.join([i.describe(start, right) for i in self.phenomena])
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
            f = phn.digraph_from_phenomenode(self, title=str(self), **graph_attrs)
            if display or file:
                def size(node):
                    phenomena = node.phenomena
                    N = len(phenomena)
                    for n in phenomena: N += size(n)
                    return N
                N = size(self)
                if N < 3:
                    size_key = 'node'
                elif N < 8:
                    size_key = 'network'
                else:
                    size_key = 'big-network'
                # import dot2tex
                # texcode = dot2tex.dot2tex(f.source)
                height = (
                    phn.preferences.graphviz_html_height
                    [size_key]
                    [phn.preferences.tooltips_full_results]
                )
                phn.finalize_digraph(f, file, format, height)
            else:
                return f
    
    def show(self, context_format=None, start=None, right=True):
        with phn.preferences.temporary() as pref:
            if context_format is not None: pref.context_format = context_format
            return print(self.describe(start, right))
    
    _ipython_display_ = show
