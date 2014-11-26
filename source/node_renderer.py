"""
  A class to maintain render information about a Node instance and provide
  rendering methods for that node.
"""

# Library Imports
from matplotlib.patches import Wedge

# Local Module Imports
import config
from helper import midTheta, theta2Quadrant, polar2Cartesian, mapRangeParam, \
                   calcColor
from math import pi

class NodeRenderer:

  """
    Constructor

    Args:
      edge: A Node instance
  """
  def __init__(self, node, start_theta, end_theta):
    self.node = node
    self.start_theta = start_theta
    self.end_theta = end_theta

  """
    Render this NodeRenderer instance as a set of matplotlib wedge patches
    and labels.

    Args:
      ax: A matplotlib Axes instance to add text and patches to.
  """
  def render(self, ax):
    # Patches
    node = self.node
    for layer_i in xrange(len(node.md.layers)):
      # Calculate Color
      num_gradients   = len(config.NODE_COLOR_GRADIENTS)
      start_color     = config.NODE_COLOR_GRADIENTS[layer_i % num_gradients][0]
      end_color       = config.NODE_COLOR_GRADIENTS[layer_i % num_gradients][1]
      min_color_csv   = node.md.getPropertyMinVal('C', layer_i)
      max_color_csv   = node.md.getPropertyMaxVal('C', layer_i)
      layer_color_csv = node.getLayerColor(layer_i) 
      if min_color_csv == 'NA':
        min_color_csv = config.NON_NUM_COLOR_MIN_VAL 
        max_color_csv = config.NON_NUM_COLOR_MAX_VAL 
        layer_color_csv = abs(hash(layer_color_csv)) % max_color_csv
      layer_color     = calcColor(start_color, end_color, float(layer_color_csv), 
                                  float(min_color_csv), float(max_color_csv)) 
      # Calculate Width
      min_depth_csv   = node.md.getPropertyMinVal('D', layer_i)
      max_depth_csv   = node.md.getPropertyMaxVal('D', layer_i)
      layer_depth_csv = node.getLayerDepth(layer_i) 
      layer_depth     = mapRangeParam(float(layer_depth_csv), float(min_depth_csv), 
                                      float(max_depth_csv), 0.0, -config.RING_DEPTH)
      # Render Ring Patch
      ax.add_patch(Wedge(config.RING_ORIGIN, 
                         config.RING_RADIUS + config.RING_DEPTH * layer_i, 
                         self.start_theta, self.end_theta, 
                         width=layer_depth,
                         edgecolor='none',
                         facecolor=layer_color))
