# -*- coding: utf-8 -*-
"""
"""
from .context import ContextStack, Chemical, Phase
from .variable import Variable
class Edge:
    __slots__ = ('sources', 'sinks', 'variables')
    
    def __init__(self, sources=None, sinks=None, variables=None):
        self.sources = [] if sources is None else sources
        self.sinks = [] if sinks is None else sinks
        self.variables = () if variables is None else variables
    
    def __call__(self, fmt=None, context=None, dlim=None):
        if dlim is None: dlim = '\n'
        return dlim.join([
            variable(fmt, context)
            for variable in self.variables
        ])
    
    def framed_variables(self, context=None):
        return self.variables.framed(context)
    
    def show(self, fmt=None):
        head = f"{type(self).__name__}: "
        dlim = '\n' + len(head) * ' '
        return print(
            head + self(fmt, dlim=dlim)
        )
    _ipython_display_ = show

    def __repr__(self):
        return f"{type(self).__name__}({self.sources!r}, {self.sinks!r})"


class ActiveVariables(frozenset):
    
    def __new__(cls, *variables):
        self = super().__new__(cls, variables)
        for i in variables: setattr(self, i(-1), i)
        return self
    
    def framed(self, context=None):
        if context is None: return self
        return ActiveVariables(*[i.framed(context) for i in self])
    

class Stream(Edge):
    __slots__ = (
        'chemicals', 'phases',
    )
    default_chemicals = Chemical.family(['Water'])
    default_phases = Phase.family(['g', 'l'])
    T = Variable('T')
    P = Variable('P')
    H = Variable('H')
    S = Variable('S')
    G = Variable('G')
    A = Variable('A')
    V = Variable('V')
    F = Variable('F')
    
    @property
    def Fcp(self):
        return Variable('F', ContextStack(self.chemicals, self.phases))
    @property
    def Fc(self):
        return Variable('F', self.chemicals)
    
    def __init__(self, sources=None, sinks=None, chemicals=None, phases=None,
                 variables=None):
        if chemicals is None: chemicals = self.default_chemicals
        if phases is None: phases = self.default_phases
        self.chemicals = chemicals
        self.phases = phases
        if variables is None: variables = ActiveVariables(self.Fcp, self.T, self.P)
        super().__init__(sources, sinks, variables)
