# -*- coding: utf-8 -*-
# BioSTEAM: The Biorefinery Simulation and Techno-Economic Analysis Modules
# Copyright (C) 2020-2023, Yoel Cortes-Pena <yoelcortes@gmail.com>
# 
# This module is under the UIUC open-source license. See 
# github.com/BioSTEAMDevelopmentGroup/biosteam/blob/master/LICENSE.txt
# for license details.
"""
This module includes classes and functions concerning Stream objects.
"""
from __future__ import annotations
from .varnode import VarNode
from .variable import Variables, variable_index as index

__all__ = ('Stream', 'Inlets', 'Outlets', 'Sink', 'Source', 'InletPort', 'OutletPort',
           'StreamPorts', 'SuperpositionInlet', 'SuperpositionOutlet')
        

# %% Utilities

def pipe_info(source, sink):
    """Return stream information header."""
    # First line
    if source is None:
        source = ''
    else:
        source = f' from {repr(source)}'
    if sink is None:
        sink = ''
    else:
        sink = f' to {repr(sink)}'
    return f"{source}{sink}"

    
# %% Streams

class Stream:
    """Create a stream which defines associated variables."""
    __slots__ = ('Fcp', 'T', 'P', 'varnodes', 'source', 'sink')
    
    def __init__(self, source=None, sink=None):
        self.source = source
        self.sink = sink
        sources = [source] if source else None
        sinks = [sink] if sink else None
        self.Fcp = Fcp = VarNode(index.Fcp, sources, sinks)
        self.T = T = VarNode(index.T, sources, sinks)
        self.P = P = VarNode(index.P, sources, sinks)
        self.varnodes = (Fcp, T, P)
        
    def __repr__(self):
        return f"{type(self).__name__}({self.Fcp!r}, {self.T!r}, {self.P!r})"
        

# %% Utilities

def n_missing(ub, N):
    if ub < N: raise RuntimeError(f"size of streams exceeds {ub}")
    return ub - N

# %% List objects for input and output streams

def as_streams(streams):
    isa = isinstance
    if isa(streams, Stream):
        return [streams]
    else:
        loaded_streams = []
        for i in streams:
            if isa(i, Stream):
                pass
            elif i is None:
                s = Stream(None, None)
            else:
                raise ValueError('only stream objects are valid')
            loaded_streams.append(s)
    return loaded_streams

class StreamSequence:
    """
    Abstract class for a sequence of streams for a Unit object.
    
    Abstract methods:
        * _dock(self, stream) -> Stream
        * _redock(self, stream) -> Stream
        * _undock(self) -> None
        * _load_stream(self)
    
    """
    __slots__ = ('streams',)
        
    def __init__(self, streams):
        redock = self._redock
        self.streams = [redock(i) for i in streams]
        
    def __add__(self, other):
        return self.streams + other
    def __radd__(self, other):
        return other + self.streams
    
    # DO NOT DELETE: These should be implemented by child class
    # def _dock(self, stream): return stream
    # def _redock(self, stream): return stream
    # def _undock(self, stream): pass

    def _set_streams(self, slice, streams):
        streams = [self._as_stream(i) for i in streams]
        all_streams = self.streams
        for stream in all_streams[slice]: self._undock(stream)
        all_streams[slice] = streams
        for stream in all_streams: self._redock(stream)
       
    def _as_stream(self, stream):
        if stream is None:
            stream = self._create_stream()
        elif not isinstance(stream, Stream):
            raise TypeError(
                f"'{type(self).__name__}' object can only contain "
                f"'Stream' objects; not '{type(stream).__name__}'"
            )
        return stream
       
    @property
    def size(self):
        return self.streams.__len__()
    
    def __len__(self):
        return self.streams.__len__()
    
    def __bool__(self):
        return bool(self.streams)
    
    def _set_stream(self, int, stream):
        stream = self._as_stream(stream)
        self._undock(self.streams[int])
        self.streams[int] = self._redock(stream)
    
    def empty(self):
        for i in self.streams: self._undock(i)
        self._initialize_streams()
    
    def insert(self, index, stream):
        self._undock(stream)
        self._dock(stream)
        self.streams.insert(index, stream)
    
    def append(self, stream):
        self._undock(stream)
        self._dock(stream)
        self.streams.append(stream)
    
    def extend(self, streams):
        for i in streams:
            self._undock(i)
            self._dock(i)
            self.streams.append(i)
    
    def replace(self, stream, other_stream):
        index = self.index(stream)
        self[index] = other_stream

    def index(self, stream):
        return self.streams.index(stream)

    def pop(self, index):
        streams = self.streams
        stream = streams.pop(index)
        return stream

    def remove(self, stream):
        self._undock(stream)
        stream = self._create_stream()
        self.replace(stream, stream)
        
    def clear(self):
        for i in self.streams: self._undock(i)
        self.streams.clear()
    
    def reverse(self):
        self.streams.reverse()
    
    def __iter__(self):
        return iter(self.streams)
    
    def __getitem__(self, index):
        return self.streams[index]
    
    def __setitem__(self, index, item):
        isa = isinstance
        if isa(index, int):
            self._set_stream(index, item, 2)
        elif isa(index, slice):
            self._set_streams(index, item, 2)
        else:
            raise IndexError("Only intergers and slices are valid "
                             f"indices for '{type(self).__name__}' objects")
    
    def __repr__(self):
        return repr(self.streams)


class Inlets(StreamSequence):
    """Create an Inlets object which serves as input streams for a Unit object."""
    __slots__ = ('sink', '_fixed_size')
    
    def __init__(self, sink, streams):
        self.sink = sink
        super().__init__(streams)
    
    def _create_stream(self):
        return Stream(None, self.sink)
    
    def _dock(self, stream): 
        stream.sink = self.sink
        return stream

    def _redock(self, stream): 
        sink = stream.sink
        if sink:
            inlets = sink.inlets
            if inlets is not self and stream in inlets: inlets.remove(stream)
        stream.sink = self.sink
        return stream
    
    def _undock(self, stream): 
        stream.sink = None
    
        
class Outlets(StreamSequence):
    """Create an Outlets object which serves as output streams for a Unit object."""
    __slots__ = ('source',)
    
    def __init__(self, source, streams):
        self.source = source
        super().__init__(streams)
    
    def _create_stream(self):
        return Stream(self.source, None)
    
    def _dock(self, stream): 
        stream.source = self.source
        return stream

    def _redock(self, stream): 
        source = stream.source
        if source:
            outlets = source.outlets
            if outlets is not self and stream in outlets: outlets.remove(stream)
        stream.source = self.source
        return stream
    
    def _undock(self, stream): 
        stream.source = None


# %% Sink and Source object for piping notation

class Sink:
    """Create a Sink object that connects a stream to a unit using piping
    notation."""
    __slots__ = ('stream', 'index')
    def __init__(self, stream, index):
        self.stream = stream
        self.index = index

    # Forward pipping
    def __sub__(self, unit):
        unit.inlets[self.index] = self.stream
        return unit
    
    # Backward pipping
    __pow__ = __sub__
    
    def __repr__(self):
        return f'<{ type(self).__name__}: {self.index}>'


class Source:
    """Create a Source object that connects a stream to a unit using piping
    notation."""
    __slots__ = ('stream', 'index')
    def __init__(self, stream, index):
        self.stream = stream
        self.index = index

    # Forward pipping
    def __rsub__(self, unit):
        unit.outlets[self.index] = self.stream
        return unit
    
    # Backward pipping
    __rpow__ = __rsub__
    
    def __repr__(self):
        return f'<{ type(self).__name__}: {self.index}>'
    

# %% System pipping

class InletPort:
    __slots__ = ('sink', 'index')
    
    @classmethod
    def from_inlet(cls, inlet):
        sink = inlet.sink
        if not sink: raise ValueError(f'stream {inlet} is not an inlet to any unit')
        index = sink.inlets.index(inlet)
        return cls(sink, index)
    
    def __init__(self, sink, index):
        self.sink = sink
        self.index = index
      
    def __eq__(self, other):
        return self.sink is other.sink and self.index == other.index  
      
    def _sorting_key(self):
        return (self.sink.ID[1:], self.sink.ID, self.index)
        
    def get_stream(self):
        return self.sink.inlets[self.index]
    
    def set_stream(self, stream):
        self.sink.inlets._set_stream(self.index, stream)
    
    def __str__(self):
        return f"{self.index}-{self.sink}"
    
    def __repr__(self):
        return f"{type(self).__name__}({self.sink}, {self.index})"


class OutletPort:
    __slots__ = ('source', 'index')
    
    @classmethod
    def from_outlet(cls, outlet):
        source = outlet.source
        if not source: raise ValueError(f'stream {outlet} is not an outlet to any unit')
        index = source.outlets.index(outlet)
        return cls(source, index)
    
    def __init__(self, source, index):
        self.source = source
        self.index = index
    
    def __eq__(self, other):
        return self.source is other.source and self.index == other.index
    
    def get_stream(self):
        return self.source.outlets[self.index]
    
    def set_stream(self, stream):
        self.source.outlets._set_stream(self.index, stream)
    
    def __str__(self):
        return f"{self.source}-{self.index}"
    
    def __repr__(self):
        return f"{type(self).__name__}({self.source}, {self.index})"


class StreamPorts:
    __slots__ = ('_ports',)
    
    @classmethod
    def from_inlets(cls, inlets, sort=None):
        return cls([InletPort.from_inlet(i) for i in inlets], sort)
    
    @classmethod
    def from_outlets(cls, outlets, sort=None):
        return cls([OutletPort.from_outlet(i) for i in outlets], sort)
    
    def __init__(self, ports, sort=None):
        self._ports = tuple(ports)    
    
    def __bool__(self):
        return bool(self._ports)
        
    def __iter__(self):
        for i in self._ports: yield i.get_stream()
    
    def __len__(self):
        return len(self._ports)
    
    def __getitem__(self, index):
        if isinstance(index, slice):
            return self.__class__(self._ports[index])
        else:
            return self._ports[index].get_stream()
    
    def __setitem__(self, index, item):
        isa = isinstance
        if isa(index, int):
            self._set_stream(index, item, 2)
        elif isa(index, slice):
            self._set_streams(index, item, 2)
        else:
            raise IndexError("Only intergers and slices are valid "
                            f"indices for '{type(self).__name__}' objects")
          
    def _set_stream(self, int, stream):
        self._ports[int].set_stream(stream)
    
    def _set_streams(self, slice, streams):
        ports = self._ports[slice]
        if len(streams) == len(ports):
            for i, j in zip(ports, streams): i.set_stream(j)
        else:
            raise IndexError("number of inlets must match the size of slice")
    
    def __repr__ (self):
        ports = ', '.join([str(i) for i in self._ports])
        return f"[{ports}]"


# %% Auxiliary piping

def superposition_property(name):
    @property
    def p(self):
        return getattr(self.port.get_stream(), name)
    @p.setter
    def p(self, value):
        setattr(self.port.get_stream(), name, value)
        
    return p

def _superposition(cls, parent, port):
    excluded = set([*cls.__dict__, port, '_' + port, 'port'])
    for name in parent.__dict__:
        if name in excluded: continue
        setattr(cls, name, superposition_property(name))
    return cls

def superposition(parent, port):
    return lambda cls: _superposition(cls, parent, port)


@superposition(Stream, 'sink')
class SuperpositionInlet(Stream): 
    """Create a SuperpositionInlet that references an inlet from another 
    unit operation."""
    __slots__ = ()
    
    def __init__(self, port, sink=None):
        self.port = port
        self.sink = sink
      

@superposition(Stream, 'source')
class SuperpositionOutlet(Stream):
    """Create a SuperpositionOutlet that references an outlet from another 
    unit operation."""
    __slots__ = ()
    
    def __init__(self, port, source=None):
        self.port = port
        self.source = source
    

# %% Stream pipping
        
def __sub__(self, index):
    if isinstance(index, int):
        return Sink(self, index)
    elif isinstance(index, Stream):
        new = self.copy()
        new.separate_out(index)   
        return new
    else:
        return index.__rsub__(self)

def __rsub__(self, index):
    if isinstance(index, int):
        return Source(self, index)
    else:
        return index.__sub__(self)

basic_stream_info = lambda self: (f"{type(self).__name__}: {self.ID or ''}"
                                  f"{pipe_info(self.source, self.sink)}\n")

