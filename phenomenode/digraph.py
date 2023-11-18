# -*- coding: utf-8 -*-
"""
"""
import numpy as np
import phenomephenomenode as phn
from .connection import Connection
from warnings import warn
from graphviz import Digraph
from IPython import display

__all__ = ('digraph_from_phenomenode',
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

def digraph_from_phenomenode(phenomenode, **graph_attrs):
    f = blank_digraph(**graph_attrs) 
    all_connections = set()
    connected = set()
    phenomenode_names = {}
    update_phenomenode_names(f, [phenomenode], phenomenode_names)
    update_digraph_from_path(f, [phenomenode], 0, phenomenode_names, all_connections, connected)
    add_connections(f, all_connections.difference(connected), phenomenode_names)
    return f

def update_digraph_from_path(f, path, depth, node_names, all_connections, connected):
    phenomenodes = set()
    superphenomenodes = []
    varnodes = set()
    new_connections = []
    other_connections = []
    for i in path:
        if i.phenomenodes:
            superphenomenodes.append(i)
        else: 
            phenomenodes.add(i)
            varnodes.update(i.ins + i.outs)
            for varnode in i.ins:
                new_connections.append(
                    Connection(varnode, i)
                )
                for source in varnode.sources:
                    other_connections.append(
                        Connection(source, varnode)
                    )
            for varnode in i.outs:
                new_connections.append(
                    Connection(i, varnode)
                )
                for sink in varnode.sinks:
                    other_connections.append(
                        Connection(varnode, sink)
                    )
    all_connections.update(new_connections + other_connections)
    update_varnode_names(f, varnodes, node_names)
    update_phenomenode_names(f, phenomenodes, node_names)
    add_connections(f, new_connections, node_names)
    connected.update(new_connections)
    depth += 1
    N_colors = len(preferences.depth_colors)
    color = preferences.depth_colors[(depth - 1) % N_colors]
    if preferences.fill_cluster:
        if depth == 1:
            kwargs = dict(bgcolor=color, penwidth='0')
        else:
            kwargs = dict(bgcolor=color, penwidth='0.2', color=preferences.edge_color)
    else:
        kwargs = dict(color=color, bgcolor='none', penwidth='0.75', style='solid')
    for i in superphenomenodes:
        with f.subgraph(name='cluster_' + str(hash(i))) as c:
            c.attr(label=str(i), fontname="Arial", 
                   labeljust='l', fontcolor=preferences.label_color, 
                   tooltip=i.get_tooltip_string(),
                   **kwargs)
            update_digraph_from_path(c, i.phenomenodes, depth, node_names, all_connections, connected)


def update_phenomenode_names(f: Digraph, path, node_names):
    for n in path:
        if n.phenomenodes: continue
        kwargs = n.vizoptions()
        node_names[n] = kwargs['name']
        f.node(**kwargs)

def update_varnode_names(f: Digraph, varnodes, node_names):
    for n in varnodes:
        if n in node_names: continue
        kwargs = n.vizoptions()
        node_names[n] = kwargs['name']
        f.node(**kwargs)

def add_connection(f: Digraph, connection, node_names, **edge_options):
    source, sink = connection
    f.attr('edge', label='', taillabel='', headlabel='', labeldistance='2',
           **edge_options)
    for i in connection:
        if isinstance(i, phn.PhenomeNode):
            tooltip = i.get_tooltip_string()
            color = i.graphics.color
            break
    else:
        raise RuntimeError('connection does not include a phenomenode')
    penwidth = '1.0'
    f.edge(node_names[source], node_names[sink], label='', 
           labeltooltip=tooltip, edgetooltip=tooltip, arrowtail='none', 
           arrowhead='normal', headport='c', tailport='c', color=color,
           penwidth=penwidth)

def add_connections(f: Digraph, connections, node_names, **edge_options):
    # Set attributes for graph and edges
    f.attr('graph', overlap='orthoyx', fontname="Arial",
           outputorder='edgesfirst', phenomenodesep='0.5', ranksep='0.15', maxiter='1000000')
    f.attr('edge', dir='foward', fontname='Arial')
    for connection in connections:
        add_connection(f, connection, node_names, 
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
