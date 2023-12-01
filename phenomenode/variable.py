# -*- coding: utf-8 -*-
"""
"""
import phenomenode as phn
from types import MappingProxyType
from .context import ContextStack, ContextItem, ContextFamily, Chemical, Phase, Inlet, Outlet
from .quantity import Quantity
from .preferences import preferences

__all__ = (
    'Variable', 'Variables', 'FunctionCall', 'index',
)

class Variable(Quantity):
    __slots__ = ('name', 'context', '_hash')
    
    def __init__(self, name, context=None):
        self.name = name
        self.context = ContextStack() if context is None else context
        
    def __call__(self, *args):
        return FunctionCall(self, args)
        
    def __getitem__(self, index):
        context = self.context
        cls = self.__class__
        if not context:
            return cls(self.name, index)
        elif isinstance(index, (ContextFamily, ContextItem)):
            tag = index.tag
            if isinstance(context, ContextFamily):
                if context.tag == tag: 
                    return cls(self.name, index)
                else:
                    return cls(self.name, index + context)
            elif isinstance(context, ContextStack):
                ns = [n for n, i in enumerate(context) if isinstance(i, ContextFamily) and i.tag is tag]
                if ns:
                    context = context.copy()
                    context[ns[0]] = index
                    context = ContextStack(*context)
                else:
                    context = context + index
                return cls(self.name, context)
            else:
                return cls(self.name, index + context)
        elif isinstance(index, ContextStack):
            variable = self
            for i in index: variable = variable[i]
            return variable
        else:
            raise TypeError('index must be a context')
            
    def __hash__(self):
        try:
            return self._hash
        except:
            self._hash = hash(
                (self.name, self.context)
            )
            return self._hash
        
    def __eq__(self, other):
        return format(self, 'n') == format(other, 'n')
        
    def __repr__(self):
        return f"{type(self).__name__}({self.name!r}, {self.context!r})"
    
    def __format__(self, fmt):
        if fmt == '': fmt = preferences.context_format
        name = self.name
        context = self.context
        if not context: return name
        if fmt == 's':
            return f"{name}{context:s}"
        elif fmt == 'l':
            return f"{name}_" "{" f"{context:{fmt}}" "}"
        elif fmt == 'h':
            return f"<{name}<SUB>{context:{fmt}}</SUB>>"
        elif fmt == 'n':
            return f"{name}[{context:{fmt}}]"
        else:
            raise ValueError(f'invalid format {fmt!r}')
        
    def __str__(self):
        return format(self, 's')
        
    def framed(self, context=None):
        return self.__class__(self.name, self.context + context)
    
    def show(self):
        return print(self)
    _ipython_display_ = show


class Variables(frozenset):
    def __new__(cls, *variables):
        self = super().__new__(cls, variables)
        setattr = super().__setattr__
        setattr(self, 'variables', variables)
        for i in variables: setattr(self, str(i), i)
        return self
    
    def __getitem__(self, index):
        return self.variables[index]
    
    def __iter__(self):
        return iter(self.variables)
    
    def __setattr__(self, name, other):
        raise AttributeError("variables are immutable")
    
    def framed(self, context=None):
        if context is None: return self
        return Variables(*[i.framed(context) for i in self])
    
    def __str__(self):
        return f"Variables({', '.join([str(i) for i in self])})"
    
    def show(self, fmt=None):
        variables = f"({', '.join([format(i, fmt) for i in self])})"
        return print(variables)
    _ipython_display_ = show


class FunctionCall(Quantity):
    __slots__ = ('function', 'parameters', '_hash')
    
    def __init__(self, function, parameters):
        self.function = function
        self.parameters = parameters
        
    def __hash__(self):
        try:
            return self._hash
        except:
            self._hash = hash(
                (self.function, self.parameters)
            )
            return self._hash
        
    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.function == other.function and self.parameters is other.parameters
    
    def __str__(self):
        parameters = self.parameters
        if len(parameters) == 1 and isinstance(parameters[0], (FunctionCall, phn.Variable)):
            return f"{self.function} {parameters[0]}"
        else:
            parameters = ', '.join([format(i) for i in parameters])
            return f"{self.function}({parameters})"
        
    def __repr__(self):
        return f"{type(self).__name__}({self.function!r}, {self.parameters!r})"
    
    def show(self):
        return print(self)
    _ipython_display_ = show


class Index:
    
    def __init__(self, **items):
        self.__dict__.update(items)
        
    def __repr__(self):
        return f"{type(self).__name__}({', '.join([f'{i}={j!r}' for i, j in self.__dict__])})"
    
liquid = Phase('liq')
solid = Phase('sol')
gas = Phase('gas')
chemicals = Chemical.family
inlets = Inlet.family
outlets = Outlet.family
phases = Phase.family
extract = Phase('ext')
raffinate = Phase('raf')
index = Index(
    sum=Variable('Σ'),
    min=Variable('min'),
    product=Variable('Π'),
    lle=Variable('lle'),
    equilibrium=Variable('equilibrium'),
    T = Variable('T'), # Temperature [K]
    P = Variable('P'), # Pressure [Pa]
    H = Variable('H'), # Enthalpy [kJ]
    S = Variable('S'), # Entropy [kJ]
    G = Variable('G'), # Gibbs free energy [kJ]
    A = Variable('A'), # Helmholtz free energy [kJ]
    V = Variable('V'), # Vapor fraction [by mol]
    L = Variable('L'), # Extract fraction [by mol]
    F = Variable('F'), # Flow rate [by mol]
    Q = Variable('Q'), # Duty [kJ]
    f = Variable('f'), # Fugacity [Pa]
    split = Variable('θ'), # Split fraction
    chemicals = Chemical.family,
    phases = Phase.family,
    liquid = liquid,
    extract = extract,
    raffinate = raffinate,
    solid = solid,
    gas = gas,
    inlets = inlets,
    outlets = outlets,
    Fcp = Variable('F', ContextStack(chemicals, phases)),
    Fc = Variable('F', chemicals),
    FVc = Variable('F', ContextStack(chemicals, gas)),
    FLc = Variable('F', ContextStack(chemicals, liquid)),
    FL = Variable('F', liquid), # Liquid flow rate [by mol]
    FV = Variable('F', gas), # Vapor flow rate [by mol]
    KV = Variable('K', ContextStack(chemicals, gas)),
    KL = Variable('K', ContextStack(chemicals, liquid)),
    hV = Variable('h', gas),
    hL = Variable('h', liquid),
    DeltaP = Variable('ΔP'),
    z = Variable('z', chemicals), # Bulk composition [by mol]
    zV = Variable('z', ContextStack(chemicals, gas)), # Vapor composition [by mol]
    zL = Variable('z', ContextStack(chemicals, liquid)), # Liquid composition [by mol]
    fV = Variable('f', ContextStack(chemicals, gas)), # Vapor fugacity [Pa] 
    fL = Variable('f', ContextStack(chemicals, liquid)), # Liquid fugacity [Pa] 
    hE = Variable('h', extract),
    hR = Variable('h', raffinate),
    zE = Variable('z', ContextStack(chemicals, extract)), # Extract composition [by mol]
    zR = Variable('z', ContextStack(chemicals, raffinate)), # Raffinate composition [by mol]
    fE = Variable('f', ContextStack(chemicals, extract)), # Extract fugacity [Pa] 
    fR = Variable('f', ContextStack(chemicals, raffinate)), # Raffinate fugacity [Pa] 
    FEc = Variable('F', ContextStack(chemicals, extract)),
    FRc = Variable('F', ContextStack(chemicals, raffinate)),
    FE = Variable('F', extract), # Extract flow rate [by mol]
    FR = Variable('F', raffinate), # Raffinate flow rate [by mol]
)
