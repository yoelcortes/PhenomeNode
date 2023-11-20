# -*- coding: utf-8 -*-
"""
"""
import phenomenode as phn
from .phenomenode import PhenomeNode
from .variable import Variables, Variable, variable_index as index
from .function import function_index as f
from .equality import Equality as EQ
from .graphics import (
    material_graphics, equilibrium_graphics, energy_graphics,
    pressure_graphics
)
from . unit import Unit

__all__ = (
    'BulkEnthalpy', 
    'BulkMaterial',
    'LLE', 'VLE',
    'BubblePoint',
    'DewPoint',
    'MinPressure',
    'Enthalpy',
    'Equilibrium',
)

class BulkEnthalpy(PhenomeNode):
    default_ins = 'H'
    default_outs = 'H'
    graphics = energy_graphics
    
    def load(self):
        feeds = self.ins
        product, = self.outs
        for i in [*feeds, product]: assert i.variable == index.H
    
    def equations(self):
        Hs = self.inlet_variables()
        H, = self.outlet_variables()
        return [EQ(f.sum(*Hs), H)]


class Enthalpy(PhenomeNode):
    default_ins = ['Fcp', 'T', 'P']
    default_outs = 'H'
    graphics = energy_graphics
    
    def equations(self):
        Fcp, T, P = self.inlet_variables()
        H, = self.outlet_variables()
        return [EQ(f.enthalpy(Fcp, T, P), H)]
    
    
class BulkMaterial(PhenomeNode):
    default_ins = 'Fcp'
    default_outs = 'Fc'
    graphics = material_graphics
    
    def equations(self):
        Fcps = self.inlet_variables()
        Fc, = self.outlet_variables()
        return [EQ(f.sum[index.phases](*Fcps), Fc)]


class VLEMaterialBalance(PhenomeNode):
    default_ins = ['Fc', 'KVc', 'V']
    default_outs = ['FVc', 'FLc']
    graphics = material_graphics
    
    def equations(self):
        Fc, KVc, V = self.inlet_variables()
        FVc, FLc = self.outlet_variables()
        return [
            EQ((1 - V) * Fc / (V * KVc + (1 - V)), FLc),
            EQ(Fc - FLc, FVc),
        ]
    

class VLEEnergyBalance(PhenomeNode):
    default_ins = ['hL', 'hV', 'V', 'FLc']
    default_outs = ['FVc', 'FLc']
    graphics = energy_graphics
    
    def equations(self):
        Fc, KVc, V = self.inlet_variables()
        FVc, FLc = self.outlet_variables()
        return [
            EQ((1 - V) * Fc / (V * KVc + (1 - V)), FLc),
            EQ(Fc - FLc, FVc),
        ]
    
    
    

class VLE(PhenomeNode):
    default_ins = ['Fc', 'P', 'V', 'KVc', 'T']
    graphics = equilibrium_graphics
    
    def equations(self):
        return [EQ(f.vle(*self.inlet_variables()), 0)]
    

class LLE(PhenomeNode):
    default_ins = ['Fc', 'T', 'P', 'L', 'KLc']
    graphics = equilibrium_graphics
    
    def equations(self):
        return [EQ(f.lle(*self.inlet_variables()), 0)]
    
    
class BubblePoint(PhenomeNode):
    default_ins = ['FLc', 'KVc', 'T', 'P']
    graphics = equilibrium_graphics
    
    def equations(self):
        return [EQ(f.bubble_point(*self.inlet_variables()), 0)]
    
    
class DewPoint(PhenomeNode):
    default_ins = ['FVc', 'KVc', 'T', 'P']
    graphics = equilibrium_graphics
    
    def equations(self):
        return [EQ(f.dew_point(*self.inlet_variables()), 0)]
 

class Equilibrium(PhenomeNode):
    default_ins = ['Fc', 'P', 'T', 'H']
    default_outs = ['Fcp']
    graphics = equilibrium_graphics
    
    def equations(self):
        Fcp, = self.outlet_variables()
        return [EQ(f.equilibrium(*self.inlet_variables()), Fcp)]
  
    
class PressureDrop(PhenomeNode):
    default_ins = ['P', 'DeltaP']
    default_outs = ['P']
    graphics = pressure_graphics
    
    def equations(self):
        Pin, DeltaP = self.inlet_variables()
        Pout, = self.outlet_variables()
        return [EQ(Pin - DeltaP, Pout)]
    
     
class MinPressure(PhenomeNode):
    default_ins = 'P'
    default_outs = ['P']
    graphics = pressure_graphics
    
    def equations(self):
        P, = self.outlet_variables()
        return [EQ(f.min(*self.inlet_variables()), P)]
