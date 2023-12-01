# -*- coding: utf-8 -*-
"""
"""
import phenomenode as phn
from .phenomenode import PhenomeNode
from .variable import index as I
from .equation import Equation as EQ

__all__ = (
    'BulkEnergy', 
    'BulkMaterial',
    'LLE', 'VLE',
    'MinPressure',
    'Equilibrium',
    'Energy',
    'BulkComponents',
    'Composition',
    'EQMaterialBalance',
    'EQEnergyBalance',
    'PressureDrop',
    'Multiply',
    'Divide',
    'Substract',
    'RachfordRice',
)

class BulkEnergy(PhenomeNode):
    default_ins = 'H'
    default_outs = 'H'
    category = 'energy'
    
    def equations(self):
        Hs = self.inlet_variables()
        H, = self.outlet_variables()
        return [EQ(I.sum(*Hs), H)]


class Energy(PhenomeNode):
    default_ins = ['Fcp', 'T', 'P']
    default_outs = 'H'
    category = 'energy'
    
    def equations(self):
        Fcp, T, P = self.inlet_variables()
        H, = self.outlet_variables()
        return [EQ(H(Fcp, T, P), H)]
    
    
class BulkMaterial(PhenomeNode):
    default_ins = 'Fcp'
    default_outs = 'Fc'
    category = 'material'
    
    def equations(self):
        Fcps = self.inlet_variables()
        Fc, = self.outlet_variables()
        return [EQ(I.sum[I.phases](*Fcps), Fc)]


class Composition(PhenomeNode):
    default_ins = ['Fc', 'F']
    default_outs = 'z'
    category = 'material'
    
    def equations(self):
        Fc, F = self.inlet_variables()
        z, = self.outlet_variables()
        return [EQ(Fc / F, z)]        

class BulkComponents(PhenomeNode):
    default_ins = 'Fc'
    default_outs = 'F'
    category = 'material'
    
    def equations(self):
        Fc, = self.inlet_variables()
        F, = self.outlet_variables()
        return [EQ(I.sum[I.chemicals](Fc), F)]


class EQMaterialBalance(PhenomeNode):
    default_ins = ['Fc', 'KV', 'V']
    default_outs = ['FLc']
    category = 'material'
    
    def equations(self):
        Fc, KV, V = self.inlet_variables()
        FLc, = self.outlet_variables()
        return [
            EQ((1 - V) * Fc / (V * KV + (1 - V)), FLc),
        ]
    

class Substract(PhenomeNode):
    
    def equations(self):
        L1, L2 = self.inlet_variables()
        R, = self.outlet_variables()
        return [
            EQ(L1 - L2, R)
        ]

class EQEnergyBalance(PhenomeNode):
    default_ins = ['H', 'hL', 'hV', 'FL']
    default_outs = ['V']
    category = 'energy'
    
    def equations(self):
        H, hL, hV, FL = self.inlet_variables()
        V, = self.outlet_variables()
        return [
            EQ((H/FL - hL) / hV, V / (1 - V)),
        ]
    

class RachfordRice(PhenomeNode):
    default_ins = ['z', 'KV', 'V']
    default_outs = []
    category = 'material'
    
    def equations(self):
        z, KV, V = self.inlet_variables()
        return [
            EQ(I.sum[I.chemicals](z * (KV - 1) / (1 + V * (KV - 1))), 0),
        ]
    
    
class Multiply(PhenomeNode):
    
    def equations(self):
        L1, L2 = self.inlet_variables()
        R, = self.outlet_variables()
        return [
            EQ(L1 * L2, R)
        ]

class Divide(PhenomeNode):
    
    def equations(self):
        L1, L2 = self.inlet_variables()
        R, = self.outlet_variables()
        return [
            EQ(L1 / L2, R)
        ]
    
class VLE(PhenomeNode):
    default_ins = ['zL', 'zV', 'T', 'P']
    default_outs = ['fV', 'fL']
    category = 'equilibrium'
    
    def equations(self):
        x, y, P, T = self.inlet_variables()
        fV, fL = self.outlet_variables()
        return [EQ(fL(x, T, P), fV(y, T, P))]
    

class LLE(PhenomeNode):
    default_ins = ['Fc', 'T', 'P', 'FLc']
    default_outs = []
    category = 'equilibrium'
    
    def equations(self):
        variables = self.inlet_variables()
        return [EQ(I.lle(*variables), variables[-1])]


class Equilibrium(PhenomeNode):
    default_ins = ['Fc', 'P', 'T', 'H']
    default_outs = ['Fcp']
    category = 'equilibrium'
    
    def equations(self):
        Fcp, = self.outlet_variables()
        return [EQ(I.equilibrium(*self.inlet_variables()), Fcp)]
  
    
class PressureDrop(PhenomeNode):
    default_ins = ['P', 'DeltaP']
    default_outs = ['P']
    category = 'pressure'
    
    def equations(self):
        Pin, DeltaP = self.inlet_variables()
        Pout, = self.outlet_variables()
        return [EQ(Pin - DeltaP, Pout)]
    
     
class MinPressure(PhenomeNode):
    default_ins = 'P'
    default_outs = ['P']
    category = 'pressure'
    
    def equations(self):
        P, = self.outlet_variables()
        return [EQ(I.min(*self.inlet_variables()), P)]
