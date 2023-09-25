# -*- coding: utf-8 -*-
"""
"""

class Registry:
    __slots__ = ('contexts', 'context_levels')
        
    def __init__(self, contexts=None):
        self.context_levels = []
        self.contexts = [] if contexts is None else contexts
        
    def register(self, obj):
        """Register object without warnings or checks."""
        if obj not in self.contexts:
            self.contexts.append(obj)
    
    def open_context_level(self):
        contexts = self.contexts
        self.contexts = []
        self.context_levels.append(contexts)
        
    def close_context_level(self):
        contexts = self.contexts
        self.contexts = self.context_levels.pop()
        return contexts
    
    def __contains__(self, obj):
        obj in self.contexts
    
    def __iter__(self):
        return iter(self.contexts)
    
    def __repr__(self):
        return f"{type(self).__name__}([{', '.join([repr(i) for i in self])}])"
    
    def show(self):
        if self.contexts:
            print(f'{type(self).__name__}:\n' + '\n'.join([str(i) for i in self]))
        else:
            print(f'{type(self).__name__}: (Empty)')
    
    _ipython_display_ = show
