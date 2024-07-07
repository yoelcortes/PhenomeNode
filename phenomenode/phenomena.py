# -*- coding: utf-8 -*-
"""
"""
import phenomenode as phn
from .phenomenode import PhenomeNode
from .variable import index as I
from .equation import Equation as EQ

__all__ = (
    # Material balance equations
    'MassConservation',
    'SeparationProcess',
    'Splitting',
    # Energy correction equation
    'EnergyConservation',
    # Pressure drops
    'PressureBalance',
    # Abstract nonlinear equations
    # 'Generation',
    # 'Separation',
    # 'Splitting',
    # 'EnergyContent',
    
    'BubblePoint',
    'SeparationFactorVLE',
    'EnergyDensityVLE',
    
    'EnergyParameterUpdate',
    'BulkMaterial',
    'MinPressure',
    'EnergyDeparture',
    'Energy',
    'BulkComponents',
    'Composition',
    'Multiply',
    'Divide',
    'Substract',
    
    'Function',
)

# %% Linear equations

class MassConservation(PhenomeNode):
    default_ins = ['Fc']
    default_outs = ['Fc']
    category = 'material'
    directed = False
    linear = True
    
    def equations(self):
        Fins = self.inlet_variables()
        Fouts = self.outlet_variables()
        return [EQ(I.sum(Fouts) - I.sum(Fins), 0)]


class SeparationProcess(PhenomeNode):
    default_ins = [I.Sc, 'Fc']
    default_outs = ['Fc']
    category = 'material'
    directed = False
    linear = True
    
    def equations(self):
        Sc, *Fxs = self.inlet_variables()
        Fys = self.outlet_variables()
        return [EQ(Sc * I.sum(Fxs) - I.sum(Fys), 0)]


class Splitting(PhenomeNode):
    default_ins = [I.split, 'Fcp']
    default_outs = ['Fcp']
    category = 'material'
    linear = True
    directed = False
    
    def equations(self):
        split, *Fout = self.inlet_variables()
        Fouts = self.outlet_variables()
        return [EQ(split * Fout - I.sum(Fouts), 0)]
    
    
class EnergyConservation(PhenomeNode):
    default_ins = [['DeltaE'], ['dHdE']]
    default_outs = ['DeltaE', ['dHdE'], 'DeltaH']
    category = 'energy'
    directed = False
    linear = True
    
    def equations(self):
        DeltaEs_in, dHdE_in, = self.inlet_variables()
        DeltaE_out, dHdE_out, DeltaH  = self.outlet_variables()
        return [EQ(DeltaE_out * I.sum(dHdE_out) - I.sum([i*j for i, j in zip(DeltaEs_in, dHdE_in)]), DeltaH)]


class PressureBalance(PhenomeNode):
    default_ins = ['DeltaP', 'P']
    default_outs = ['P']
    category = 'pressure'
    directed = False
    linear = True
    
    def equations(self):
        DeltaP, Pin, = self.inlet_variables()
        Pout  = self.outlet_variables()
        return [EQ(Pout, Pin + DeltaP)]


# %% General nonlinear phenomenological equations

class EnergyParameterUpdate(PhenomeNode):
    default_ins = [I.DeltaE, I.E]
    default_outs = []
    category = 'hidden'
    directed = False
    linear = True
    
    def equations(self):
        DeltaE, E = self.inlet_variables()
        return [EQ(E, DeltaE + E)]


class EnergyDeparture(PhenomeNode):
    default_ins = ['H']
    default_outs = [I.DeltaH, 'H']
    category = 'energy-parameter'
    directed = True
    linear = True
    
    def equations(self):
        Hins = self.inlet_variables()
        DeltaH, *Houts = self.outlet_variables()
        return [EQ(DeltaH, I.sum(Houts) - I.sum(Hins))]


class Energy(PhenomeNode):
    default_ins = ['Fcp', 'T', 'P']
    default_outs = 'H'
    category = 'energy-parameter'
    directed = True
    
    def equations(self):
        Fcp, T, P = self.inlet_variables()
        H, = self.outlet_variables()
        return [EQ(I.H(Fcp, T, P), H)]


class BulkComponents(PhenomeNode):
    default_ins = 'Fcp'
    default_outs = 'Fc'
    category = 'material-parameter'
    directed = True
    linear = True
    
    def equations(self):
        Fcps = self.inlet_variables()
        Fc, = self.outlet_variables()
        return [EQ(I.sum[I.phases](*Fcps), Fc)]


class Composition(PhenomeNode):
    default_ins = ['Fc', 'F']
    default_outs = ['z']
    category = 'material-parameter'
    directed = True
    
    def equations(self):
        Fc, F = self.inlet_variables()
        z, = self.outlet_variables()
        return [EQ(Fc / F, z)]        


class BulkMaterial(PhenomeNode):
    default_ins = 'Fc'
    default_outs = 'F'
    category = 'material-parameter'
    directed = True
    linear = True
    
    def equations(self):
        Fc, = self.inlet_variables()
        F, = self.outlet_variables()
        return [EQ(I.sum[I.chemicals](Fc), F)]


class RashfordRice(PhenomeNode):
    default_ins = ['z', 'KV', 'V']
    default_outs = []
    category = 'material-parameter'
    
    def equations(self):
        z, KV, V = self.inlet_variables()
        return [
            EQ(I.sum[I.chemicals](z * (KV - 1) / (1 + V * (KV - 1))), 0),
        ]


# %% Nonlinear phenomenological equations - VLE

class BubblePoint(PhenomeNode):
    default_ins = ['zL', 'P']
    default_outs = ['KV', 'T']
    category = 'material-parameter'
    directed = True
    
    def equations(self):
        zL, P = self.inlet_variables()
        K, T = self.outlet_variables()
        return [
            EQ(K & T, I.BubblePoint(zL, P)),
        ]

class SeparationFactorVLE(PhenomeNode):
    default_ins = ['B', 'KV']
    default_outs = ['Sc']
    category = 'material-parameter'
    directed = True
    linear = True
    
    def equations(self):
        B, K = self.inlet_variables()
        Sc, = self.outlet_variables()
        return [
            EQ(Sc, B * K),
        ]

class EnergyDensityVLE(PhenomeNode):
    default_ins = ['hV', 'FL']
    default_outs = ['dHdE']
    category = 'energy-parameter'
    directed = True
    linear = True
    
    def equations(self):
        hV, FL = self.inlet_variables()
        dHdE, = self.outlet_variables()
        return [
            EQ(dHdE, hV * FL),
        ]

# %% Nonlinear phenomenological equations - Aggregation

class Function(PhenomeNode):
    default_ins = [[]]
    default_outs = []
    category = 'material-parameter'
    directed = True
    linear = False
    
    def equations(self):
        ins = self.inlet_variables()
        outs  = self.outlet_variables()
        out = outs[0]
        for i in outs[1:]: out = out & i
        return [EQ(out, I.function(*ins))]


# %% Nonlinear phenomenological equations - LLE

# %% Nonlinear phenomenological equations - Compressor

# %% Nonlinear phenomenological equations - Pump

# %% Mixing

class MinPressure(PhenomeNode):
    default_ins = 'P'
    default_outs = 'P'
    category = 'pressure'
    directed = True
    
    def equations(self):
        P, = self.outlet_variables()
        return [EQ(I.min(*self.inlet_variables()), P)]


class Substract(PhenomeNode):
    directed = True
    linear = True
    
    def equations(self):
        L1, L2 = self.inlet_variables()
        R, = self.outlet_variables()
        return [
            EQ(L1 - L2, R)
        ]

class Multiply(PhenomeNode):
    directed = True
    linear = True
    
    def equations(self):
        L1, L2 = self.inlet_variables()
        R, = self.outlet_variables()
        return [
            EQ(L1 * L2, R)
        ]

class Divide(PhenomeNode):
    directed = True
    linear = True
    
    def equations(self):
        L1, L2 = self.inlet_variables()
        R, = self.outlet_variables()
        return [
            EQ(L1 / L2, R)
        ]

     

