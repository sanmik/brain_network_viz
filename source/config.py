"""
  This file contains globally include-able configuration values
"""

"""
  CSV PARSING
"""

# Define the number of CSV rows encoding metadata
NUM_NODE_METADATA_ROWS = 3
NUM_EDGE_METADATA_ROWS = 3

# The number of the first column in the range of CSV columns encoding node layer
# info: {color, width, depth, label}. All columns after this in the CSV 
# define layer properties.
NODE_LAYER_COLS_BEGIN = 5

# The number of the first column in the range of CSV columns encoding edge layer
# info: {color, width, depth, label}. All columns after this in the CSV 
# define properties.
EDGE_LAYER_COLS_BEGIN = 3

"""----------------------------------------------------------------------------
  METADATA
----------------------------------------------------------------------------"""

# Legal USE_AS attribute tag strings
USE_AS_KEYS = (
  # Model Properties
  'G', # Group - Used to group Nodes into Lobes
  'P', # Position - X,Y,Z Postion Values
  'S', # Start Node - Used to specify the start node of an edge
  'E', # End Node - Used to specify the end node of an edge

  # Render Properties
  'C', # Color
  'W', # Width - Used for angular width of Nodes and thickness of Edge lines
  'D', # Depth - Used for ring thickness of Nodes and draw order of Edges
  'L', # Label
)
NODE_USE_AS_KEYS = ('C', 'W', 'D', 'L')
EDGE_USE_AS_KEYS = ('C', 'W', 'D', 'L')

"""----------------------------------------------------------------------------
  DEFAULT VALUES
----------------------------------------------------------------------------"""
NODE_DEFAULT_META = {
  'C': (None, None, 0, 1), # Prop Name, Prop Column, Min, Max
  'W': (None, None, 0, 1), 
  'D': (None, None, 0, 1), 
  'L': (None, None, 'NA', 'NA') 
}

NODE_DEFAULT_VAL = {
  'C': 1, 
  'W': 1, 
  'D': 1, 
  'L': '' 
}

EDGE_DEFAULT_META = {
  'C': (None, None, 0, 1), # Prop Name, Prop Column, Min, Max
  'W': (None, None, 0, 1), 
  'D': (None, None, 0, 1), 
  'L': (None, None, 'NA', 'NA') 
}

EDGE_DEFAULT_VAL = {
  'C': 1, 
  'W': 0.5, 
  'D': 1, 
  'L': '' 
}

"""----------------------------------------------------------------------------
  RENDERING PROPERTIES 
----------------------------------------------------------------------------"""

# Total number of degree's for gaps between lobes
TOTAL_GAP_DEGREES = 30.0

# Radius of the visualization ring in matplotlib units.
RING_RADIUS = 0.70

# Center point of the visualization ring.
RING_ORIGIN = (0.0, 0.0) 

# Depth of the ring in the radial dimension.
RING_DEPTH = 0.1 

# Edge width range
MIN_EDGE_WIDTH = 0.0
MAX_EDGE_WIDTH = 2.0

# An array of color gradients. Will be cycled through to color rings.
NODE_COLOR_GRADIENTS = [
  ('#44A77D', '#004C2C'), # Green
  ('#46779D', '#032A47'), # Blue
  ('#F3B663', '#6F4000'), # Orange/Brown
  ('#DA6638', '#6F2000')] # Red

EDGE_COLOR_GRADIENT = ('#DA6638', '#6F2000') # Red

LAYER_LABEL_COLORS = ('#801815', '#804615', '#0D4A4D', '#116416')

""" When input color values are not numeric, but are instead strings, those
strings get hashed to numeric values and modulo'd into the range specified
by the following constants. """
NON_NUM_COLOR_MIN_VAL = 0
NON_NUM_COLOR_MAX_VAL = 1000


""" There are two approaches to 'sparsifying' the rendered edges, given a 
percent value p. The first renders all edges with weights in the top p% of
the range of existing edge weights. The second renders p% of the existing
edges, choosing those edges with the highest weights.
"""
EDGE_THRESH_1 = 1
EDGE_THRESH_2 = 2
