# -*- coding: utf-8 -*-
"""
"""
from .variable import Variable, index as I
from .varnode import VarNode as Node

__all__ = ('Inlets', 'Outlets')

class Gate:
    """
    Abstract class for a sequence of nodes connected to a phenomenode.
    
    Abstract methods:
        * _dock(self, node) -> Node
        * _undock(self) -> None
        * _create_node(self) -> Node
        * framed_variables(self) -> list[ActiveVariables]
    
    """
    __slots__ = ('nodes',)
        
    def __init__(self, nodes):
        dock = self._dock
        isa = isinstance
        if isa(nodes, Node) or hasattr(nodes, 'varnodes'):
            self.nodes = [dock(nodes)]
        elif isa(nodes, Variable):
            self.nodes = [dock(Node(nodes))]
        elif isa(nodes, str):
            self.nodes = [dock(Node(getattr(I, nodes)))]
        elif hasattr(nodes, '__iter__'):
            self.nodes = []
            for i in nodes:
                if isa(i, Node) or hasattr(i, 'varnodes'):
                    s = dock(i)
                elif isa(i, Variable):
                    s = dock(Node(i))
                elif isa(nodes, str):
                    s = dock(Node(getattr(I, nodes)))
                elif hasattr(i, '__iter__'):
                    s = dock(i)
                else:
                    raise TypeError(f"{i!r} is not a node")
                self.nodes.append(s)
        else:
            raise TypeError(f"nodes must be a list of nodes; not a {type(nodes).__name__!r} object")
        
    @property
    def varnodes(self):
        varnodes = []
        for i in self.nodes:
            if hasattr(i, 'varnodes'):
                varnodes.extend(i.varnodes)
            elif hasattr(i, '__iter__'):
                varnodes.extend(i)
            else:
                varnodes.append(i)
        return varnodes
    
    def framed_variables(self):
        variables = []
        for i in self.nodes:
            if hasattr(i, 'varnodes'):
                variables.append([i.variable.framed(i.get_full_context()) for i in i.varnodes])
            elif hasattr(i, '__iter__'):
                variables.append([i.variable.framed(i.get_full_context()) for i in i])
            else:
                variables.append(i.variable.framed(i.get_full_context()))
        return variables
    
    def _create_node(self, variable):
        return Node(variable)
        
    def __add__(self, other):
        return self.nodes + other
    def __radd__(self, other):
        return other + self.nodes
    
    # DO NOT DELETE: These should be implemented by child class
    # def _dock(self, node): return node
    # def _undock(self, node): pass

    def _set_nodes(self, slice, nodes):
        nodes = [self._as_node(i) for i in nodes]
        all_nodes = self.nodes
        for node in all_nodes[slice]: self._undock(node)
        all_nodes[slice] = nodes
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
        return self.nodes.__len__()
    
    def __len__(self):
        return self.nodes.__len__()
    
    def __bool__(self):
        return bool(self.nodes)
    
    def _set_node(self, int, node):
        node = self._as_node(node)
        self._undock(self.nodes[int])
        self.nodes[int] = self._dock(node)
    
    def empty(self):
        for i in self.nodes: self._undock(i)
        self.nodes = []
    
    def insert(self, index, node):
        self._undock(node)
        self._dock(node)
        self.nodes.insert(index, node)
    
    def append(self, node):
        self._undock(node)
        self._dock(node)
        self.nodes.append(node)
    
    def extend(self, nodes):
        for i in nodes:
            self._undock(i)
            self._dock(i)
            self.nodes.append(i)
    
    def replace(self, node, other_node):
        index = self.index(node)
        self[index] = other_node

    def index(self, node):
        return self.nodes.index(node)

    def pop(self, index):
        nodes = self.nodes
        node = nodes.pop(index)
        return node

    def remove(self, node):
        self._undock(node)
        node = self._create_node()
        self.replace(node, node)
        
    def clear(self):
        for i in self.nodes: self._undock(i)
        self.nodes.clear()
    
    def reverse(self):
        self.nodes.reverse()
    
    def __iter__(self):
        return iter(self.nodes)
    
    def __getitem__(self, index):
        return self.nodes[index]
    
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
        return repr(self.nodes)


class Inlets(Gate):
    """Create an Inlets object which serves as inlet nodes for a phenomenode."""
    __slots__ = ('sink',)
    
    def __init__(self, sink, nodes):
        self.sink = sink
        super().__init__(nodes)
    
    def _create_node(self, variable):
        return Node(variable, None, [self.sink])
    
    def _dock(self, node):
        if hasattr(node, 'varnodes'):
            for i in node.varnodes: self._dock(i)
        elif hasattr(node, '__iter__'):
            for i in node: self._dock(i)
        else:
            node.sinks.appendleft(self.sink)
        return node

    def _undock(self, node): 
        if self.sink in node.sinks: 
            raise RuntimeError('undocking nodes breaks node connections')
            node.sinks.remove(self.sink)
    
        
class Outlets(Gate):
    """Create an Outlets object which serves as outlet nodes for a phenomenode."""
    __slots__ = ('source',)
    
    def __init__(self, source, nodes):
        self.source = source
        super().__init__(nodes)
            
    def _create_node(self, variable):
        return Node(variable, [self.source], None)
    
    def _dock(self, node): 
        if hasattr(node, 'varnodes'):
            for i in node.varnodes: self._dock(i)
        elif hasattr(node, '__iter__'):
            for i in node: self._dock(i)
        else:
            node.sources.appendleft(self.source)
        return node
    
    def _undock(self, node): 
        if self.sources in node.sources: 
            raise RuntimeError('undocking nodes breaks node connections')
            node.sources.remove(self.source)
        
