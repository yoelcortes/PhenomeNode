# -*- coding: utf-8 -*-
"""
"""
from .preferences import preferences

class PhenomeNodeGraphics:
    """Create a PhenomeNodeGraphics object that contains specifications for 
    Graphviz node and edge styles."""
    __slots__ = ('category',)
    
    #: [dict] Node settings
    options = {
        'shape': 'point',
        'style': 'filled',
        'gradientangle': '0',
        'width': '0.1',
        'height': '0.1',
        'orientation': '0.0',
        'peripheries': '1',
        'margin': 'default',
        'fontname': 'Arial'
    }
    
    #: [dict] Colors by category
    colors = {
        'material': 'black',
        'transport': '#33cc33',
        'reaction': '#5fc1cf',
        'equilibrium': '#a180b8',
        'energy': '#f1777f',
        'pressure': '#8ead3e',
    }
    
    def __init__(self, category):
        #: [str] Phenomena category(e.g., material, energy, equilibrium, reaction, transport)
        self.category = category
    
    @property
    def color(self):
        return self.colors[self.category]
    
    def get_options(self, node): # pragma: no coverage
        """Return node tailored to node specifications"""
        options = self.options.copy()
        options['name'] = str(hash(node))
        options['label'] = str(node)
        options['fillcolor'] = options['fontcolor'] = options['color'] = self.color
        return options
        
    def __repr__(self): # pragma: no coverage
        return f'{type(self).__name__}(category={self.category})'


# %% Graphics components

material_graphics = PhenomeNodeGraphics(category='material')
energy_graphics = PhenomeNodeGraphics(category='energy')
equilibrium_graphics = PhenomeNodeGraphics(category='equilibrium')
reaction_graphics = PhenomeNodeGraphics(category='reaction')
transport_graphics = PhenomeNodeGraphics(category='transport')
pressure_graphics = PhenomeNodeGraphics(category='pressure')