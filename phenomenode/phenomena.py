# -*- coding: utf-8 -*-
"""
"""
import phenomenode as phn
from .phenomenode import PhenomeNode
from .variable import Variables, Variable, variable_index as index
from .function import function_index as f
from .equality import Equality as EQ
from . unit import Unit

__all__ = (
    'BulkEnthalpy', 
    'BulkMaterial',
    'LLE', 'VLE',
    'BubblePoint',
    'DewPoint',
    'MinPressure',
    'Equilibrium',
    'Enthalpy',
    'BulkComponents',
    'Composition',
    'EQMaterialBalance',
    'EQEnergyBalance',
    'PressureDrop',
    'Multiply',
)

class BulkEnthalpy(PhenomeNode):
    default_ins = 'H'
    default_outs = 'H'
    category = 'energy'
    
    def equations(self):
        Hs = self.inlet_variables()
        H, = self.outlet_variables()
        return [EQ(f.sum(*Hs), H)]


class Enthalpy(PhenomeNode):
    default_ins = ['Fcp', 'T', 'P']
    default_outs = 'H'
    category = 'energy'
    
    def equations(self):
        Fcp, T, P = self.inlet_variables()
        H, = self.outlet_variables()
        return [EQ(f.enthalpy(Fcp, T, P), H)]
    
    
class BulkMaterial(PhenomeNode):
    default_ins = 'Fcp'
    default_outs = 'Fc'
    category = 'material'
    
    def equations(self):
        Fcps = self.inlet_variables()
        Fc, = self.outlet_variables()
        return [EQ(f.sum[index.phases](*Fcps), Fc)]


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
        return [EQ(f.sum[index.chemicals](Fc), F)]


class EQMaterialBalance(PhenomeNode):
    default_ins = ['Fc', 'KVc', 'V']
    default_outs = ['FVc', 'FLc']
    category = 'material'
    
    def equations(self):
        Fc, KVc, V = self.inlet_variables()
        FVc, FLc = self.outlet_variables()
        return [
            EQ((1 - V) * Fc / (V * KVc + (1 - V)), FLc),
            EQ(Fc - FLc, FVc),
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
    
class Multiply(PhenomeNode):
    
    def equations(self):
        L1, L2 = self.inlet_variables()
        R, = self.outlet_variables()
        return [
            EQ(L1 * L2, R)
        ]
    
class VLE(PhenomeNode):
    default_ins = ['Fc', 'P', 'V', 'T']
    default_outs = ['KVc']
    category = 'equilibrium'
    
    def equations(self):
        KVc, = self.outlet_variables()
        return [EQ(f.vle(*self.inlet_variables()), KVc)]
    

class LLE(PhenomeNode):
    default_ins = ['Fc', 'T', 'P', 'L']
    default_outs = ['KLc']
    category = 'equilibrium'
    
    def equations(self):
        KLc, = self.outlet_variables()
        return [EQ(f.lle(*self.inlet_variables()), KLc)]
    
    
class BubblePoint(PhenomeNode):
    default_ins = ['FLc', 'KVc', 'T', 'P']
    category = 'equilibrium'
    
    def equations(self):
        return [EQ(f.bubble_point(*self.inlet_variables()), 0)]
    
    
class DewPoint(PhenomeNode):
    default_ins = ['FVc', 'KVc', 'T', 'P']
    category = 'equilibrium'
    
    def equations(self):
        return [EQ(f.dew_point(*self.inlet_variables()), 0)]
 

class Equilibrium(PhenomeNode):
    default_ins = ['Fc', 'P', 'T', 'H']
    default_outs = ['Fcp']
    category = 'equilibrium'
    
    def equations(self):
        Fcp, = self.outlet_variables()
        return [EQ(f.equilibrium(*self.inlet_variables()), Fcp)]
  
    
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
        return [EQ(f.min(*self.inlet_variables()), P)]
