# -*- coding: utf-8 -*-
"""
"""
from .preferences import preferences
from typing import Iterable
__all__ = ('ContextStack', 'ContextFamily', 'ContextItem', 'Number',
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
        elif isinstance(other, context_types):
            if other in self.stack:
                breakpoint()
            return ContextStack(*self, other)
        elif isinstance(other, Iterable):
            for i in other:
                if isinstance(i, context_types): continue
                raise ValueError('only contexts can be added; not {type(i).__name__} objects')
            return ContextStack(*self.stack, *other)
        else:
            return NotImplemented
    __iadd__ = __add__
    
    def __radd__(self, other):
        if other is None:
            return self
        elif isinstance(other, context_types):
            return ContextStack(other, *self)
        elif isinstance(other, '__iter__'):
            for i in other:
                if isinstance(i, context_types): continue
                raise ValueError('only contexts can be added; not {type(i).__name__} objects')
            return ContextStack(*self.stack, *other)
        else:
            return NotImplemented
    
    def __format__(self, fmt):
        if fmt == '': fmt = preferences.context_format
        if fmt == 's':
            return ''.join([format(i, fmt) for i in self])
        else:
            return ', '.join([format(i, fmt) for i in self])
        
    def __str__(self):
        return format(self, preferences.context_format)
        
    def __repr__(self):
        return f"{type(self).__name__}{self.stack!r}"


class ContextFamily:
    __slots__ = ()
    
    def __add__(self, other):
        if isinstance(other, ContextStack):
            return ContextStack(self, *other.stack)
        elif other is None:
            return self
        elif isinstance(other, context_types):
            return ContextStack(self, other)
        elif isinstance(other, Iterable):
            for i in other:
                if isinstance(i, context_types): continue
                raise ValueError('only contexts can be added; not {type(i).__name__} objects')
            return ContextStack(self, *other)
        else:
            return NotImplemented
    __iadd__ = __add__
    
    def __radd__(self, other):
        if other is None:
            return self
        else:
            return NotImplemented
      
    def __format__(self, fmt):
        if fmt == '': fmt = preferences.context_format
        if fmt in ('s', 'n', 'l', 'h'):
            return self.tag
        elif fmt == 'f':
            return f"{format_name(type(self).__name__)}"
        else:
            raise ValueError(f'invalid context format {fmt!r}')
            
    def __str__(self):
        return format(self, preferences.context_format)
        
    
    def __repr__(self):
        return f"{type(self).__name__}()"


class ContextItem:
    __slots__ = ('name',)
    registered_tags = set()
    priority = 0
    tickets = {}

    @property
    def ticket(self):
        return self.tickets[self.tag]
    @ticket.setter
    def ticket(self, ticket):
        self.tickets[self.tag] = ticket
        
    def __init_subclass__(cls, tag=None, abstract=False, priority=None):
        if abstract: return
        if priority is None:
            cls.priority += 1
        else:
            cls.priority += priority
        name = cls.__name__
        if tag == 'None':
            tag = None
        elif tag is None:
            tag = name[0].lower()
        elif not isinstance(tag, str):
            raise ValueError('tag must be a string')
        elif len(tag) != 1:
            raise ValueError('tag must be a (roman or greek) letter')
        if tag in cls.registered_tags: 
            raise ValueError(f'tag {tag!r} already used')
        cls.tag = tag
        cls.registered_tags.add(tag)
        cls.tickets[cls.tag] = 0
        cls.family = type(name + 's', (ContextFamily,), {'tag': tag})()
        Contexts.append(cls)
    
    def __new__(cls, name=None):
        self = super().__new__(cls)
        self.name = self.take_ticket() if name is None else name
        return self
    
    def take_ticket(self):
        ticket = self.ticket
        self.ticket += 1
        return ticket
    
    __iadd__ = __add__ = ContextFamily.__add__
    __radd__ = ContextFamily.__radd__
    
    def __format__(self, fmt):
        if fmt == '': fmt = preferences.context_format
        if fmt == 's':
            return ""
        elif fmt == 'n' or fmt == 'l' or fmt == 'h':
            name = self.name
            if isinstance(name, str):
                return name
            elif self.tag:
                return f"{self.tag}={name}"    
            else:
                return str(name)
        elif fmt == 'f':
            return str(self)
        else:
            raise ValueError(f'invalid context format {fmt!r}')
            
    def __str__(self):
        return f"{type(self).__name__}({self:n})" 
    
    def __repr__(self):
        return f"{type(self).__name__}({self.name!r})" 


class Inlet(ContextItem): pass
class Outlet(ContextItem): pass
class Phase(ContextItem): pass
class Chemical(ContextItem): pass
class Number(ContextItem, tag='None'): pass

context_types = (ContextFamily, ContextItem)