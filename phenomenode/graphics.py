# -*- coding: utf-8 -*-
"""
"""
from .preferences import preferences

__all__ = ('PhenomeNodeGraphics',)

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
        'material': '#403a48',
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
graphics = dict(
    material=PhenomeNodeGraphics(category='material'),
    energy=PhenomeNodeGraphics(category='energy'),
    equilibrium=PhenomeNodeGraphics(category='equilibrium'),
    reaction=PhenomeNodeGraphics(category='reaction'),
    transport=PhenomeNodeGraphics(category='transport'),
    pressure=PhenomeNodeGraphics(category='pressure'),
)
