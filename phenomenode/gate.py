# -*- coding: utf-8 -*-
"""
"""
from .variable import Variables
from .edge import Edge
from .context import Inlet, Outlet, ContextStack

__all__ = ('Inlets', 'Outlets')

class Gate:
    """
    Abstract class for a sequence of edges entering or exiting a node.
    
    Abstract methods:
        * _dock(self, edge) -> Edge
        * _undock(self) -> None
        * _create_edge(self) -> Edge
        * framed_variables(self) -> list[ActiveVariables]
    
    """
    __slots__ = ('edges',)
        
    def __init__(self, size, edges=None, index=None, variables=None):
        dock = self._dock
        isa = isinstance
        if edges is None:
            self.edges = [self._create_edge(index, variables) for i in range(size)]
        elif isa(edges, Edge):
            self.edges = [dock(edges)]
        elif hasattr(edges, '__iter__'):
            self.edges = []
            for i in edges:
                if isa(i, Edge):
                    s = dock(i)
                elif i is None:
                    s = self._create_edge(index, variables)
                else:
                    raise TypeError(f"{i!r} is not an edge")
                self.edges.append(s)
        
    @property
    def variables(self):
        variables = []
        for i in self.edges: variables.extend(i.variables)
        return Variables(*variables)
        
    def _create_edge(self, index, variables):
        return Edge(None, None, index, variables)
        
    def __add__(self, other):
        return self.edges + other
    def __radd__(self, other):
        return other + self.edges
    
    # DO NOT DELETE: These should be implemented by child class
    # def _dock(self, edge): return edge
    # def _undock(self, edge): pass

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
        self._undock(edge)
        self._dock(edge)
        self.edges.insert(index, edge)
    
    def append(self, edge):
        self._undock(edge)
        self._dock(edge)
        self.edges.append(edge)
    
    def extend(self, edges):
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


class Inlets(Gate):
    """Create an Inlets object which serves as inlet edges for a node."""
    __slots__ = ('sink',)
    
    def __init__(self, sink, size, edges, index, variables):
        self.sink = sink
        super().__init__(size, edges, index, variables)
    
    def framed_variables(self, context, family=False):
        edges = self.edges
        if not edges: return []
        if family:
            variables = self.variables
            return variables.framed(Inlet.family + context)
        else:
            return [i.framed_variables(Inlet(n) + context) for n, i in enumerate(self.edges)]
    
    def _create_edge(self, index, variables):
        return Edge(None, [self.sink], index, variables)
    
    def _dock(self, edge): 
        edge.sinks.appendleft(self.sink)
        return edge

    def _undock(self, edge): 
        if self.sink in edge.sinks: 
            raise RuntimeError('undocking edges breaks node connections')
            edge.sinks.remove(self.sink)
    
        
class Outlets(Gate):
    """Create an Outlets object which serves as outlet edges for a node."""
    __slots__ = ('source',)
    
    def __init__(self, source, size, edges, index, variables):
        self.source = source
        super().__init__(size, edges, index, variables)
    
    def framed_variables(self, context, family=False, inbound=None):
        edges = self.edges
        if not edges: return []
        if inbound is None: inbound = True
        if family:
            variables = self.variables
            return variables.framed(Outlet.family + context)
        elif inbound:
            return [
                i.framed_variables(
                    Inlet(i.sinks[0].ins.index(i)) +
                    sum(i.sinks, None)
                    if i.sinks else 
                    Outlet(n) + context
                )
                for n, i in enumerate(self.edges)
            ]
        else:
            return [
                i.framed_variables(Outlet(n) + context)
                for n, i in enumerate(self.edges)
            ]
            
    
    def _create_edge(self, index, variables):
        return Edge([self.source], None, index, variables)
    
    def _dock(self, edge): 
        edge.sources.appendleft(self.source)
        return edge
    
    def _undock(self, edge): 
        if self.sources in edge.sources: 
            raise RuntimeError('undocking edges breaks node connections')
            edge.sources.remove(self.source)
        
