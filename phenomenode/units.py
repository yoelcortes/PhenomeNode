# -*- coding: utf-8 -*-
"""
"""
import phenomenode as phn
from .variable import index as I
from .phenomenode import PhenomeNode

__all__ = (
    'Mixer', 
    'Splitter', 
    'MultiStageVLE',
    'StageVLE',
    'MultiStageLLE',
    'StageLLE', 
)

class Mixer(PhenomeNode, tag='x'):
    n_ins = 2
    n_outs = 1
    def load(self):
        feeds = self.ins
        product, = self.outs
        self.min_pressure = phn.MinPressure(ins=[i.P for i in feeds], outs=[product.P])
        self.bulk_material = bulk_material = phn.BulkMaterial(ins=[i.Fcp for i in feeds])
        self.enthalpies = enthalpies = [phn.Energy(ins=[*i.varnodes]) for i in feeds]
        self.bulk_enthalpy = bulk_enthalpy = phn.BulkEnergy(
            ins=[i.outs[0] for i in enthalpies]
        )
        self.equilibrium = phn.Equilibrium(
            ins=(bulk_material.outs[0], product.T, product.P, bulk_enthalpy.outs[0]),
            outs=[product.Fcp]
        )


class Splitter(PhenomeNode, tag='θ'):
    n_ins = 1
    n_outs = 2
    def load(self):
        feed, = self.ins
        top, bottom = self.outs
        multiply = phn.Multiply(ins=[I.split, feed.Fcp], outs=[top.Fcp], category='material')
        self.split = multiply.ins[0]
        phn.Multiply(ins=[self.split, feed.H], outs=[top.H], category='energy')
        top.T = bottom.T = feed.T
        top.P = bottom.P = feed.P
        phn.Substract(ins=[feed.Fcp, top.Fcp], outs=[bottom.Fcp], category='material')
        phn.Substract(ins=[feed.H, top.H], outs=[bottom.H], category='energy')
        

class StageVLE(PhenomeNode, tag='s'):
    n_ins = 2
    n_outs = 2
    
    def prepare(self, ins, outs, location=None):
        vapor, liquid = outs
        if location is None: location = 'middle'
        if location == 'middle':
            Vfeed, Lfeed, *others = ins
            vapor.P = Lfeed.P
            liquid.P = Vfeed.P
        elif location == 'bottom':
            Lfeed, *others = ins
            vapor.P = Lfeed.P
        elif location == 'top':
            Vfeed, *others = ins
            liquid.P = Vfeed.P
        else:
            raise ValueError(f'invalid stage location {location!r}')
        vapor.T = liquid.T
        vapor.Fcp.variable = I.FVc
        liquid.Fcp.variable = I.FLc
        super().prepare(ins, outs)
    
    def load(self):
        feeds = self.ins
        enthalpies = [i.H for i in feeds]
        enthalpies.append('Q')
        self.bulk_enthalpy = bulk_enthalpy = phn.BulkEnergy(
            ins=enthalpies,
        )
        Hbulk, = bulk_enthalpy.outs
        vapor, liquid = self.outs
        T = vapor.T = liquid.T
        P = vapor.P
        self.pressure_drop = phn.PressureDrop(ins=[vapor.P, None], outs=[liquid.P])
        self.bulk_material = bulk_material = phn.BulkMaterial(ins=[i.Fcp for i in feeds])
        Fc = bulk_material.outs[0]
        self.vle_material_balance = vle_material_balance = phn.EQMaterialBalance(
            ins=(Fc, I.KV, I.V), outs=[liquid.Fcp],
        )
        FLc, = vle_material_balance.outs
        Fc, KV, V = self.vle_material_balance.ins
        substract = phn.Substract(ins=[Fc, FLc], outs=[vapor.Fcp], category='material')
        FVc, = substract.outs
        self.bulk = bulk = phn.BulkComponents(ins=[Fc], outs=['F'])
        F, = bulk.outs
        self.bulk_composition = bulk_composition = phn.Composition(ins=[Fc, F], outs=[I.z])
        z, = bulk_composition.outs
        self.bulk_vapor = bulk_vapor = phn.BulkComponents(ins=[FVc], outs=['FV'])
        FV, = bulk_vapor.outs
        self.bulk_liquid = bulk_liquid = phn.BulkComponents(ins=[FLc], outs=['FL'])
        FL, = bulk_liquid.outs
        self.vapor_composition = vapor_composition = phn.Composition(ins=[FVc, FV], outs=[I.zV])
        zV, = vapor_composition.outs
        self.liquid_composition = liquid_composition = phn.Composition(ins=[FLc, FL], outs=[I.zL])
        zL, = liquid_composition.outs
        self.liquid_enthalpy = liquid_enthalpy = phn.Energy(
            ins=[zL, T, liquid.P], outs=['hL'],
        )
        self.vle = phn.VLE(
            ins=(zL, zV, T, P),
        )
        phn.Divide(ins=[zV, zL], outs=[KV], category='equilibrium')
        hL, = liquid_enthalpy.outs
        self.vapor_enthalpy = vapor_enthalpy = phn.Energy(
            ins=[zV, T, vapor.P], outs=['hV'],
        )
        hV, = vapor_enthalpy.outs
        self.vle_energy_balance = phn.EQEnergyBalance(
            ins=[Hbulk, hL, hV, FL], outs=[V]
        )
        self.rashford_rice = phn.RachfordRice(
            ins=[z, KV, V]
        )
        phn.Multiply(ins=[hV, FV], outs=[vapor.H], category='energy')
        phn.Multiply(ins=[hL, FL], outs=[liquid.H], category='energy')
        
        

class StageLLE(PhenomeNode, tag='s'):
    n_ins = 2
    n_outs = 2
    
    def prepare(self, ins, outs):
        LIQ, liq = outs
        LIQ.Fcp.variable = I.FEc
        liq.Fcp.variable = I.FRc
        super().prepare(ins, outs)
    
    def load(self):
        feeds = self.ins
        enthalpies = [i.H for i in feeds]
        enthalpies.append(I.Q)
        self.bulk_enthalpy = bulk_enthalpy = phn.BulkEnergy(
            ins=enthalpies
        )
        Hbulk, = bulk_enthalpy.outs
        LIQ, liq = self.outs
        # Assume pressures are given by pumps, so no need to add equations
        LIQ.T = liq.T
        self.bulk_material = bulk_material = phn.BulkMaterial(ins=[i.Fcp for i in feeds])
        Fc = bulk_material.outs[0]
        self.lle = lle = phn.LLE(
            ins=(Fc, LIQ.T, LIQ.P, liq.Fcp),
        )
        Fc, T, P, FRc = lle.ins
        self.lle_material_balance = lle_material_balance = phn.EQMaterialBalance(
            ins=(Fc, I.KL, I.L), outs=[FRc]
        )
        Fc, KL, L = lle_material_balance.ins
        substract = phn.Substract(ins=[Fc, FRc], outs=[LIQ.Fcp], category='material')
        FEc, = substract.outs
        self.bulk_LIQUID = bulk_LIQ = phn.BulkComponents(ins=[FEc], outs=[I.FE])
        FE, = bulk_LIQ.outs
        self.bulk_liquid = bulk_liq = phn.BulkComponents(ins=[FRc], outs=[I.FR])
        FR, = bulk_liq.outs
        self.LIQUID_composition = LIQUID_composition = phn.Composition(ins=[FEc, FE], outs=[I.zE])
        zE, = LIQUID_composition.outs
        self.liquid_composition = liquid_composition = phn.Composition(ins=[FRc, FR], outs=[I.zR])
        zR, = liquid_composition.outs
        phn.Divide(ins=[zE, zR], outs=[KL], category='equilibrium')
        self.liquid_enthalpy = liquid_enthalpy = phn.Energy(
            ins=[zR, T, liq.P], outs=['hR'],
        )
        hR, = liquid_enthalpy.outs
        self.LIQUID_enthalpy = LIQUID_enthalpy = phn.Energy(
            ins=[zE, T, LIQ.P], outs=['hE'],
        )
        hE, = LIQUID_enthalpy.outs
        self.lle_energy_balance = phn.EQEnergyBalance(
            ins=[Hbulk, hR, hE, FE], outs=[L]
        )
        phn.Multiply(ins=[hE, FE], outs=[LIQ.H], category='energy')
        phn.Multiply(ins=[hR, FR], outs=[liq.H], category='energy')
        
        
class MultiStageVLE(PhenomeNode, tag='v'):
    n_ins = 2
    n_outs = 2
    
    def prepare(self, ins, outs, n_stages, feed_stages=None):
        if feed_stages is None: feed_stages = (0, -1)
        self.feed_stages = feed_stages
        self.n_stages = n_stages
        super().prepare(ins, outs)
        
    def load(self):
        n_stages = self.n_stages
        vapor, liquid = self.outs
        outlet_streams = [
            [vapor, phn.Stream()], 
            *[[phn.Stream(), phn.Stream()] # Vapor, Liquid
              for i in range(n_stages - 2)],
            [phn.Stream(), liquid]
        ]
        feed_stages = [(i if i >= 0 else n_stages + i) for i in self.feed_stages]
        feeds_by_stage = {i: [] for i in feed_stages}
        for i, j in zip(feed_stages, self.ins): feeds_by_stage[i].append(j)
        inlet_streams = []
        for i in range(n_stages):
            if i == 0:
                inlets = [outlet_streams[i+1][0]]
            elif i == n_stages - 1:
                inlets = [outlet_streams[i-1][1]]
            else:
                inlets = [outlet_streams[i+1][0], outlet_streams[i-1][1]]
            if i in feeds_by_stage:
                inlets.extend(feeds_by_stage[i])
            inlet_streams.append(inlets)
        stage_location = {0: 'top', n_stages-1: 'bottom'}
        self.vle_stages = [
            StageVLE(
                ins=inlet_streams[i],
                outs=outlet_streams[i],
                location=stage_location.get(i, 'middle'),
            ) for i in range(n_stages)
        ]
        
class MultiStageLLE(PhenomeNode, tag='e'):
    n_ins = 2
    n_outs = 2
    
    def prepare(self, ins, outs, n_stages, feed_stages=None):
        if feed_stages is None: feed_stages = (0, -1)
        self.feed_stages = feed_stages
        self.n_stages = n_stages
        super().prepare(ins, outs)
        
    def load(self):
        n_stages = self.n_stages
        extract, raffinate = self.outs
        outlet_streams = [
            [extract, phn.Stream()], 
            *[[phn.Stream(), phn.Stream()] # Extract, Raffinate
              for i in range(n_stages - 2)],
            [phn.Stream(), raffinate]
        ]
        feed_stages = [(i if i >= 0 else n_stages + i) for i in self.feed_stages]
        feeds_by_stage = {i: [] for i in feed_stages}
        for i, j in zip(feed_stages, self.ins): feeds_by_stage[i].append(j)
        inlet_streams = []
        for i in range(n_stages):
            if i == 0:
                inlets = [outlet_streams[i+1][0]]
            elif i == n_stages - 1:
                inlets = [outlet_streams[i-1][1]]
            else:
                inlets = [outlet_streams[i+1][0], outlet_streams[i-1][1]]
            if i in feeds_by_stage:
                inlets.extend(feeds_by_stage[i])
            inlet_streams.append(inlets)
        self.lle_stages = [
            StageLLE(
                ins=inlet_streams[i],
                outs=outlet_streams[i],
            ) for i in range(n_stages)
        ]
            
# class Split(Node):
#     n_ins = 1
#     n_outs = 2
    
#     def load(self):
#         inlet, = self.ins
#         outs = self.outs
#         for i in outs: i.variables = inlet.variables
    
#     def equations(self, fmt=None, context=None, inbound=None):
#         inlet, = self.inlet_variables()
#         top, bottom = self.outlet_variables()
#         split = I.split
#         vars = self.ins[0].variables
#         if I.Fc in vars:
#             equations = [
#                 EQ(inlet.Fc * split, top.Fc),
#                 EQ(inlet.Fc * (1 - split), bottom.Fc)
#             ]
#         elif I.Fcp in vars:
#             equations = [
#                 EQ(inlet.Fcp * split, top.Fcp),
#                 EQ(inlet.Fcp * (1 - split), bottom.Fcp)
#             ]
#         if I.H in vars:
#             equations = [
#                 EQ(inlet.H * split, top.H),
#                 EQ(inlet.H * (1 - split), bottom.H)
#             ]
#         elif I.T in vars:
#             equations = [
#                 EQ(inlet.T, top.T, bottom.T)
#             ]
#         if I.P in vars:
#             equations = [
#                 EQ(inlet.P, top.P, bottom.P)
#             ]
#         return equations


# class StageLLE(Node, tag='z'):
#     n_ins = 2
#     n_outs = 2
    
#     def prepare(self, ins, outs, T=None, P=None, Q=None):
#         self.init_ins(ins)
#         self.init_outs(outs)
#         self.T = T
#         self.P = P
#         self.Q = Q
    
#     def load(self):
#         specs = []
#         filtered = []
#         if self.Q:
#             self.ins.append(
#                 phn.Edge(variables=Variables(I.Q))
#             )
#         self.mixer = Mixer(self.ins)
#         if self.T:
#             specs.append(I.T)
#             filtered.append(I.H)
#         if self.P:
#             specs.append(I.P)
#             filtered.append(I.P)
#         if self.T and self.Q: 
#             raise ValueError('cannot specify both temperature and duty')
#         elif not (self.T or self.Q):
#             raise ValueError('must either temperature or duty')
#         self.filter = Pylon.filter(self.mixer.outs[0], filtered)
#         self.distribute = Pylon.distribute(self.filter.outs[0], [I.Fc], 2)
#         specs = Variables(*specs)
#         if specs:
#             self.ins.append(
#                 phn.Edge(variables=specs)
#             )
#             self.outlet_specs = Pylon.repeat(self.ins[-1], 3)
#             self.merge_specs = Pylon.merge([self.distribute.outs[0], self.outlet_specs.outs[0]])
#             lle_inlet = self.merge_specs.outs[0]
#         else:
#             self.outlet_specs = Pylon.distribute(self.distribute.outs[0], [I.P], 3)
#             lle_inlet = self.distribute.outs[0]
#         self.lle = LLE(lle_inlet)
#         lle_outlet = self.lle.outs[0]
#         merge_T = I.T in lle_outlet.variables
#         if merge_T:
#             self.pop = Pylon.pop(lle_outlet, [I.T], 3)
#             lle_outlet = self.pop.outs[0]
#         self.partition_merge = Pylon.merge([lle_outlet, self.distribute.outs[1]])
#         self.partition = Partition(self.partition_merge.outs[0])
#         if merge_T:
#             self.exit_merges = [Pylon.merge([i, j, k]) for i, j, k 
#                                 in zip(self.partition.outs, self.outlet_specs.outs[1:], self.pop.outs[1:])]
#         else:
#             self.exit_merges = [Pylon.merge([i, j]) for i, j in zip(self.partition.outs, self.outlet_specs.outs[1:])]


# class LLE(Node, tag='l'):
#     n_ins = 1
#     n_outs = 1
    
#     def load(self):
#         inlet, = self.ins
#         outlet, = self.outs
#         if I.H in inlet.variables:
#             outlet.variables = Variables(I.KL, I.L, I.T)
#         else:
#             outlet.variables = Variables(I.KL, I.L)
    
#     def equations(self):
#         inlet, = self.inlet_variables()
#         outlet,  = self.outlet_variables()
#         if hasattr(inlet, 'H'):
#             lle = EQ(f.lle(*inlet), outlet.KL & outlet.L & outlet.T)
#         else:
#             lle = EQ(f.lle(*inlet), outlet.KL & outlet.L)
#         return [lle]


# class Partition(Node, tag='ϕ'):
#     n_ins = 1
#     n_outs = 2
    
#     def load(self):
#         inlet, = self.ins
#         top, bottom = self.outs
#         if not inlet.variables.difference([I.KV, I.V, I.T, I.Fc]):
#             self.vle = True
#             self.lle = False
#         elif not inlet.variables.difference([I.KL, I.L, I.T, I.Fc]):
#             self.vle = False
#             self.lle = True
#         else:
#             raise ValueError('inlet variables must be partition coefficients and a phase fraction')
#         top.variables = bottom.variables = Variables(I.Fcp)
    
#     def equations(self):
#         inlet, = self.inlet_variables()
#         top, bottom = self.outlet_variables()
#         if self.vle:
#             return [
#                 EQ(top.Fcp[I.liquid], inlet.Fc * (1 - inlet.V) / (inlet.V * (inlet.KV - 1) + 1)),
#                 EQ(bottom.Fcp[I.liquid], inlet.Fc * inlet.V / (inlet.V * (inlet.KV - 1) + 1))
#             ]
#         elif self.lle:
#             return [
#                 EQ(top.Fcp[I.liquid], inlet.Fc * (1 - inlet.L) / (inlet.L * (inlet.KL - 1) + 1)),
#                 EQ(bottom.Fcp[I.liquid], inlet.Fc * inlet.L / (inlet.L * (inlet.KL - 1) + 1))
#             ]
#         else:
#             raise RuntimeError('unknown error')
            
    