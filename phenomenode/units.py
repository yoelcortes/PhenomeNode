# -*- coding: utf-8 -*-
"""
"""
import phenomenode as phn
from .variable import index as I
from .phenomenode import PhenomeNode

__all__ = (
    'Mixer', 
    'Condenser',
    'Splitter', 
    'StageVLE',
    'AggregatedStageVLE',
    'AggregatedStageLLE',
    'MultiStageVLE',
    'MultiStageLLE',
    'StageLLE', 
    'ShortcutColumn',
)

class Mixer(PhenomeNode, tag='x'): # Single phase
    n_ins = 2
    n_outs = 1
    
    def prepare(self, ins, outs):
        outs[0].define_energy_parameter('T')
        super().prepare(ins, outs)
    
    def load(self):
        ins = self.ins
        product, = outs = self.outs
        self.min_pressure = phn.MinPressure(ins=[i.P for i in ins], outs=[product.P])
        self.inlet_energies = [phn.Energy(ins=[i.Fcp, i.T, i.P]) for i in ins]
        self.outlet_energies = [phn.Energy(ins=[i.Fcp, i.T, i.P]) for i in outs]
        inlet_enthalpies = [i.outs[0] for i in self.inlet_energies]
        outlet_enthalpies = [i.outs[0] for i in self.outlet_energies]
        self.energy_departure = phn.EnergyDeparture(
            ins=inlet_enthalpies, outs=[I.DeltaH, *outlet_enthalpies],
        )
        DeltaH = self.energy_departure.outs[0]
        self.energy_densities = [phn.LiquidEnergyDensity(ins=[i.Fcp, i.T, i.P], outs=[i.dHdE]) for i in outs]
        dHdEs = [i.outs[0] for i in self.energy_densities]
        self.mass_conservation = phn.MassConservation(
            ins=[i.Fcp for i in ins],
            outs=[i.Fcp for i in outs],
        )
        self.energy_conservation = phn.EnergyCorrection(
            ins=[[i.DeltaE for i in ins], [i.dHdE for i in ins]],
            outs=[product.DeltaE, dHdEs, DeltaH]
        )
        self.energy_parameter_update = phn.EnergyParameterUpdate(
            ins=[product.DeltaE, product.T],
        )


class Splitter(PhenomeNode, tag='θ'):
    n_ins = 1
    n_outs = 2
    
    def prepare(self, ins, outs):
        feed, = ins
        top, bottom = outs
        top.T = bottom.T = feed.T
        top.P = bottom.P = feed.P
        # E = feed.DeltaE.variable.name[-1]
        # top.define_energy_parameter(E)
        # bottom.define_energy_parameter(E)
        top.DeltaE = bottom.DeltaE = feed.DeltaE
        super().prepare(ins, outs)
    
    def load(self):
        feed, = self.ins
        top, bottom = self.outs
        multiply = phn.Multiply(ins=[I.split, feed.Fcp], outs=[top.Fcp], category='material', subcategory='lle-material')
        self.split = split = multiply.ins[0]
        phn.Substract(ins=[feed.Fcp, top.Fcp], outs=[bottom.Fcp], category='material', subcategory='lle-material')
        self.top_energy_density = phn.Multiply(ins=[split, feed.dHdE], outs=[top.dHdE], category='energy-phenomena')
        self.bottom_energy_density = phn.Substract(ins=[feed.dHdE, top.dHdE], outs=[bottom.dHdE], category='energy-phenomena')


class Condenser(PhenomeNode, tag='s'):
    n_ins = 1
    n_outs = 1
    
    def prepare(self, ins, outs):
        liquid, = outs
        liquid.no_energy_parameter()
        liquid.Fcp.variable = I.FLc  
        super().prepare(ins, outs)
    
    def load(self):
        feed, = ins = self.ins
        product, = outs = self.outs
        self.pressure_balance = phn.PressureBalance(ins=[feed.P, I.DeltaP], outs=[product.P])
        self.mass_conservation = phn.MassConservation(
            ins=[i.Fcp for i in ins],
            outs=[i.Fcp for i in outs],
        )
        

class StageVLE(PhenomeNode, tag='s'):
    n_ins = 2
    n_outs = 2
    
    def prepare(self, ins, outs, location=None, abstract_parameters=False, adiabatic=True):
        vapor, liquid = outs
        if location is None: location = 'middle'
        if location == 'middle':
            if len(ins) == 1:
                Lfeed, *others = ins
                vapor.P = Lfeed.P
            else:
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
        if adiabatic:
            vapor.define_energy_parameter('B')
        else:
            vapor.no_energy_parameter()
        liquid.no_energy_parameter()
        self.abstract_parameters = abstract_parameters
        self.adiabatic = adiabatic
        super().prepare(ins, outs)
    
    def load(self):
        ins = self.ins
        vapor, liquid = outs = self.outs
        abstract_parameters = self.abstract_parameters
        adiabatic = self.adiabatic
        if abstract_parameters:
            DeltaH = I.DeltaH
        elif adiabatic:
            self.inlet_energies = [phn.Energy(ins=[i.Fcp, i.T, i.P]) for i in ins]
            self.outlet_energies = [phn.Energy(ins=[i.Fcp, i.T, i.P]) for i in outs]
            inlet_enthalpies = [i.outs[0] for i in self.inlet_energies]
            outlet_enthalpies = [i.outs[0] for i in self.outlet_energies]
            inlet_enthalpies.append('Q')
            self.energy_departure = phn.EnergyDeparture(
                ins=inlet_enthalpies, outs=[I.DeltaH, *outlet_enthalpies],
            )
            DeltaH = self.energy_departure.outs[0]
        T = vapor.T = liquid.T
        P = liquid.P
        if abstract_parameters:
            Sc = I.Sc
        else:
            self.pressure_balance = phn.PressureBalance(ins=[vapor.P, I.DeltaP], outs=[liquid.P])
            self.bulk_liquid = bulk_liquid = phn.BulkMaterial(ins=[liquid.Fcp], outs=['FL'], subcategory='vle')
            FL, = bulk_liquid.outs
            self.liquid_composition = liquid_composition = phn.Composition(ins=[liquid.Fcp, FL], outs=[I.zL], subcategory='vle')
            zL, = liquid_composition.outs
            self.bubble_point = phn.BubblePoint(ins=[zL, P], outs=[I.KV, T], subcategory='vle')
            K, T = self.bubble_point.outs
            self.separation_factor = phn.SeparationFactorVLE(ins=[K, I.B], outs=[I.Sc], subcategory='vle')
            
            B = self.separation_factor.ins[1]
            Sc = self.separation_factor.outs[0]
            if adiabatic:
                self.bulk_vapor = bulk_vapor = phn.BulkMaterial(ins=[vapor.Fcp], outs=['FV'], category='energy-phenomena')
                self.bulk_liquid_energy = bulk_liquid_energy = phn.BulkMaterial(ins=[liquid.Fcp], outs=['FL'], category='energy-phenomena')
                FL, = bulk_liquid_energy.outs
                self.specific_gas_enthalpy = phn.Divide(
                    ins=[outlet_enthalpies[0], bulk_vapor.outs[0]], 
                    outs=[I.hV],
                    category='energy-phenomena'
                )
                hV = self.specific_gas_enthalpy.outs[0]
                self.energy_density = phn.VaporEnergyDensity(ins=[hV, FL], outs=[vapor.dHdE])
            
        self.mass_conservation = phn.MassConservation(
            ins=[i.Fcp for i in ins],
            outs=[i.Fcp for i in outs]
        )
        self.separation_process = phn.SeparationProcess(
            ins=[Sc, liquid.Fcp], outs=[vapor.Fcp]
        )
        if adiabatic:
            self.energy_conservation = phn.EnergyCorrection(
                ins=[[i.DeltaE for i in ins], [i.dHdE for i in ins]],
                outs=[vapor.DeltaE, [vapor.dHdE], DeltaH]
            )
            self.energy_parameter_update = phn.EnergyParameterUpdate(
                ins=[vapor.DeltaE, B],
            )
        

# TODO: Work on pressures for LLE

class StageLLE(PhenomeNode, tag='s'):
    n_ins = 2
    n_outs = 2
    
    def prepare(self, ins, outs, location=None, abstract_parameters=False,
                pseudo_equilibrium=True):
        extract, raffinate = outs
        if location is None: location = 'middle'
        if location == 'middle':
            if len(ins) == 1:
                Rfeed, *others = ins
                extract.P = Rfeed.P
            else:
                Efeed, Rfeed, *others = ins
                extract.P = Efeed.P
                raffinate.P = Rfeed.P
        elif location == 'bottom':
            Rfeed, *others = ins
            extract.P = Rfeed.P
        elif location == 'top':
            Efeed, *others = ins
            raffinate.P = Efeed.P
        else:
            raise ValueError(f'invalid stage location {location!r}')
        extract.T = raffinate.T
        extract.Fcp.variable = I.FEc
        raffinate.Fcp.variable = I.FRc  
        extract.define_energy_parameter('T')
        raffinate.define_energy_parameter('T')
        extract.DeltaE = raffinate.DeltaE
        extract.T = raffinate.T
        self.abstract_parameters = abstract_parameters
        self.pseudo_equilibrium = pseudo_equilibrium
        super().prepare(ins, outs)
    
    def load(self):
        ins = self.ins
        extract, raffinate = outs = self.outs
        abstract_parameters = self.abstract_parameters
        if abstract_parameters:
            DeltaH = I.DeltaH
        else:
            self.inlet_energies = [phn.Energy(ins=[i.Fcp, i.T, i.P]) for i in ins]
            self.outlet_energies = [phn.Energy(ins=[i.Fcp, i.T, i.P]) for i in outs]
            inlet_enthalpies = [i.outs[0] for i in self.inlet_energies]
            outlet_enthalpies = [i.outs[0] for i in self.outlet_energies]
            inlet_enthalpies.append('Q')
            self.energy_departure = phn.EnergyDeparture(
                ins=inlet_enthalpies, outs=[I.DeltaH, *outlet_enthalpies],
            )
            DeltaH = self.energy_departure.outs[0]
        T = extract.T
        P = raffinate.P
        self.pressure_balance = phn.PressureBalance(ins=[extract.P, I.DeltaP], outs=[raffinate.P])
        if abstract_parameters:
            Sc = I.Sc
            dHdEs = [i.dHdE for i in outs]
        else:
            self.bulk_extract = bulk_extract = phn.BulkMaterial(ins=[extract.Fcp], outs=['FE'], subcategory='lle')
            FE, = bulk_extract.outs
            self.extract_composition = extract_composition = phn.Composition(ins=[extract.Fcp, FE], outs=[I.zE], subcategory='lle')
            zE, = extract_composition.outs
            self.bulk_components = bulk_components = phn.BulkComponents(ins=[i.Fcp for i in ins], subcategory='lle-phenomena')
            Fc = bulk_components.outs[0]
            self.bulk_material = bulk_material = phn.BulkComponents(ins=[bulk_components.outs[0]], subcategory='lle-phenomena')
            F = bulk_material.outs[0]
            self.bulk_composition = bulk_composition = phn.Composition(ins=[Fc, F], subcategory='lle-phenomena')
            z = bulk_composition.outs[0]
            if self.pseudo_equilibrium:
                self.pseudo_equilibrium = PE = phn.PseudoEquilibrium(ins=[I.gammaR, I.KL, zE], subcategory='lle')
                KL = PE.outs[1]
                self.parameter_updates = [phn.ParameterUpdate(ins=[i], outs=[j], subcategory='lle-update') for i, j in zip(PE.ins, PE.outs)]
                self.rashford_rice = RR = phn.RashfordRice(ins=[z, KL, I.L], subcategory='lle-phenomena')
                L = RR.ins[2]
                self.separation_factor = phn.SeparationFactorLLE(ins=[KL, L], outs=[I.Sc], subcategory='lle-phenomena')
            else:
                self.lle_criteria = phn.LLECriteria(ins=[z, T, P], outs=[zE, I.L])
                zE, L = self.lle_criteria.outs
                self.partition_coefficient = partition_coefficient = phn.PartitionCoefficient(ins=[z, zE, L])
                KL = partition_coefficient.outs[0]
                self.separation_factor = phn.SeparationFactorLLE(ins=[KL, L], outs=[I.Sc])
            Sc = self.separation_factor.outs[0]
            self.energy_densities = [phn.LiquidEnergyDensity(ins=[i.Fcp, i.T, i.P], outs=[i.dHdE]) for i in outs]
            dHdEs = [i.outs[0] for i in self.energy_densities]
        self.mass_conservation = phn.MassConservation(
            ins=[i.Fcp for i in ins],
            outs=[i.Fcp for i in outs],
            subcategory='lle-material',
        )
        self.separation_process = phn.SeparationProcess(
            ins=[Sc, raffinate.Fcp], outs=[extract.Fcp],
            subcategory='lle-material',
        )
        self.energy_conservation = phn.EnergyCorrection(
            ins=[[i.DeltaE for i in ins], [i.dHdE for i in ins]],
            outs=[extract.DeltaE, dHdEs, DeltaH]
        )
        self.energy_parameter_update = phn.EnergyParameterUpdate(
            ins=[extract.DeltaE, extract.T],
        )


class AggregatedStageLLE(PhenomeNode, tag='s'):
    n_ins = 1
    n_outs = 2
    
    def prepare(self, ins, outs):
        extract, raffinate = outs
        extract.Fcp.variable = I.FEc
        raffinate.Fcp.variable = I.FRc  
        # extract.define_energy_parameter('T')
        # raffinate.define_energy_parameter('T')
        extract.DeltaE = raffinate.DeltaE
        super().prepare(ins, outs)
    
    def load(self):
        feed, *other = ins = self.ins
        extract, raffinate = outs = self.outs
        self.inlet_energies = [phn.Energy(ins=[i.Fcp, i.T, i.P]) for i in ins]
        self.outlet_energies = [phn.Energy(ins=[i.Fcp, i.T, i.P]) for i in outs]
        inlet_enthalpies = [i.outs[0] for i in self.inlet_energies]
        outlet_enthalpies = [i.outs[0] for i in self.outlet_energies]
        inlet_enthalpies.append('Q')
        self.energy_departure = phn.EnergyDeparture(
            ins=inlet_enthalpies, outs=[I.DeltaH, *outlet_enthalpies],
        )
        DeltaH = self.energy_departure.outs[0]
        self.pressure_balance = phn.PressureBalance(ins=[extract.P, I.DeltaP], outs=[raffinate.P])
        self.ufunc = phn.Function(ins=[(i.Fcp, i.T, i.P) for i in ins], outs=[I.Sc, extract.T, raffinate.T, I.DeltaP, I.DeltaP])
        Sc, TE, TR, DPE, DPR = self.ufunc.outs
        self.raffinate_pressure_balance = phn.PressureBalance(ins=[feed.P, DPR], outs=[raffinate.P])
        self.extract_pressure_balance = phn.PressureBalance(ins=[feed.P, DPE], outs=[extract.P])
        self.energy_densities = [phn.LiquidEnergyDensity(ins=[i.Fcp, i.T, i.P], outs=[i.dHdE]) for i in outs]
        self.mass_conservation = phn.MassConservation(
            ins=[i.Fcp for i in ins],
            outs=[i.Fcp for i in outs]
        )
        self.separation_process = phn.SeparationProcess(
            ins=[Sc, raffinate.Fcp], outs=[extract.Fcp]
        )
        self.energy_conservation = phn.EnergyCorrection(
            ins=[[i.DeltaE for i in ins], [i.dHdE for i in ins]],
            outs=[extract.DeltaE, [i.outs[0] for i in self.energy_densities], DeltaH]
        )
        self.energy_parameter_update = phn.EnergyParameterUpdate(
            ins=[extract.DeltaE, extract.T],
        )
        

class AggregatedStageVLE(PhenomeNode, tag='s'):
    n_ins = 1
    n_outs = 2
    
    def prepare(self, ins, outs, location=None):
        vapor, liquid = outs
        vapor.T = liquid.T
        vapor.Fcp.variable = I.FVc
        liquid.Fcp.variable = I.FLc  
        # vapor.define_energy_parameter('B')
        liquid.no_energy_parameter()
        super().prepare(ins, outs)
    
    def load(self):
        feed, *others = ins = self.ins
        vapor, liquid = outs = self.outs
        self.inlet_energies = [phn.Energy(ins=[i.Fcp, i.T, i.P]) for i in ins]
        self.outlet_energies = [phn.Energy(ins=[i.Fcp, i.T, i.P]) for i in outs]
        inlet_enthalpies = [i.outs[0] for i in self.inlet_energies]
        outlet_enthalpies = [i.outs[0] for i in self.outlet_energies]
        inlet_enthalpies.append('Q')
        self.energy_departure = phn.EnergyDeparture(
            ins=inlet_enthalpies, outs=[I.DeltaH, *outlet_enthalpies],
        )
        DeltaH = self.energy_departure.outs[0]
        self.bulk_liquid = bulk_liquid = phn.BulkMaterial(ins=[liquid.Fcp], outs=['FL'])
        FL, = bulk_liquid.outs
        self.liquid_composition = liquid_composition = phn.Composition(ins=[liquid.Fcp, FL], outs=[I.zL])
        zL, = liquid_composition.outs
        # try:
        self.ufunc = phn.Function(ins=[(i.Fcp, i.T, i.P) for i in ins], outs=[I.KV, vapor.T, liquid.T, I.DeltaP, I.DeltaP])
        # except:
        #     breakpoint()
        K, TV, TL, DPV, DPL = self.ufunc.outs
        self.liquid_pressure_balance = phn.PressureBalance(ins=[feed.P, DPL], outs=[liquid.P])
        self.vapor_pressure_balance = phn.PressureBalance(ins=[feed.P, DPV], outs=[vapor.P])
        self.separation_factor = phn.SeparationFactorVLE(ins=[K, I.B], outs=[I.Sc])
        B = self.separation_factor.ins[1]
        Sc = self.separation_factor.outs[0]
        self.bulk_vapor = bulk_vapor = phn.BulkMaterial(ins=[vapor.Fcp], outs=['FV'], category='energy-phenomena')
        self.bulk_liquid_energy = bulk_liquid_energy = phn.BulkMaterial(ins=[liquid.Fcp], outs=['FL'], category='energy-phenomena')
        FL, = bulk_liquid_energy.outs
        self.specific_gas_enthalpy = phn.Divide(
            ins=[outlet_enthalpies[0], bulk_vapor.outs[0]], 
            outs=[I.hV],
            category='energy-phenomena'
        )
        hV = self.specific_gas_enthalpy.outs[0]
        self.energy_density = phn.VaporEnergyDensity(ins=[hV, FL], outs=[vapor.dHdE])
        self.mass_conservation = phn.MassConservation(
            ins=[i.Fcp for i in ins],
            outs=[i.Fcp for i in outs]
        )
        self.separation_process = phn.SeparationProcess(
            ins=[Sc, liquid.Fcp], outs=[vapor.Fcp]
        )
        self.energy_conservation = phn.EnergyCorrection(
            ins=[[i.DeltaE for i in ins], [i.dHdE for i in ins]],
            outs=[vapor.DeltaE, [vapor.dHdE], DeltaH]
        )
        self.energy_parameter_update = phn.EnergyParameterUpdate(
            ins=[vapor.DeltaE, B],
        )

class ShortcutColumn(PhenomeNode, tag='s'):
    n_ins = 1
    n_outs = 2
    
    def prepare(self, ins, outs, location=None):
        vapor, liquid = outs
        vapor.T = liquid.T
        vapor.Fcp.variable = I.FVc
        liquid.Fcp.variable = I.FLc  
        vapor.no_energy_parameter()
        liquid.no_energy_parameter()
        super().prepare(ins, outs)
    
    def load(self):
        feed, *others = ins = self.ins
        vapor, liquid = outs = self.outs
        self.ufunc = phn.Function(
            ins=[(i.Fcp, i.T, i.P) for i in ins],
            outs=[I.Sc, vapor.T, liquid.T, I.DeltaP, I.DeltaP],
            subcategory='aggregated',
        )
        Sc, TV, TL, DPV, DPL = self.ufunc.outs
        self.liquid_pressure_balance = phn.PressureBalance(ins=[feed.P, DPL], outs=[liquid.P])
        self.vapor_pressure_balance = phn.PressureBalance(ins=[feed.P, DPV], outs=[vapor.P])
        self.mass_conservation = phn.MassConservation(
            ins=[i.Fcp for i in ins],
            outs=[i.Fcp for i in outs]
        )
        self.separation_process = phn.SeparationProcess(
            ins=[Sc, liquid.Fcp], outs=[vapor.Fcp]
        )


# class StageLLE(PhenomeNode, tag='s'):
#     n_ins = 2
#     n_outs = 2
    
#     def prepare(self, ins, outs):
#         LIQ, liq = outs
#         LIQ.Fcp.variable = I.FEc
#         liq.Fcp.variable = I.FRc
#         super().prepare(ins, outs)
    
#     def load(self):
#         feeds = self.ins
#         enthalpies = [i.H for i in feeds]
#         enthalpies.append(I.Q)
#         self.bulk_enthalpy = bulk_enthalpy = phn.BulkEnergy(
#             ins=enthalpies
#         )
#         Hbulk, = bulk_enthalpy.outs
#         LIQ, liq = self.outs
#         # Assume pressures are given by pumps, so no need to add equations
#         LIQ.T = liq.T
#         self.bulk_material = bulk_material = phn.BulkMaterial(ins=[i.Fcp for i in feeds])
#         Fc = bulk_material.outs[0]
#         self.lle = lle = phn.LLE(
#             ins=(Fc, LIQ.T, LIQ.P, liq.Fcp),
#         )
#         Fc, T, P, FRc = lle.ins
#         self.lle_material_balance = lle_material_balance = phn.EQMaterialBalance(
#             ins=(Fc, I.KL, I.L), outs=[FRc]
#         )
#         Fc, KL, L = lle_material_balance.ins
#         substract = phn.Substract(ins=[Fc, FRc], outs=[LIQ.Fcp], category='material')
#         FEc, = substract.outs
#         self.bulk_LIQUID = bulk_LIQ = phn.BulkComponents(ins=[FEc], outs=[I.FE])
#         FE, = bulk_LIQ.outs
#         self.bulk_liquid = bulk_liq = phn.BulkComponents(ins=[FRc], outs=[I.FR])
#         FR, = bulk_liq.outs
#         self.LIQUID_composition = LIQUID_composition = phn.Composition(ins=[FEc, FE], outs=[I.zE])
#         zE, = LIQUID_composition.outs
#         self.liquid_composition = liquid_composition = phn.Composition(ins=[FRc, FR], outs=[I.zR])
#         zR, = liquid_composition.outs
#         phn.Divide(ins=[zE, zR], outs=[KL], category='equilibrium')
#         self.liquid_enthalpy = liquid_enthalpy = phn.Energy(
#             ins=[zR, T, liq.P], outs=['hR'],
#         )
#         hR, = liquid_enthalpy.outs
#         self.LIQUID_enthalpy = LIQUID_enthalpy = phn.Energy(
#             ins=[zE, T, LIQ.P], outs=['hE'],
#         )
#         hE, = LIQUID_enthalpy.outs
#         self.lle_energy_balance = phn.EQEnergyBalance(
#             ins=[Hbulk, hR, hE, FE], outs=[L]
#         )
#         phn.Multiply(ins=[hE, FE], outs=[LIQ.H], category='energy')
#         phn.Multiply(ins=[hR, FR], outs=[liq.H], category='energy')
        
        
class MultiStageVLE(PhenomeNode, tag='v'):
    n_ins = 2
    n_outs = 2
    
    def prepare(self, ins, outs, n_stages, feed_stages=None, abstract_parameters=False):
        if feed_stages is None: feed_stages = (0, -1)
        self.feed_stages = feed_stages
        self.n_stages = n_stages
        self.abstract_parameters = abstract_parameters
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
        abstract_parameters = self.abstract_parameters
        self.vle_stages = [
            StageVLE(
                ins=inlet_streams[i],
                outs=outlet_streams[i],
                location=stage_location.get(i, 'middle'),
                abstract_parameters=abstract_parameters,
                adiabatic=(i!=0) or (i==n_stages-1)
            ) for i in range(n_stages)
        ]
        
class MultiStageLLE(PhenomeNode, tag='e'):
    n_ins = 2
    n_outs = 2
    
    def prepare(self, ins, outs, n_stages, feed_stages=None, abstract_parameters=False):
        if feed_stages is None: feed_stages = (0, -1)
        self.feed_stages = feed_stages
        self.n_stages = n_stages
        self.abstract_parameters = abstract_parameters
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
        abstract_parameters = self.abstract_parameters
        self.lle_stages = [
            StageLLE(
                ins=inlet_streams[i],
                outs=outlet_streams[i],
                abstract_parameters=abstract_parameters,
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
            
    