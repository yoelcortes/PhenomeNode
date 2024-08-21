# -*- coding: utf-8 -*-
"""
"""
import phenomenode as phn

__all__ = ('PhenomeNodeGraphics',)

class PhenomeNodeGraphics:
    """Create a PhenomeNodeGraphics object that contains specifications for 
    Graphviz node and edge styles."""
    __slots__ = ('category', 'subcategory', 'directed', 'linear', 'options', 'color', 'subcolor')
    
    #: [dict] Default node settings
    default_options = {
        'shape': 'point',
        'style': 'filled',
        'gradientangle': '0',
        'width': '0.2',
        'height': '0.2',
        'orientation': '0.0',
        'peripheries': '0',
        'margin': '0',
        'fontname': 'Arial'
    }
    
    #: [dict] Default colors by category
    default_colors = {
        'material': '#a180b8', # purple
        'hidden': '#bdc2bf', # grey
        'material-phenomena': '#5fc1cf', # blue
        'energy-phenomena': '#f1777f', # red
        'energy': '#403a48', # black
        'pressure': '#8ead3e', # green
        'lle': '#718838', # Green dirty
        'lle-material': '#a180b8', # purple
        'lle-phenomena': '#5fc1cf', # blue
        'vle': '#dd7440', # Orange
        'aggregated': '#00a996', # Blue 
        'lle-update': '#bdc2bf', # Grey
    }
    
    def __init__(self, category, subcategory, directed, linear):
        #: [str] Phenomena category (e.g., material, energy, material-phenomena, energy-phenomena).
        self.category = category
        
        #: [str] Phenomena subcategory (e.g., lle, lle-material, lle-phenomena, vle).
        self.subcategory = subcategory
        
        #: [bool] Whether equation should explicitly solve for a variable.
        self.directed = directed
        
        #: [bool] Whether equation is linear.
        self.linear = linear
        
        #: [dict] Node settings
        self.options = self.default_options.copy()
        
        # [str] Node and edge category color
        self.color = self.default_colors[category]
        
        # [str] Node and edge subcategory color
        self.subcolor = self.default_colors.get(subcategory)
    
    def update(self, **options):
        self.options.update(options)
    
    def get_options(self, node): # pragma: no coverage
        """Return node tailored to node specifications"""
        options = self.options.copy()
        options['name'] = str(hash(node))
        options['label'] = ''
        color = (self.subcolor or self.color) if phn.preferences.subcategory else self.color
        options['fillcolor'] = options['fontcolor'] = options['color'] = color
        return options
        
    def __repr__(self): # pragma: no coverage
        return f'{type(self).__name__}(category={self.category}, subcategory={self.subcategory}, directed={self.directed}, linear={self.linear})'

