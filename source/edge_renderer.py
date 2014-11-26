"""
  A class to maintain render information about an Edge instance and provide
  rendering methods for that edge.
"""

# Library Imports
from matplotlib.patches import Path, PathPatch

# Local Module Imports
import config
from helper import mapRangeParam, calcColor
from helper import polar2Cartesian, midTheta 

class EdgeRenderer:

  def __init__(self, edge):
    """
      Constructor

      Args:
        edge: An Edge instance
    """
    self.edge = edge

    # Render properties. Populated below.
    self.color = None
    self.width = None
    self.depth = None
    self.label = None

    # Parse color, width, depth, and label from CSV
    csv = self.edge.csv
    md  = self.edge.md
    row_i = md.attr_indices['USE_AS']
    for col_i in range(config.EDGE_LAYER_COLS_BEGIN, len(self.edge.csv)):
      use_as = md.data[row_i][col_i]
      csv_val = csv[col_i]

      min_val = md.data[md.getAttrIdx('MIN_VAL')][col_i]
      max_val = md.data[md.getAttrIdx('MAX_VAL')][col_i]
      if use_as == 'C':
        start_color = config.EDGE_COLOR_GRADIENT[0]
        end_color   = config.EDGE_COLOR_GRADIENT[1]
        color_val   = csv_val
        if min_val == 'NA':
          min_val = config.NON_NUM_COLOR_MIN_VAL 
          max_val = config.NON_NUM_COLOR_MAX_VAL 
          color_val = abs(hash(csv_val)) % max_val
        self.color  = calcColor(start_color, end_color, float(color_val), 
                                float(min_val), float(max_val)) 
      elif use_as == 'W':
        self.width = mapRangeParam(float(csv_val), float(min_val), 
                                   float(max_val), config.MIN_EDGE_WIDTH, 
                                   config.MAX_EDGE_WIDTH)
      elif use_as == 'D':
        self.depth = float(csv_val)
      elif use_as == 'L':
        self.label = csv_val
      else:
        raise Exception('Unknown edge property specified in ' + self.edge_filename)

    # Fill in unset properties with defaults.
    # TODO: Consider following same style as node_renderer => Computing render values
    # at render time, instead of pre-computing like this.
    if not self.color:
      min_val     = config.EDGE_DEFAULT_META['C'][2] 
      max_val     = config.EDGE_DEFAULT_META['C'][3]
      color_val   = config.EDGE_DEFAULT_VAL['C']
      start_color = config.EDGE_COLOR_GRADIENT[0]
      end_color   = config.EDGE_COLOR_GRADIENT[1]
      self.color  = calcColor(start_color, end_color, float(color_val), 
                              float(min_val), float(max_val)) 
    if not self.width:
      min_val    = config.EDGE_DEFAULT_META['W'][2] 
      max_val    = config.EDGE_DEFAULT_META['W'][3]
      color_val  = config.EDGE_DEFAULT_VAL['W']
      self.width = mapRangeParam(float(color_val), float(min_val), 
                                  float(max_val), config.MIN_EDGE_WIDTH, 
                                  config.MAX_EDGE_WIDTH) 
    if not self.depth:
      self.depth = float(config.EDGE_DEFAULT_VAL['D'])
    if not self.label:
      self.depth = config.EDGE_DEFAULT_VAL['L']

  def render(self, ax, node_extents):
    """
      Render this EdgeRenderer instance.

      Args:
        ax: A matplotlib Axes instance to add text and patches to.
        node_extents: A lookup table to find node start and end thetas 
    """
    edge = self.edge
    n1_extents = node_extents[edge.start_node.uID]
    n2_extents = node_extents[edge.end_node.uID]
    bez_codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
    n1_mid_theta = midTheta(*n1_extents)
    n1_endpoint = polar2Cartesian(config.RING_RADIUS, n1_mid_theta)
    n2_mid_theta = midTheta(*n2_extents)
    n2_endpoint = polar2Cartesian(config.RING_RADIUS, n2_mid_theta)
    bez_verts = [n1_endpoint, config.RING_ORIGIN, n2_endpoint]
    bez_path = Path(bez_verts, bez_codes)
    ax.add_patch(PathPatch(bez_path, 
                           facecolor='none', 
                           edgecolor=self.color, 
                           lw=self.width))

  def __lt__(self, other):
    """
      Comparator to define ordering of EdgeRenders based on their depth.

      Return:
        Boolean
    """
    return self.depth < other.depth
