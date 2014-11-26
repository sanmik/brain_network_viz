"""
  A class to maintain model and render data about connections between brain
  nodes.
"""
import config

class Edge:
  def __init__(self, csv_row, start_node, end_node, md):
    """
    Construct an Edge instance.

    Args:
      csv_row: This edge's csv row as a list of strings.
      start_node: A reference to one endpoint Node of this edge.
      end_node: A reference to the other endpoint Node of this edge.
      md: A Metadata object about edges.
    """
    self.md = md
    self.csv = csv_row
    self.start_node = start_node
    self.end_node = end_node
