"""
  A class to maintain model data about Nodes (brain regions)
"""

# Library Imports
import numpy as np

# Local Module Imports
import config
from helper import cartesian2Polar, calcColor, mapRangeParam

class Node:
  def __init__(self, csv_row, lobe, md):
    """
    Node Constructor.

    Args:
      csv_row: This node's csv row as a list of strings.
      lobe: A reference to this node's lobe object
      md: A Metadata object about nodes
    """
    self.csv = csv_row
    self.lobe = lobe
    self.md = md
    self.uID = csv_row[md.getPropIdx('Id')]
    x = float(csv_row[md.getPropIdx('X')])
    y = float(csv_row[md.getPropIdx('Y')])
    z = float(csv_row[md.getPropIdx('Z')])
    self.pos  = (x, y, z)

  def setThetas(self, t1, t2):
    """
    Set this node's angular width delimiters.

    Args:
      t1: Start theta in degrees
      t2: End theta in degrees
    Return:
      None
    """
    self.theta1 = t1
    self.theta2 = t2

  def __lt__(self, other):
    """
    Comparator to define ordering of nodes based on theta polar coordinate.

    Return:
      Boolean
    """
    (self_r, self_theta)   = cartesian2Polar( self.pos[0],  self.pos[1])
    (other_r, other_theta) = cartesian2Polar(other.pos[0], other.pos[1])
    return self_theta < other_theta

  def getLayerLabel(self, layer_i):
    """
    Get the label csv value for this node's i-th layer.

    Return:
      String label if it exists, empty string if not.
    """
    idx = self.md.getPropertyIdx('L', layer_i)
    if idx:
      return self.csv[idx]
    else:
      return config.NODE_DEFAULT_VAL['L'] 

  def getLayerDepth(self, layer_i):
    """
    Get the depth csv value for this node's i-th layer
    """
    idx = self.md.getPropertyIdx('D', layer_i)
    if idx:
      return self.csv[idx]
    else:
      return config.NODE_DEFAULT_VAL['D'] 

  def getLayerWidth(self):
    """
    Get this node's layer width csv value. Same for all layers.
    """
    idx = self.md.getPropertyIdx('W', 0)
    if idx:
      return self.csv[idx]
    else:
      return config.NODE_DEFAULT_VAL['W'] 

  def getLayerColor(self, layer_i):
    """
    Get the color csv value for this node's i-th layer. 
    """
    idx = self.md.getPropertyIdx('C', layer_i)
    if idx:
      return self.csv[idx]
    else:
      return config.NODE_DEFAULT_VAL['C'] 

  def weight(self):
    """
    Return the weight of this node
    """
    return float(self.getLayerWidth())
