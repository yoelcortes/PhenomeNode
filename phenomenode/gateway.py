# -*- coding: utf-8 -*-
"""
"""
from .edge import Edge
from .context import Inlet, Outlet

class Gateway:
    """
    Abstract class for a sequence of edges for a node.
    
    Abstract methods:
        * _dock(self, edge) -> Edge
        * _undock(self) -> None
        * _create_edge(self) -> Edge
        * framed_variables(self) -> list[ActiveVariables]
    
    """
    __slots__ = ('edges',)
        
    def __init__(self, size, edges=None, etype=None):
        if etype is None: etype = Edge
        dock = self._dock
        isa = isinstance
        if edges is None:
            self.edges = [self._create_edge(etype) for i in range(size)]
        elif isa(edges, Edge):
            self.edges = [dock(edges)]
        elif hasattr(edges, '__iter__'):
            self.edges = []
            for i in edges:
                if isa(i, etype):
                    s = dock(i)
                elif i is None:
                    s = self._create_edge(etype)
                else:
                    raise TypeError(f"{i!r} is not an edge")
                self.edges.append(s)
        
    def _create_edge(self, etype):
        return etype(None, None)
        
    def __add__(self, other):
        return self.edges + other
    def __radd__(self, other):
        return other + self.edges
    
    # DO NOT DELETE: These should be implemented by child class
    # def _dock(self, edge): return edge
    
    def _undock(self, edge): 
        raise RuntimeError('undocking edges breaks node connections')

    def _set_edges(self, slice, edges):
        edges = [self._as_edge(i) for i in edges]
        all_edges = self.edges
        for edge in all_edges[slice]: self._undock(edge)
        all_edges[slice] = edges
        for edge in all_edges: self._dock(edge)
       
    def _as_edge(self, edge):
        if edge is None:
            edge = self._create_edge()
        elif not isinstance(edge, Edge):
            raise TypeError(
                f"'{type(self).__name__}' object can only contain "
                f"'Edge' objects; not '{type(edge).__name__}'"
            )
        return edge
       
    @property
    def size(self):
        return self.edges.__len__()
    
    def __len__(self):
        return self.edges.__len__()
    
    def __bool__(self):
        return bool(self.edges)
    
    def _set_edge(self, int, edge):
        edge = self._as_edge(edge)
        self._undock(self.edges[int])
        self.edges[int] = self._dock(edge)
    
    def empty(self):
        for i in self.edges: self._undock(i)
        self.edges = []
    
    def insert(self, index, edge):
        if self._fixed_size: 
            raise RuntimeError(f"size of '{type(self).__name__}' object is fixed")
        self._undock(edge)
        self._dock(edge)
        self.edges.insert(index, edge)
    
    def append(self, edge):
        if self._fixed_size: 
            raise RuntimeError(f"size of '{type(self).__name__}' object is fixed")
        self._undock(edge)
        self._dock(edge)
        self.edges.append(edge)
    
    def extend(self, edges):
        if self._fixed_size: 
            raise RuntimeError(f"size of '{type(self).__name__}' object is fixed")
        for i in edges:
            self._undock(i)
            self._dock(i)
            self.edges.append(i)
    
    def replace(self, edge, other_edge):
        index = self.index(edge)
        self[index] = other_edge

    def index(self, edge):
        return self.edges.index(edge)

    def pop(self, index):
        edges = self.edges
        if self._fixed_size:
            edge = edges[index]
            edge = self._create_edge()
            self.replace(edge, edge)
        else:
            edge = edges.pop(index)
        return edge

    def remove(self, edge):
        self._undock(edge)
        edge = self._create_edge()
        self.replace(edge, edge)
        
    def clear(self):
        for i in self.edges: self._undock(i)
        self.edges.clear()
    
    def reverse(self):
        self.edges.reverse()
    
    def __iter__(self):
        return iter(self.edges)
    
    def __getitem__(self, index):
        return self.edges[index]
    
    def __setitem__(self, index, item):
        isa = isinstance
        if isa(index, int):
            self._set_edge(index, item)
        elif isa(index, slice):
            self._set_edges(index, item)
        else:
            raise IndexError("Only intergers and slices are valid "
                             f"indices for '{type(self).__name__}' objects")
    
    def __repr__(self):
        return repr(self.edges)


class Inlets(Gateway):
    """Create an Inlets object which serves as inlet edges for a node."""
    __slots__ = ('sink',)
    
    def __init__(self, sink, size, edges, etype):
        self.sink = sink
        super().__init__(size, edges, etype)
    
    def framed_variables(self, context, family=False):
        edges = self.edges
        if not edges: return []
        if family:
            variables, = set([i.variables for i in edges]) # All variables must be the same
            return variables.framed(context + Inlet.family([i for i in range(len(edges))]))
        else:
            return [i.framed_variables(context + Inlet(n)) for n, i in enumerate(self.edges)]
    
    def _create_edge(self, etype):
        return etype(None, [self.sink])
    
    def _dock(self, edge): 
        edge.sinks.append(self.sink)
        return edge

    # def _undock(self, edge): 
    #     edge.sinks.remove(self.sink)
    
        
class Outlets(Gateway):
    """Create an Outlets object which serves as outlet edges for a node."""
    __slots__ = ('source',)
    
    def __init__(self, source, size, edges, etype):
        self.source = source
        super().__init__(size, edges, etype)
    
    def framed_variables(self, context, family=False):
        edges = self.edges
        if not edges: return []
        if family:
            variables, = set([i.variables for i in edges]) # All variables must be the same
            return variables.framed(context + Outlet.family([i for i in range(len(edges))]))
        else:
            return [i.framed_variables(context + Outlet(n)) for n, i in enumerate(self.edges)]
    
    def _create_edge(self, etype):
        return etype([self.source], None)
    
    def _dock(self, edge): 
        edge.sources.append(self.source)
        return edge
    
    # def _undock(self, edge): 
    #     edge.sources.remove(self.source)
        
