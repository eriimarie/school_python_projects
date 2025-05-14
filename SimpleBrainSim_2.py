#!/usr/bin/env python
# coding: utf-8

# In[1]:


import plotly.graph_objects as go
import numpy as np
import networkx as nx
import math

    
def mesh_properties(mesh_coords):
    """Calculate center and radius of sphere minimally containing a 3-D mesh
    
    Parameters
    ----------
    mesh_coords : tuple
        3-tuple with x-, y-, and z-coordinates (respectively) of 3-D mesh vertices
    """

    radii = []
    center = []

    for coords in mesh_coords:
        c_max = max(c for c in coords)
        c_min = min(c for c in coords)
        center.append((c_max + c_min) / 2)

        radius = (c_max - c_min) / 2
        radii.append(radius)

    return(center, max(radii))


# Download and prepare dataset from BrainNet repo
coords = np.loadtxt(np.DataSource().open('https://raw.githubusercontent.com/mingruixia/BrainNet-Viewer/master/Data/SurfTemplate/BrainMesh_Ch2_smoothed.nv'), skiprows=1, max_rows=53469)
x, y, z = coords.T

triangles = np.loadtxt(np.DataSource().open('https://raw.githubusercontent.com/mingruixia/BrainNet-Viewer/master/Data/SurfTemplate/BrainMesh_Ch2_smoothed.nv'), skiprows=53471, dtype=int)
triangles_zero_offset = triangles - 1
i, j, k = triangles_zero_offset.T

# Generate 3D mesh.  Simply replace with 'fig = go.Figure()' or turn opacity to zero if seeing brain mesh is not desired.
fig = go.Figure(data=[go.Mesh3d(x=x, y=y, z=z,
                                 i=i, j=j, k=k,
                                 color='lightpink', opacity=0.5, name='', showscale=False, hoverinfo='none')])

# Generate networkx graph and initial 3-D positions using Kamada-Kawai path-length cost-function inside sphere containing brain mesh
G = nx.gnp_random_graph(200, 0.02, seed=42) # Replace G with desired graph here

mesh_coords = (x, y, z)
mesh_center, mesh_radius = mesh_properties(mesh_coords)

scale_factor = 5 # Tune this value by hand to have more/fewer points between the brain hemispheres.
pos_3d = nx.kamada_kawai_layout(G, dim=3, center=mesh_center, scale=scale_factor*mesh_radius) 

# Calculate final node positions on brain surface
pos_brain = {}

for node, position in pos_3d.items():
    squared_dist_matrix = np.sum((coords - position) ** 2, axis=1)
    pos_brain[node] = coords[np.argmin(squared_dist_matrix)]

# Prepare networkx graph positions for plotly node and edge traces
nodes_x = [position[0] for position in pos_brain.values()]
nodes_y = [position[1] for position in pos_brain.values()]
nodes_z = [position[2] for position in pos_brain.values()]

edge_x = []
edge_y = []
edge_z = []
for s, t in G.edges():
    edge_x += [nodes_x[s], nodes_x[t]]
    edge_y += [nodes_y[s], nodes_y[t]]
    edge_z += [nodes_z[s], nodes_z[t]]

# Decide some more meaningful logic for coloring certain nodes.  Currently the squared distance from the mesh point at index 42.
node_colors = []
for node in G.nodes():
    if np.sum((pos_brain[node] - coords[42]) ** 2) < 1000:
        node_colors.append('red')
    else:
        node_colors.append('gray')

# Add node plotly trace
fig.add_trace(go.Scatter3d(x=nodes_x, y=nodes_y, z=nodes_z,
                           #text=labels,
                           mode='markers', 
                           #hoverinfo='text',
                           name='Nodes',
                           marker=dict(
                                       size=5,
                                       color=node_colors
                                      )
                           ))

# Add edge plotly trace.  Comment out or turn opacity to zero if not desired.
fig.add_trace(go.Scatter3d(x=edge_x, y=edge_y, z=edge_z,
                           mode='lines',
                           hoverinfo='none',
                           name='Edges',
                           opacity=0.1, 
                           line=dict(color='gray')
                           ))

# Make axes invisible
fig.update_scenes(xaxis_visible=False,
                  yaxis_visible=False,
                  zaxis_visible=False)

# Manually adjust size of figure
fig.update_layout(autosize=False,
                  width=800,
                  height=800)

fig.show()


# In[ ]:




