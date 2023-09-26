# -*- coding: utf-8 -*-
"""
"""
from .preferences import preferences
__all__ = ('ContextStack', 'ContextFamily', 'ContextItem',
           'Inlet', 'Outlet', 'Phase', 'Chemical', 'Contexts')

Contexts = []

def format_name(line):
    words = []
    word = ''
    last = ''
    for i in line:
        if i.isupper() and last.isalpha() and not last.isupper():
            words.append(word)
            word = i
        else:
            word += i
        last = i
    words.append(word)
    line = ''
    for word in words:
        n = len(word)
        if n > 1:
            line += word + ' '
        else:
            line += word
    line = line.strip(' ')
    words = []
    for word in line.split(' '):
        if not all([(i.isupper() or not last.isalpha()) for i in word]):
            word = word.lower()
        words.append(word)
    return ' '.join(words)


class ContextStack:
    __slots__ = ('stack',)
    
    def __new__(cls, *stack):
        self = super().__new__(cls)
        self.stack = stack
        return self
    
    @classmethod
    def from_tuple(cls, tuple):
        self = super().__new__(cls)
        self.stack = tuple
        return self
    
    def __bool__(self):
        return bool(self.stack)
    
    def __getitem__(self, index):
        return ContextStack.from_tuple(self.stack[index])
    
    def __iter__(self):
        return iter(self.stack)
    
    def __contains__(self, value):
        return value in self.stack
    
    def __add__(self, other):
        if isinstance(other, ContextStack):
            return ContextStack.from_tuple(self.stack + other.stack)
        elif other is None:
            return self
        elif isinstance(other, (ContextFamily, ContextItem)):
            return ContextStack(*self, other)
        else:
            return NotImplemented
    __iadd__ = __add__
    
    def __radd__(self, other):
        if other is None:
            return self
        elif isinstance(other, (ContextFamily, ContextItem)):
            return ContextStack(other, *self)
        else:
            return NotImplemented
    
    def __call__(self, fmt=None):
        if fmt is None: fmt = preferences.context_format
        if fmt == -1:
            return ''.join([i(fmt) for i in self])
        else:
            return ', '.join([i(fmt) for i in self])
    
    def __str__(self):
        return f"({', '.join([str(i) for i in self])})" 
    
    def __repr__(self):
        return f"{type(self).__name__}{self.stack!r}"


class ContextFamily:
    __slots__ = ('names',)
    
    def __init__(self, names):
        self.names = frozenset(names)
    
    @property
    def tag(self):
        return self.item.tag
    
    def __getitem__(self, index):
        return ContextStack.from_tuple([self][index])
    
    def __iter__(self):
        yield self
    
    def __contains__(self, value):
        return value is self
    
    def __add__(self, other):
        if isinstance(other, ContextStack):
            return ContextStack(self, *other)
        elif other is None:
            return self
        elif isinstance(other, (ContextFamily, ContextItem)):
            return ContextStack(self, other)
        else:
            return NotImplemented
    __iadd__ = __add__
    
    def __radd__(self, other):
        if other is None:
            return self
        else:
            return NotImplemented
    
    def __call__(self, fmt=None):
        if fmt is None: fmt = preferences.context_format
        if fmt == -1 or fmt == 0:
            return self.tag
        elif fmt == 1:
            return f"{self.tag} in {format_name(type(self).__name__)}"
        elif fmt == 2:
            return f"{self.tag} in {self}"
        else:
            raise ValueError('invalid context format {fmt!r}')
            
    def __str__(self):
        return f"{{{', '.join([str(i) for i in self.names])}}}" 
    
    def __repr__(self):
        names = ', '.join([repr(i) for i in self.names])
        return f"{type(self).__name__}({names})"


class ContextItem:
    __slots__ = ('name',)
    registered_tags = set()
    priority = 0
    
    def __init_subclass__(cls, tag=None, abstract=False, priority=None):
        if abstract: return
        if priority is None:
            cls.priority += 1
        else:
            cls.priority += priority
        cls.ticket = 0
        name = cls.__name__
        if tag is None: 
            tag = ''.join([i.lower() for i in name if i.isupper()])
        elif not isinstance(tag, str): 
            raise ValueError('tag must be a string')
        if tag in cls.registered_tags: 
            raise ValueError(f'tag {tag!r} already used')
        cls.tag = tag
        cls.registered_tags.add(tag)
        cls.family = type(name + 's', (ContextFamily,), {})
        cls.family.item = cls
        Contexts.append(cls)
    
    def __new__(cls, name=None):
        self = super().__new__(cls)
        self.name = self.take_ticket() if name is None else name
        return self
    
    @classmethod
    def take_ticket(cls):
        ticket = cls.ticket
        cls.ticket += 1
        return ticket
    
    __iter__ = ContextFamily.__iter__
    __contains__ = ContextFamily.__contains__
    __getitem__ = ContextFamily.__getitem__
    __iadd__ = __add__ = ContextFamily.__add__
    __radd__ = ContextFamily.__radd__
    
    def __call__(self, fmt=None):
        if fmt is None: fmt = preferences.context_format
        if fmt == -1:
            return ""
        if fmt == 0 or fmt == 1:
            return f"{self.tag}={self.name}"    
        elif fmt == 2:
            return f"{self.tag}={self}"
        else:
            raise ValueError(f'invalid context format {fmt!r}')
    
    def __str__(self):
        return f"{type(self).__name__}({self.name})"
    
    def __repr__(self):
        return f"{type(self).__name__}({self.name!r})" 


class Inlet(ContextItem): pass
class Outlet(ContextItem): pass
class Phase(ContextItem): pass
class Chemical(ContextItem): pass
