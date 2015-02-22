"""
  Main driver program to render a neuronal connection data.

  Developed for use with Python 2.7
"""

# Library Imports
import sys
import bisect
import argparse
import csv
import os

# Local module imports
import config
from graph import Graph
from graph_renderer import GraphRenderer
from metadata import NodeMetadata, EdgeMetadata

def main(nodefile, edgefile, outimage='fmri-viz.pdf', sdef=100):
  # Parse command line args
  parser = argparse.ArgumentParser(prog='fmri-viz',
             description='An fmri graph visualization tool')
  parser.add_argument('-n', help='Node csv filename', default=nodefile)
  parser.add_argument('-e', help='Edge csv filename', default=edgefile)
  parser.add_argument('-a', help='Edge adjacency matrix csv filename')
  parser.add_argument('-l', help='Lobe extent file')
  parser.add_argument('-s', type=int, default=sdef,
    help='Specifies that only edges with a weight in the top s percent of ' +
         'the full range of edge weights will be rendered')
  parser.add_argument('-t', type=int,
    help='Specifies that t% of edges will be rendered. Those edges will be' +
         'those with the highest weights. If there is a tie between ' + 
         'candidates of the same weight, it will be broken non-deterministically')
  parser.add_argument('-o', help='output filename', default=outimage)
  args = parser.parse_args()
  node_filename   = args.n
  edge_filename   = args.e
  adj_filename    = args.a
  lobe_filename   = args.l
  edge_percent_s  = args.s 
  edge_percent_t  = args.t 
  output_filename = args.o

  if (edge_filename is None) and (adj_filename is None):
    parser.error('You must specify either a standard edge file (-e) or' +
                 'an adjacency edge file (-a)') 
  if edge_percent_s and edge_percent_t:
    parser.error('You must filter edges with either -s or -t, not both') 

  # Parse Node and Edge CSV for metadata
  node_file = open(node_filename, 'rb')
  if adj_filename:
    temp_edge_filename = generateEdgeFile(adj_filename)
    edge_filename = temp_edge_filename
  edge_file = open(edge_filename, 'rb')
  node_md = NodeMetadata(node_file, config.NUM_NODE_METADATA_ROWS, 'Id')
  edge_md = EdgeMetadata(edge_file, config.NUM_EDGE_METADATA_ROWS, 'Id')
  node_file.close()
  edge_file.close()

  # Edge Threshold Info
  edge_thresh = None
  if edge_percent_s:
    edge_thresh = (edge_percent_s, config.EDGE_THRESH_1)
  elif edge_percent_t:
    edge_thresh = (edge_percent_t, config.EDGE_THRESH_2)

  # Lets go!
  g  = Graph(node_md, edge_md, node_filename, edge_filename)
  gr = GraphRenderer(g, lobe_filename)
  gr.render(output_filename, edge_thresh)

  # Cleanup
  if adj_filename:
    os.remove(temp_edge_filename)

def generateEdgeFile(adj_filename):
  """
  Generate a temporary standard edge file based on the given adjacency edge
  file.

  Return:
    The filename of the generated temp CSV file
  """
  # Parse the adjacency file
  edges = []
  edge_id = 0
  min_v = None
  max_v = None
  min_depth = 0
  depth     = 0
  num_nodes = 0
  with open(adj_filename, 'r') as adj_f:
    r = csv.reader(adj_f, delimiter='\t')
    for row_idx, row in enumerate(r):
      if not num_nodes:
        num_nodes = len(row)
      else:
        assert len(row) == num_nodes
      for col_idx, v in enumerate(row):
        if v:
          v = float(v)
          if not min_v:
            min_v = v
            max_v = v
          if (v < min_v):
            min_v = v
          if v > max_v:
            max_v = v
          start  = 'Node' + str(row_idx + 1)
          end    = 'Node' + str(col_idx + 1)
          depth += 1 
          edges.append([edge_id, start, end, v, v, depth, ''])
          edge_id += 1
  max_depth = depth

  # Create temporary edge CSV file
  temp_edge_filename = 'temp_edges.csv'
  with open(temp_edge_filename, 'w') as edge_f:
    w = csv.writer(edge_f, delimiter='\t')
    header_row =   ['Id', 'Node1', 'Node2', 'Property1', 'Property2', 'Property3', 'Property4']
    meta_row_min = ['MIN_VAL', 'NA', 'NA', str(min_v), str(min_v), str(min_depth), 'NA']
    meta_row_max = ['MAX_VAL', 'NA', 'NA', str(max_v), str(max_v), str(max_depth), 'NA']
    meta_row_use = ['USE_AS', 'S', 'E', 'C', 'W', 'D', 'L']
    w.writerow(header_row)
    w.writerow(meta_row_min)
    w.writerow(meta_row_max)
    w.writerow(meta_row_use)
    for edge in edges: 
      w.writerow(edge)
  return temp_edge_filename

if __name__ == '__main__':
  main()
