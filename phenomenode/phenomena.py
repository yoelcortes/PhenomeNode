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
    'Enthalpy',
    'Equilibrium',
)

class BulkEnthalpy(PhenomeNode):
    default_ins = 'H'
    default_outs = 'H'
    
    def load(self):
        feeds = self.ins
        product, = self.outs
        for i in [*feeds, product]: assert i.variable == index.H
    
    def equations(self):
        Hi = self.inlet_variables(family=True)
        H, = self.outlet_variables()
        return [EQ(f.sum[index.inlets](Hi), H)]


class Enthalpy(PhenomeNode):
    default_ins = ['Fcp', 'T', 'P']
    default_outs = 'H'
    
    def equations(self):
        Fcp, T, P = self.inlet_variables()
        H, = self.outlet_variables()
        return [EQ(f.enthalpy(Fcp, T, P), H)]
    
    
class BulkMaterial(PhenomeNode):
    default_ins = 'Fcp'
    default_outs = 'Fc'
    
    def equations(self):
        Fcpi = self.inlet_variables(family=True)
        Fc, = self.outlet_variables()
        return [EQ(f.sum[index.inlets, index.phases](Fcpi), Fc)]


class VLE(PhenomeNode):
    default_ins = ['Fc', 'P', 'V', 'KVc', 'T']
    
    def equations(self):
        return [EQ(f.vle(*self.inlet_variables()), 0)]
    

class LLE(PhenomeNode):
    default_ins = ['Fc', 'T', 'P', 'L', 'KLc']
    
    def equations(self):
        return [EQ(f.lle(*self.inlet_variables()), 0)]
    
    
class BubblePoint(PhenomeNode):
    default_ins = ['FLc', 'KVc', 'T', 'P']
    
    def equations(self):
        return [EQ(f.bubble_point(*self.inlet_variables()), 0)]
    
    
class DewPoint(PhenomeNode):
    default_ins = ['FVc', 'KVc', 'T', 'P']
    
    def equations(self):
        return [EQ(f.dew_point(*self.inlet_variables()), 0)]
    
    
class MinPressure(PhenomeNode):
    default_ins = 'P'
    default_outs = ['P']
    def equations(self):
        P, = self.outlet_variables()
        return [EQ(f.min(*self.inlet_variables()), P)]


class Equilibrium(PhenomeNode):
    default_ins = ['Fc', 'P', 'T', 'H']
    default_outs = ['Fcp']
    
    def equations(self):
        Fcp, = self.outlet_variables()
        return [EQ(f.equilibrium(*self.inlet_variables()), Fcp)]
    