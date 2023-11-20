# -*- coding: utf-8 -*-
"""
"""
from .variable import Variable, Variables, variable_index as index
from .varnode import VarNode as Node
from .context import Inlet, Outlet

__all__ = ('Ins', 'Outs')

class Gate:
    """
    Abstract class for a sequence of varnodes connected to a phenomenode.
    
    Abstract methods:
        * _dock(self, node) -> Node
        * _undock(self) -> None
        * _create_node(self) -> Node
        * framed_variables(self) -> list[ActiveVariables]
    
    """
    __slots__ = ('varnodes',)
        
    def __init__(self, varnodes):
        dock = self._dock
        isa = isinstance
        if isa(varnodes, Node):
            self.varnodes = [dock(varnodes)]
        elif isa(varnodes, Variable):
            self.varnodes = [dock(Node(varnodes))]
        elif isa(varnodes, str):
            self.varnodes = [dock(Node(getattr(index, varnodes)))]
        elif hasattr(varnodes, '__iter__'):
            self.varnodes = []
            for i in varnodes:
                if isa(i, Node):
                    s = dock(i)
                elif isa(i, Variable):
                    s = dock(Node(i))
                else:
                    raise TypeError(f"{i!r} is not a node")
                self.varnodes.append(s)
        else:
            raise TypeError(f"{varnodes!r} is not a list of nodes")
        
    @property
    def variables(self):
        variables = [i.variable for i in self.varnodes]
        return Variables(*variables)
        
    def _create_node(self, variable):
        return Node(variable)
        
    def __add__(self, other):
        return self.varnodes + other
    def __radd__(self, other):
        return other + self.varnodes
    
    # DO NOT DELETE: These should be implemented by child class
    # def _dock(self, node): return node
    # def _undock(self, node): pass

    def _set_nodes(self, slice, varnodes):
        varnodes = [self._as_node(i) for i in varnodes]
        all_nodes = self.varnodes
        for node in all_nodes[slice]: self._undock(node)
        all_nodes[slice] = varnodes
        for node in all_nodes: self._dock(node)
       
    def _as_node(self, node):
        if isinstance(node, Variable):
            node = self._create_node(node)
        elif not isinstance(node, Node):
            raise TypeError(
                f"'{type(self).__name__}' object can only contain "
                f"'Node' objects; not '{type(node).__name__}'"
            )
        return node
       
    @property
    def size(self):
        return self.varnodes.__len__()
    
    def __len__(self):
        return self.varnodes.__len__()
    
    def __bool__(self):
        return bool(self.varnodes)
    
    def _set_node(self, int, node):
        node = self._as_node(node)
        self._undock(self.varnodes[int])
        self.varnodes[int] = self._dock(node)
    
    def empty(self):
        for i in self.varnodes: self._undock(i)
        self.varnodes = []
    
    def insert(self, index, node):
        self._undock(node)
        self._dock(node)
        self.varnodes.insert(index, node)
    
    def append(self, node):
        self._undock(node)
        self._dock(node)
        self.varnodes.append(node)
    
    def extend(self, varnodes):
        for i in varnodes:
            self._undock(i)
            self._dock(i)
            self.varnodes.append(i)
    
    def replace(self, node, other_node):
        index = self.index(node)
        self[index] = other_node

    def index(self, node):
        return self.varnodes.index(node)

    def pop(self, index):
        varnodes = self.varnodes
        node = varnodes.pop(index)
        return node

    def remove(self, node):
        self._undock(node)
        node = self._create_node()
        self.replace(node, node)
        
    def clear(self):
        for i in self.varnodes: self._undock(i)
        self.varnodes.clear()
    
    def reverse(self):
        self.varnodes.reverse()
    
    def __iter__(self):
        return iter(self.varnodes)
    
    def __getitem__(self, index):
        return self.varnodes[index]
    
    def __setitem__(self, index, item):
        isa = isinstance
        if isa(index, int):
            self._set_node(index, item)
        elif isa(index, slice):
            self._set_nodes(index, item)
        else:
            raise IndexError("Only intergers and slices are valid "
                             f"indices for '{type(self).__name__}' objects")
    
    def __repr__(self):
        return repr(self.varnodes)


class Ins(Gate):
    """Create an Ins object which serves as inlet varnodes for a phenomenode."""
    __slots__ = ('sink',)
    
    def __init__(self, sink, varnodes):
        self.sink = sink
        super().__init__(varnodes)
    
    def framed_variables(self, family=False):
        varnodes = self.varnodes
        if not varnodes: return []
        if family:
            variables = self.variables
            context = [
                i for i in self.sink.ancestry if i.phenomena
            ]
            return variables.framed(Inlet.family + context)
        else:
            return [i.variable.framed(i.get_full_context()) for i in self.varnodes]
    
    def _create_node(self, variable):
        return Node(variable, None, [self.sink])
    
    def _dock(self, node): 
        node.sinks.appendleft(self.sink)
        return node

    def _undock(self, node): 
        if self.sink in node.sinks: 
            raise RuntimeError('undocking varnodes breaks node connections')
            node.sinks.remove(self.sink)
    
        
class Outs(Gate):
    """Create an Outs object which serves as outlet varnodes for a phenomenode."""
    __slots__ = ('source',)
    
    def __init__(self, source, varnodes):
        self.source = source
        super().__init__(varnodes)
    
    def framed_variables(self, family=False):
        varnodes = self.varnodes
        if not varnodes: return []
        if family:
            variables = self.variables
            context = [
                i for i in self.source.ancestry if i.phenomena
            ]
            return variables.framed(Outlet.family + context)
        else:
            return [i.variable.framed(i.get_full_context()) for i in self.varnodes]
            
    def _create_node(self, variable):
        return Node(variable, [self.source], None)
    
    def _dock(self, node): 
        node.sources.appendleft(self.source)
        return node
    
    def _undock(self, node): 
        if self.sources in node.sources: 
            raise RuntimeError('undocking varnodes breaks node connections')
            node.sources.remove(self.source)
        
