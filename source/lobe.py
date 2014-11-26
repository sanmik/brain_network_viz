"""
  A class to maintain model data about Lobes (collections of Nodes) 
"""
import bisect
from helper import centerOfMass, cartesian2Polar

class Lobe:
  def __init__(self, uID, name):
    """
    Lobe constructor.

    Args:
      uID: The unique ID string of this lobe
      name: The string name of this lobe.
    """
    # Model Data
    self.uID  = uID 
    self.name = name
    self.nodes = [] # Sorted by polar theta coord 

  def addNode(self, node):
    """
    Insert a new node into this lobe's sorted list.

    Args:
      node: A Node instance
    Return:
      None
    """
    bisect.insort(self.nodes, node)

  def weight(self):
    """
    Return the weight of this lobe.
    """
    return sum([node.weight() for node in self.nodes])

  def centerOfMass(self):
    """
    Return the center of mass of this lobe.

    Return:
      A 3-tuple of floats (x, y, z)
    """
    assert len(self.nodes) != 0
    node_positions = [node.pos for node in self.nodes]
    node_weights   = [node.weight() for node in self.nodes]
    return centerOfMass(node_positions, node_weights)

  def __lt__(self, other):
    """
    Comparator to define ordering of lobes based on theta polar coordinate of
    their center of mass.

    Precondition: Because ordering depends on weights, the operand lobe's
    nodes must have their layers list initialized.

    Return:
      Boolean
    """
    assert len(self.nodes)  != 0
    assert len(other.nodes) != 0
    # TODO: Write tests and delete old commented out code.
    #self_node_positions  = [node.pos for node in self.nodes]
    #self_node_weights    = [node.weight for node in self.nodes]
    #(self_x, self_y, self_z) = centerOfMass(self_node_positions, self_node_weights)
    (self_x, self_y, self_z) = self.centerOfMass()

    #other_node_positions = [node.pos for node in other.nodes]
    #other_node_weights   = [1] * len(other.nodes) # TODO: Account for weighted nodes
    #(other_x, other_y, other_z) = centerOfMass(other_node_positions, other_node_weights)
    (other_x, other_y, other_z) = other.centerOfMass()

    (self_r, self_theta)   = cartesian2Polar(self_x, self_y)
    (other_r, other_theta) = cartesian2Polar(other_x, other_y)
    return self_theta < other_theta
