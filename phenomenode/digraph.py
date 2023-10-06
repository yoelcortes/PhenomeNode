# -*- coding: utf-8 -*-
"""
"""
import numpy as np
import phenomenode as phn
from .connection import Connection
from warnings import warn
from graphviz import Digraph
from IPython import display

__all__ = ('digraph_from_node',
           'blank_digraph',
           'finalize_digraph',
           'display_digraph',
           'save_digraph')

edge_node = dict(
    fillcolor='#55a8b5',
    fontcolor='white', 
    style='filled', 
    orientation='0',
    width='0.6', 
    height='0.6', 
    color='#90918e', 
    margin='0',
    peripheries='1',
    fontname="Arial",
)

class PenWidth:
    __slots__ = ('percentiles',)
    def __init__(self, edges):
        values = [len(e.variables) for e in edges] or [0] 
        try:
            self.percentiles = np.percentile(
                values, 
                [33, 66, 100]
            )
        except:
            self.percentiles = 3 * [max(values)]
    
    def __call__(self, edge):
        value = len(edge.variables)
        for width, percentile in enumerate(self.percentiles, 1):
            if value <= percentile: return str(width * 0.6 + 0.4)
        raise Exception(f'{self.name} beyond maximum')

preferences = phn.preferences

def blank_digraph(format='svg', maxiter='10000000000000000000', 
                  Damping='0.995', K='0.5', **graph_attrs):
    # Create a digraph and set direction left to right
    f = Digraph(format=format)
    f.attr(rankdir='LR', maxiter=maxiter, Damping=Damping, K=K,
           penwidth='0', color='none', bgcolor=preferences.background_color,
           fontcolor=preferences.label_color, fontname="Arial",
           labeljust='l', labelloc='t', fontsize='24', constraint='false',
           **graph_attrs)
    return f

def digraph_from_node(node, **graph_attrs):
    f = blank_digraph(**graph_attrs) 
    all_edges = set()
    connected_edges = set()
    node_names = {}
    update_node_names(f, node.nodes, node_names)
    update_digraph_from_path(f, node.nodes, 0, node_names, all_edges, connected_edges)
    connections = get_all_connections(all_edges.difference(connected_edges))
    add_connections(f, connections, node_names)
    return f

def update_digraph_from_path(f, path, depth, node_names, all_edges, connected_edges):
    nodes = set()
    supernodes = []
    new_edges = set()
    for i in path:
        if i.nodes:
            supernodes.append(i)
        else: 
            nodes.add(i)
            new_edges.update(i.ins + i.outs)
    all_edges.update(new_edges)
    update_node_names(f, nodes, node_names)
    edges = [i for i in new_edges if (not i.sink or i.sink in nodes) and (not i.source or i.source in nodes)]
    connections = get_all_connections(edges)
    add_connections(f, connections, node_names)
    connected_edges.update(edges)
    depth += 1
    N_colors = len(preferences.depth_colors)
    color = preferences.depth_colors[(depth - 1) % N_colors]
    if preferences.fill_cluster:
        kwargs = dict(bgcolor=color, penwidth='0.2', color=preferences.edge_color)
    else:
        kwargs = dict(color=color, bgcolor='none', penwidth='0.75', style='solid')
    for i in supernodes:
        with f.subgraph(name='cluster_' + str(hash(i))) as c:
            c.attr(label=str(i), fontname="Arial", 
                   labeljust='l', fontcolor=preferences.label_color, 
                   tooltip=i.get_tooltip_string(),
                   **kwargs)
            update_digraph_from_path(c, i.nodes, depth, node_names, all_edges, connected_edges)


def update_node_names(f: Digraph, path, node_names):
    for n in path:
        if n.nodes: continue
        kwargs = n.vizoptions()
        node_names[n] = kwargs['name']
        f.node(**kwargs)

def get_all_connections(edges, added_connections=None):
    if added_connections is None: added_connections = set()
    connections = []
    for e in edges:
        if (e.sources or e.sinks): 
            connection = Connection.from_edge(e)
            if connection and connection not in added_connections:
                connections.append(connection)
                added_connections.add(connection)
    return connections

def add_connection(f: Digraph, connection, node_names, pen_width=None, **edge_options):
    source, source_index, edge, sink_index, sink = connection
    has_source = source in node_names
    has_sink = sink in node_names
    f.attr('edge', label='', taillabel='', headlabel='', labeldistance='2',
           **edge_options)
    tooltip = edge.get_tooltip_string()
    ref = str(hash(edge))
    penwidth = pen_width(edge) if pen_width else '1.0'
    # Make edge nodes / node-edge edges / node-node edges
    if has_sink and not has_source:
        # Feed edge case
        f.node(ref,
               width='0.15', 
               height='0.15',
               shape='diamond',
               fillcolor='#f98f60',
               color=preferences.edge_color,
               tooltip=tooltip,
               label='')
        inlet_options = sink.graphics.get_inlet_options(sink, sink_index)
        f.attr('edge', arrowtail='none', arrowhead='none', headlabel=edge.describe(),
               tailport='e', penwidth=penwidth, **inlet_options)
        f.edge(ref, node_names[sink], labeltooltip=tooltip, edgetooltip=tooltip)
    elif has_source and not has_sink:
        # Product edge case
        f.node(ref, 
               width='0.15', 
               height='0.2',
               shape='triangle',
               orientation='270',
               fillcolor='#f98f60',
               color=preferences.edge_color,
               tooltip=tooltip,
               label='')
        outlet_options = source.graphics.get_outlet_options(source, source_index)
        f.attr('edge', arrowtail='none', arrowhead='none', label=edge.describe(),
               headport='w', penwidth=penwidth, **outlet_options)
        f.edge(node_names[source], ref, labeltooltip=tooltip, edgetooltip=tooltip)
    elif has_sink and has_source:
        # Process edge case
        outlet_options = source.graphics.get_outlet_options(source, source_index)
        inlet_options = sink.graphics.get_inlet_options(sink, sink_index)
        f.attr('edge', arrowtail='none', arrowhead='normal', 
               **inlet_options, **outlet_options, penwidth=penwidth)
        label = edge.describe() if preferences.label_edges else ''
        f.edge(node_names[source], node_names[sink], label=label,
               labeltooltip=tooltip, edgetooltip=tooltip)
    else:
        pass

def add_connections(f: Digraph, connections, node_names, color=None, fontcolor=None, **edge_options):
    variable_width = preferences.variable_width
    if variable_width:
        pen_width = PenWidth([i.edge for i in connections])
    else:
        pen_width = None
    
    # Set attributes for graph and edges
    f.attr('graph', overlap='orthoyx', fontname="Arial",
           outputorder='edgesfirst', nodesep='0.5', ranksep='0.15', maxiter='1000000')
    f.attr('edge', dir='foward', fontname='Arial')
    f.attr('node', **edge_node)
    index = {j: i for i, j in node_names.items()}
    length = len(index)
    def key(x):
        value = index.get(x.source, 0) + index.get(x.sink, length)
        if x.source_index:
            value += 1e-3 * x.source_index / len(x.source.outs)
        if x.sink_index:
            value += 1e-6 * x.sink_index / len(x.sink.ins)
        return value
    connections = sorted(connections, key=key)
    for connection in connections:
        add_connection(f, connection, node_names, 
                       color=color or preferences.edge_color,
                       fontcolor=fontcolor or preferences.label_color,
                       pen_width=pen_width,
                       **edge_options)

def display_digraph(digraph, format, height=None): # pragma: no coverage
    if format is None: format = preferences.graphviz_format
    if height is None: height = '400px'
    if format == 'svg':
        img = digraph.pipe(format=format)
        x = display.SVG(img)
        display.display(x)
    else:
        x = display.Image(digraph.pipe(format='png'))
        display.display(x)

def save_digraph(digraph, file, format): # pragma: no coverage
    if '.' not in file:
        if format is None: format = preferences.graphviz_format
        file += '.' + format
    elif format is None:
        format = file.split()[-1]
    else:
        raise ValueError(
            "cannot specify format extension; file already has format "
           f"extension '{file.split()[-1]}'"
        )
    img = digraph.pipe(format=format)
    f = open(file, 'wb')
    f.write(img)
    f.close()
    
def finalize_digraph(digraph, file, format, height=None): # pragma: no coverage
    if preferences.raise_exception: 
        if file: save_digraph(digraph, file, format)
        else: display_digraph(digraph, format, height)
    else:
        try:
            if file: save_digraph(digraph, file, format)
            else: display_digraph(digraph, format, height)
        except (OSError, TypeError) as exp:
            raise exp from None
        except Exception as exp: 
            warn(
                f"a '{type(exp).__name__}' was raised when generating "
                "graphviz diagram, possibly due to graphviz installation issues, "
                "make sure Graphviz executables are on your systems' PATH",
                RuntimeWarning
            )
