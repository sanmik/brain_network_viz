"""
  Maintain model data about all Lobes, Nodes, and Edges involved in this 
  visualization. Handles parsing input files and constructing those entities.
"""
# Library Imports
import csv
import bisect

# Local Module Imports
import config 
from lobe import Lobe
from node import Node
from edge import Edge

class Graph:
  def __init__(self, node_md, edge_md, node_filename, edge_filename):
    """
    Construct a graph object from the given input files.

    Args:
      node_md: A Metadata instance populated with node metadata
      edge_md: A Metadata instance populated with edge metadata
      node_filename: The file name of the CSV node input file
      edge_filename: The file name of the CSV edge input file
    """
    self.node_md = node_md
    self.edge_md = edge_md
    self.node_filename = node_filename
    self.edge_filename = edge_filename

    # Declare graph state attributes. Will be populated during CSV parsing.
    self.lobes = {}
    self.sorted_lobes = [] # Sorted 
    self.nodes = {} 
    self.edges = []        # Unsorted 
    self.total_wt = 0.0

    # Parse Node CSV for data and generate objects
    with open(node_filename, "rb") as node_file:
      dialect = csv.Sniffer().sniff(node_file.read(1024), delimiters=",\t")
      node_file.seek(0)
      reader = csv.reader(node_file, dialect)
      for row in reader:
        if reader.line_num > config.NUM_NODE_METADATA_ROWS + 1:
          node_id   = row[self.node_md.getPropIdx('Id')]
          x_val     = float(row[self.node_md.getPropIdx('X')])
          lobe_name = row[self.node_md.getPropIdx('Lobe')]
          lobe_id   = (lobe_name + '_L') if x_val <= 0 else (lobe_name + '_R')
          if lobe_id not in self.lobes: 
            self.lobes[lobe_id] = Lobe(lobe_id, lobe_name)
          # Create new Node object and add it to top level lookup
          new_node = Node(row, self.lobes[lobe_id], self.node_md)
          self.nodes[node_id] = new_node
          # Map from lobe to node for reverse lookup
          self.lobes[lobe_id].addNode(new_node) 

    # Calculate total graph weight 
    for node in self.nodes.values():
      self.total_wt += node.weight()

    # Calculate sorted lobe list
    for lobe in self.lobes.values():
      bisect.insort(self.sorted_lobes, lobe)

    # Parse Edge CSV for data
    with open(edge_filename, "rb") as edge_file:
      dialect = csv.Sniffer().sniff(edge_file.read(1024), delimiters=",\t")
      edge_file.seek(0)
      reader = csv.reader(edge_file, dialect)
      for row in reader:
        if reader.line_num > config.NUM_EDGE_METADATA_ROWS + 1:
          # Find node endpoints
          n1_key = row[self.edge_md.getPropIdx("Node1")]
          n2_key = row[self.edge_md.getPropIdx("Node2")]
          node1  = self.nodes[n1_key]
          node2  = self.nodes[n2_key]
          self.edges.append(Edge(row, node1, node2, self.edge_md))
