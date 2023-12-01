# -*- coding: utf-8 -*-
"""
"""
import phenomenode as phn
from .variable import Variable, index as I
from .context import ContextItem, ContextStack, Contexts
from .gate import Inlets, Outlets
from .registry import Registry
from .graphics import PhenomeNodeGraphics
from .utils import AbstractMethod
from .stream import Stream, as_streams
from typing import Optional, Mapping, Callable

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
    if default_sequence is None:
        return () if variables is None else variables 
    elif variables is None: 
        return default_sequence.sequence
    else:
        if isinstance(variables, str) or not hasattr(variables, '__iter__'): variables = [variables]
        new_variables = []
        for i, d in zip(variables, default_sequence):
            if i is None and d is not None:
                new_variables.append(d)
            elif isinstance(i, str):
                new_variables.append(getattr(I, i))
            elif isinstance(i, (phn.Variable, phn.VarNode)) or hasattr(i, 'varnodes'):
                new_variables.append(i)
            else:
                raise ValueError('inlets and outlets must be variables or variable nodes')
        return new_variables

class PhenomeNode(ContextItem, tag='n'):
    __slots__ = ('ins', 'outs', 'phenomena', 'inbound', 'context', 'ancestry', 'graphics')
    registry = Registry()
    default_ins = default_outs = None
    n_ins = n_outs = None
    category = None
    
    def __init_subclass__(cls, tag=None):
        if 'priority' not in cls.__dict__: cls.priority += 1
        name = cls.__name__
        if cls.load:
            if tag is None:
                tag = name[0].lower()
            elif not isinstance(tag, str):
                raise ValueError('tag must be a string')
            elif len(tag) != 1:
                raise ValueError('tag must be a (roman or greek) letter')
            cls.tag = tag
            cls.registered_tags.add(tag)
        cls.tickets[cls.tag] = 0
        if cls.default_ins is not None and not isinstance(cls.default_ins, DefaultSequence):
            if isinstance(cls.default_ins, Mapping):
                cls.default_ins = DefaultSequence(**cls.default_ins)
            elif isinstance(cls.default_ins, str):
                cls.default_ins = DefaultSequence((getattr(I, cls.default_ins),) )
            elif hasattr(cls.default_ins, '__iter__'):
                cls.default_ins = DefaultSequence(
                    tuple([
                        getattr(I, i) if isinstance(i, str) else i 
                        for i in cls.default_ins
                    ])
                )
        if cls.default_outs is not None and not isinstance(cls.default_outs, DefaultSequence):
            if isinstance(cls.default_outs, Mapping):
                cls.default_outs = DefaultSequence(**cls.default_outs)
            elif isinstance(cls.default_outs, str):
                cls.default_outs = DefaultSequence((getattr(I, cls.default_outs),) )
            elif hasattr(cls.default_outs, '__iter__'):
                cls.default_outs = DefaultSequence(
                    tuple([
                        getattr(I, i) if isinstance(i, str) else i 
                        for i in cls.default_outs
                    ])
                )
        Contexts.append(cls)
        
    def __new__(cls, ins=None, outs=None, name=None, **kwargs):
        if cls.n_ins is not None:
            ins = [Stream() for i in range(cls.n_ins)] if ins is None else as_streams(ins)
        if cls.n_outs is not None:
            outs = [Stream() for i in range(cls.n_outs)] if outs is None else as_streams(outs)
        self = super().__new__(cls, name)
        self.prepare(ins, outs, **kwargs)
        self.registry.open_context_level()
        self.load()
        self.phenomena = self.registry.close_context_level()
        for i in self.nested_phenomena: i.ancestry.append(self)
        self.registry.register(self)
        self.ancestry = [self]
        if self.category: self.graphics = PhenomeNodeGraphics(self.category)
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
    def nested_phenomena(self):
        phenomena = self.phenomena
        if phenomena:
            return sum([i.nested_phenomena for i in self.phenomena], phenomena)
        else:
            return phenomena
    
    @property
    def varnodes(self):
        varnodes = [] 
        for i in self.ins + self.outs:
            if hasattr(i, 'varnodes'):
                varnodes.extend(i.varnodes)
            else:
                varnodes.append(i)
        return varnodes
    
    @property
    def inlet_varnodes(self):
        varnodes = [] 
        for i in self.ins:
            if hasattr(i, 'varnodes'):
                varnodes.extend(i.varnodes)
            else:
                varnodes.append(i)
        return varnodes
    
    @property
    def outlet_varnodes(self):
        varnodes = [] 
        for i in self.outs:
            if hasattr(i, 'varnodes'):
                varnodes.extend(i.varnodes)
            else:
                varnodes.append(i)
        return varnodes
    
    def proprietary_varnodes(self, filterkey):
        varnodes = [] 
        for i in self.outs:
            if hasattr(i, 'varnodes'):
                varnodes.extend(i.varnodes)
            else:
                varnodes.append(i)
        for i in self.ins:
            if hasattr(i, 'varnodes'):
                if filterkey is None:
                    for j in i.varnodes:
                        if j.sources: continue
                        varnodes.append(j)
                else:
                    for j in i.varnodes:
                        if [i for i in j.sources if not filterkey(i)]: continue
                        varnodes.append(j)
            elif filterkey is None:
                if i.sources: continue
                else: varnodes.append(i)
            elif [j for j in i.sources if not filterkey(j)]: 
                continue
            else:
                varnodes.append(i)
        return varnodes
    
    @property
    def depth(self):
        if self.phenomena:
            return 1 + max([i.depth for i in self.phenomena])
        else:
            return 0
    
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
        self.phenomena = self.registry.close_context_level()
        for i in self.nested_phenomena: i.ancestry.append(self)
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
                label_nodes: Optional[bool]=None,
                cluster: Optional[bool]=None,
                filterkey: Optional[Callable]=None,
                label_format: Optional[str]=None,
                depths: Optional[int]=None,
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
            if context_format is not None: pref.context_format = context_format
            if label_nodes is not None: pref.label_nodes = label_nodes
            if cluster is not None: pref.cluster = cluster
            if label_format is not None: pref.label_format = label_format
            f = phn.digraph_from_phenomenode(self, filterkey, depths, title=str(self), **graph_attrs)
            if display or file:
                phn.finalize_digraph(f, file, format)
            else:
                return f
    
    def show(self, context_format=None, start=None, right=True):
        with phn.preferences.temporary() as pref:
            if context_format is not None: pref.context_format = context_format
            return print(self.describe(start, right))
    
    _ipython_display_ = show
