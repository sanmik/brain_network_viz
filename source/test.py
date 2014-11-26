"""
  Unit tests
"""
from unittest import main, TestCase
from math import sqrt
import bisect
import config
import metadata
import graph
from graph_renderer import GraphRenderer
import node
from node_renderer import NodeRenderer
import edge
from edge_renderer import EdgeRenderer
import lobe
import helper

class Metadatatests(TestCase):

  def setUp(self):
    # Metadata about Nodes
    node_file = open('inputs/test/test_nodes.csv', 'r')
    self.node_md = metadata.NodeMetadata(node_file, 3, 'Id')
    node_file.close()

    # Metadata about Edges
    edge_file = open('inputs/test/test_edges.csv', 'r')
    self.edge_md = metadata.EdgeMetadata(edge_file, 3, 'Id')
    edge_file.close()

  def test_parse(self):
    # Nodes
    node_data = self.node_md.data
    node_prop_indices = self.node_md.prop_indices
    node_attr_indices = self.node_md.attr_indices
    expected_row_0 = ['Id', 'Lobe', 'X', 'Y', 'Z', 'Property1', 'Property2', 
                      'Property3', 'Property4', 'Property5', 'Property6', 
                      'Property7']
    expected_row_3 = ['USE_AS', 'G', 'P', 'P', 'P', 'C', 'W', 'D', 'L', 'C', 
                      'D', 'L']
    self.assertEqual(node_data[0], expected_row_0)
    self.assertEqual(node_data[3], expected_row_3)
    self.assertEqual(node_prop_indices['Id'], 0)
    self.assertEqual(node_prop_indices['Lobe'], 1)
    self.assertEqual(node_prop_indices['Property1'], 5)
    self.assertEqual(node_prop_indices['Property5'], 9)
    self.assertEqual(node_prop_indices['Property7'], 11)
    self.assertEqual(node_attr_indices['MIN_VAL'], 1)
    self.assertEqual(node_attr_indices['MAX_VAL'], 2)
    self.assertEqual(node_attr_indices['USE_AS'], 3)

    # Edges
    edge_data = self.edge_md.data
    edge_prop_indices = self.edge_md.prop_indices
    edge_attr_indices = self.edge_md.attr_indices
    expected_row_0 = ['Id', 'Node1', 'Node2', 'Property1', 'Property2', 'Property3', 'Property4']
    expected_row_3 = ['USE_AS', 'S', 'E', 'C', 'W', 'D', 'L']
    self.assertEqual(edge_data[0], expected_row_0)
    self.assertEqual(edge_data[3], expected_row_3)
    self.assertEqual(edge_prop_indices['Id'], 0)
    self.assertEqual(edge_prop_indices['Node1'], 1)
    self.assertEqual(edge_prop_indices['Property1'], 3)
    self.assertEqual(edge_prop_indices['Property4'], 6)
    self.assertEqual(edge_attr_indices['MIN_VAL'], 1)
    self.assertEqual(edge_attr_indices['MAX_VAL'], 2)
    self.assertEqual(edge_attr_indices['USE_AS'], 3)

  def test_get(self):
    self.assertEqual(self.node_md.get('Lobe', 'MIN_VAL'), 'NA')
    self.assertEqual(self.node_md.get('Lobe', 'MAX_VAL'), 'NA')
    self.assertEqual(self.node_md.get('Z', 'MIN_VAL'), '-10')
    self.assertEqual(self.edge_md.get('Property1', 'USE_AS'), 'C')
    self.assertEqual(self.edge_md.get('Property2', 'MIN_VAL'), '-6')
    self.assertEqual(self.edge_md.get('Property2', 'MAX_VAL'), '2.8')

class EdgeMetadataTests(TestCase):

  def setUp(self):
    edge_file = open('inputs/test/test_edges.csv', 'r')
    self.edge_md = metadata.EdgeMetadata(edge_file, 3, 'Id')
    edge_file.close()

  def testGetPropertyName(self):
    self.assertEqual(self.edge_md.getPropertyName('C'), 'Property1')
    self.assertEqual(self.edge_md.getPropertyName('W'), 'Property2')
    self.assertEqual(self.edge_md.getPropertyName('D'), 'Property3')
    self.assertEqual(self.edge_md.getPropertyName('L'), 'Property4')

  # TODO: Test get methods

class NodeMetadataTests(TestCase):

  def setUp(self):
    node_file = open('inputs/test/test_nodes.csv', 'r')
    self.node_md = metadata.NodeMetadata(node_file, 3, 'Id')
    node_file.close()

  def testGetPropertyName(self):
    self.assertEqual(self.node_md.getPropertyName('C', 0), 'Property1')
    self.assertEqual(self.node_md.getPropertyName('C', 1), 'Property5')
    self.assertEqual(self.node_md.getPropertyName('W', 0), 'Property2')
    self.assertEqual(self.node_md.getPropertyName('D', 0), 'Property3')
    self.assertEqual(self.node_md.getPropertyName('D', 1), 'Property6')
    self.assertEqual(self.node_md.getPropertyName('L', 0), 'Property4')
    self.assertEqual(self.node_md.getPropertyName('L', 1), 'Property7')

  def testGetPropertyIndex(self):
    self.assertEqual(self.node_md.getPropertyIdx('C', 0), 5)
    self.assertEqual(self.node_md.getPropertyIdx('W', 0), 6)
    self.assertEqual(self.node_md.getPropertyIdx('C', 1), 9)
    self.assertEqual(self.node_md.getPropertyIdx('L', 1), 11)

  def testGetPropertyMinVal(self):
    self.assertEqual(self.node_md.getPropertyMinVal('C', 0), '0')
    self.assertEqual(self.node_md.getPropertyMinVal('C', 1), '-5')
    self.assertEqual(self.node_md.getPropertyMinVal('L', 1), 'NA')

  def testGetPropertyMaxVal(self):
    self.assertEqual(self.node_md.getPropertyMaxVal('C', 0), '1')
    self.assertEqual(self.node_md.getPropertyMaxVal('C', 1), '1')
    self.assertEqual(self.node_md.getPropertyMaxVal('L', 1), 'NA')

class GraphTests(TestCase):

  def setUp(self):
    node_file = open('inputs/test/test_nodes.csv', 'r')
    node_md = metadata.NodeMetadata(node_file, 3, 'Id')
    node_file.close()
    edge_file = open('inputs/test/test_edges.csv', 'r')
    edge_md = metadata.EdgeMetadata(edge_file, 3, 'Id')
    edge_file.close()
    self.g = graph.Graph(node_md, edge_md, 'inputs/test/test_nodes.csv', 
                         'inputs/test/test_edges.csv')

  def test_graph_constructor_1(self):
    self.assertEqual(len(self.g.nodes), 6)
    self.assertEqual(len(self.g.lobes), 3)
    self.assertEqual(len(self.g.sorted_lobes), 3) 
    self.assertEqual(len(self.g.edges), 4) 
    self.assertEqual(self.g.total_wt, 66.0)

    self.assertTrue('Lobe1_R' in self.g.lobes)
    self.assertTrue('Lobe3_L' in self.g.lobes)

    self.assertTrue('0' in self.g.nodes)
    self.assertTrue('2' in self.g.nodes)
    self.assertTrue('5' in self.g.nodes)

  # Test Lobe/Node two way mappings
  def test_graph_constructor_2(self):
    l1 = self.g.lobes['Lobe1_R']
    n1 = self.g.nodes['0']
    n2 = self.g.nodes['1']
    
    self.assertEqual(len(l1.nodes), 2)
    self.assertTrue(n1 in l1.nodes)
    self.assertTrue(n2 in l1.nodes)
    self.assertIs(l1, n1.lobe)
    self.assertIs(l1, n2.lobe)

    l3 = self.g.lobes['Lobe3_L']
    n6 = self.g.nodes['5']
    self.assertTrue(n6 in l3.nodes)
    self.assertEqual(l3, n6.lobe)

  # Check lobes are properly sorted
  def test_graph_constructor_3(self):
    first = self.g.sorted_lobes[0]
    last  = self.g.sorted_lobes[2]

    self.assertTrue(first.name, 'Lobe1')
    self.assertTrue(last.name, 'Lobe2')

class NodeTests(TestCase):

  def setUp(self):
    node_file = open('inputs/test/test_nodes.csv', 'r')
    self.node_md = metadata.NodeMetadata(node_file, 3, 'Id')
    node_file.close()

  def testNodeConstruct(self):
    node_row = ['0', 'Lobe1', '4.134981157', '-0.8118574228', 
                '-0.3647469077', '0.2', '10', '2', 'AAA', '-3.8'] 
    n1 = node.Node(node_row, None, self.node_md)
    self.assertAlmostEqual(n1.pos[0], 4.134981157)
    self.assertAlmostEqual(n1.pos[1], -0.8118574228)
    self.assertAlmostEqual(n1.pos[2], -0.3647469077)
    self.assertEqual(n1.uID, '0')

  #TODO: Test get methods
    
    # TODO: Test what a second layer would do when not provided a color, for example. Etc.

  def testNodeLessThan(self):
    node_row_1 = ['Node1', 'Lobe1', '0.0', '10.8118574228', 
                '0.3647469077', '0.2', '10', '2', 'AAA', '-3.8'] 
    node_row_2 = ['Node2', 'Lobe1', '4.134981157', '-0.8118574228', 
                '-0.3647469077', '0.2', '10', '2', 'BBB', '-3.8'] 
    n1 = node.Node(node_row_1, None, self.node_md)
    n2 = node.Node(node_row_2, None, self.node_md)
    self.assertLess(n1, n2)

class HelperTests(TestCase):

  def testCalcColor(self):
    self.assertEqual(helper.calcColor('#000000', '#FFFFFF', 5.0, 0.0, 10.0), 
                     '#7F7F7F')
    self.assertEqual(helper.calcColor('#FF0000', '#00FF00', 5.0, 10.0, 0.0), 
                     '#7F7F00')

  def testMapRangeParam(self):
    self.assertEqual(helper.mapRangeParam(1.0, 0.0, 2.0, 0.0, 10.0), 5.0)
    self.assertEqual(helper.mapRangeParam(1.0, 0.0, 2.0, 0.0, 2.0), 1.0)
    self.assertEqual(helper.mapRangeParam(1.0, 0.0, 2.0, 2.0, 0.0), 1.0)

  def testCenterOfMass(self):
    positions = [( 1.0,  0.0, 0.0), 
                 ( 0.0,  2.5, 0.0), 
                 (-1.0,  0.0, 0.0), 
                 ( 0.0, -2.5, 0.0)]
    weights   = [1.0, 1.0, 1.0, 1.0]
    self.assertEqual(helper.centerOfMass(positions, weights), (0.0, 0.0, 0.0))

    positions = [(0.5,  2.5, 0.0), 
                 (2.0,  0.5, 0.0), 
                 (3.5,  2.5, 0.0)] 
    weights   = [3.0, 4.0, 3.0]
    self.assertEqual(helper.centerOfMass(positions, weights), (2.0, 1.7, 0.0))

  def testCartesianToPolar(self):
    (r, t) = helper.cartesian2Polar(12.0, 5.0)
    self.assertEqual(r, 13.0)
    self.assertAlmostEqual(t, 22.61986495, places=7)

    (r, t) = helper.cartesian2Polar(1.0, -1.0)
    self.assertEqual(t, 315.0)
    self.assertEqual(r, sqrt(2))

  def testPolarToCartesian(self):
    (r, t) = (13.0, 22.6)
    (x, y) = helper.polar2Cartesian(r, t)
    self.assertAlmostEqual(x, 12.00173282, places=7)
    self.assertAlmostEqual(y, 4.995839195, places=7)

    (r, t) = (sqrt(2), 225.0)
    (x, y) = helper.polar2Cartesian(r, t)
    self.assertAlmostEqual(x, -1.0)
    self.assertAlmostEqual(y, -1.0)

  def testMinNetDiff(self):
    a = [45, 135, 300]
    b = [30, 95, 230]
    s = helper.minNetDiff(a, b)
    self.assertEqual(s, 125.0 / 3.0)

    a = [1] * 10000
    b = [1] * 10000
    s = helper.minNetDiff(a, b)
    self.assertEqual(s, 0.0)

    a = [270] * 10000
    b = [180] * 10000
    s = helper.minNetDiff(a, b)
    self.assertEqual(s, 90.0)

    a = [180] * 10000
    b = [270] * 10000
    s = helper.minNetDiff(a, b)
    self.assertEqual(s, -90.0)

  def testTopRange(self):
    r = range(100 + 1)

    t1 = helper.topRange(r, 1)
    self.assertAlmostEqual(t1[0], 99, places=4)
    self.assertEqual(t1[1], 100)

    t2 = helper.topRange(r, 15)
    self.assertAlmostEqual(t2[0], 85, places=4)
    self.assertEqual(t2[1], 100)

  def testAngularExtentsOverlap(self):
    a1 = 0
    a2 = 1
    b1 = 2
    b2 = 3
    self.assertFalse(helper.angularExtentsOverlap(a1, a2, b1, b2))
    self.assertFalse(helper.angularExtentsOverlap(b1, b2, a1, a2))

    a1 = 0
    a2 = 3
    b1 = 1
    b2 = 2
    self.assertTrue(helper.angularExtentsOverlap(a1, a2, b1, b2))
    self.assertTrue(helper.angularExtentsOverlap(b1, b2, a1, a2))

    a1 = 2
    a2 = 4
    b1 = 1
    b2 = 3
    self.assertTrue(helper.angularExtentsOverlap(a1, a2, b1, b2))
    self.assertTrue(helper.angularExtentsOverlap(b1, b2, a1, a2))


class EdgeTests(TestCase):

  def setUp(self):
    node_file = open('inputs/test/test_nodes.csv', 'r')
    self.node_md = metadata.NodeMetadata(node_file, 3, 'Id')
    node_file.close()
    edge_file = open('inputs/test/test_edges.csv', 'r')
    self.edge_md = metadata.EdgeMetadata(edge_file, 3, 'Id')
    edge_file.close()

  def testEdgeConstruct(self):
    edge_row = ['0', 'Node0', 'Node1', '10', '2', '0.2', 'AAA']
    node1_row = ['Node1', 'Lobe1', '0', '0', '0', '0', '0', '0', 'AAA', '0'] 
    node2_row = ['Node2', 'Lobe1', '0', '0', '0', '0', '0', '0', 'BBB', '0'] 
    n1 = node.Node(node1_row, None, self.node_md)
    n2 = node.Node(node2_row, None, self.node_md)
    e1 = edge.Edge(edge_row, n1, n2, self.edge_md)
    self.assertIs(e1.start_node, n1)
    self.assertIs(e1.end_node, n2)

class LobeTests(TestCase):

  def setUp(self):
    node_file = open('inputs/test/test_nodes.csv', 'r')
    self.node_md = metadata.NodeMetadata(node_file, 3, 'Id')
    node_file.close()

  def testAddNode(self):
    l = lobe.Lobe('Lobe1', 'Lobe1_L')
    node_row_1 = ['Node1', 'Lobe1', '-0.2', '10.8118574228', 
                '0.3647469077', '0.2', '10', '2', 'AAA', '-3.8'] 
    node_row_2 = ['Node2', 'Lobe1', '-4.134981157', '-0.8118574228', 
                '-0.3647469077', '0.2', '10', '2', 'BBB', '-3.8'] 
    node_row_3 = ['Node3', 'Lobe1', '-1.0', '-0.8118574228', 
                '-0.3647469077', '0.2', '10', '2', 'CCC', '-3.8'] 
    n1 = node.Node(node_row_1, None, self.node_md)
    n2 = node.Node(node_row_2, None, self.node_md)
    n3 = node.Node(node_row_3, None, self.node_md)
    l.addNode(n3)
    l.addNode(n2)
    l.addNode(n1)
    self.assertEqual(len(l.nodes), 3)
    self.assertIs(l.nodes[0], n1)
    self.assertIs(l.nodes[1], n2)
    self.assertIs(l.nodes[2], n3)

  def testLessThan(self):
    l1 = lobe.Lobe('Lobe1', 'Lobe1_R')
    l2 = lobe.Lobe('Lobe2', 'Lobe1_R')
    node_row_1 = ['Node1', 'Lobe1', '0.1', '1.0', 
                '0.3647469077', '0.2', '10', '2', 'AAA', '-3.8'] 
    node_row_2 = ['Node2', 'Lobe1', '4.0', '4.0', 
                '-0.3647469077', '0.2', '10', '2', 'BBB', '-3.8'] 
    node_row_3 = ['Node3', 'Lobe2', '-1.0', '-1.0', 
                '-0.3647469077', '0.2', '10', '2', 'CCC', '-3.8'] 
    node_row_4 = ['Node4', 'Lobe2', '1.0', '-1.0', 
                '-0.3647469077', '0.2', '10', '2', 'DDD', '-3.8'] 
    n1 = node.Node(node_row_1, l1, self.node_md)
    #n1.addLayerProperties()
    n2 = node.Node(node_row_2, l1, self.node_md)
    n3 = node.Node(node_row_3, l2, self.node_md)
    n4 = node.Node(node_row_4, l2, self.node_md)
    l1.addNode(n2)
    l1.addNode(n1)
    l2.addNode(n4)
    l2.addNode(n3)
    self.assertLess(l1, l2)
    self.assertLessEqual(l1, l1)
    self.assertGreaterEqual(l1, l1)

  def testWeight(self):
    l1 = lobe.Lobe('Lobe1', 'Lobe1_R')
    l2 = lobe.Lobe('Lobe2', 'Lobe1_R')
    node_row_1 = ['Node1', 'Lobe1', '0.1', '1.0', 
                '0.3647469077', '0.2', '10', '2', 'AAA', '-3.8'] 
    node_row_2 = ['Node2', 'Lobe1', '4.0', '4.0', 
                '-0.3647469077', '0.2', '11', '2', 'BBB', '-3.8'] 
    node_row_3 = ['Node3', 'Lobe2', '-1.0', '-1.0', 
                '-0.3647469077', '0.2', '12', '2', 'CCC', '-3.8'] 
    node_row_4 = ['Node4', 'Lobe2', '1.0', '-1.0', 
                '-0.3647469077', '0.2', '13', '2', 'DDD', '-3.8'] 
    n1 = node.Node(node_row_1, l1, self.node_md)
    #n1.addLayerProperties()
    n2 = node.Node(node_row_2, l1, self.node_md)
    n3 = node.Node(node_row_3, l2, self.node_md)
    n4 = node.Node(node_row_4, l2, self.node_md)
    l1.addNode(n2)
    l1.addNode(n1)
    l2.addNode(n4)
    l2.addNode(n3)
    self.assertEqual(l1.weight(), 21)
    self.assertEqual(l2.weight(), 25)

class GraphRendererTests(TestCase):
  def setUp(self):
    node_file = open('inputs/test/test_nodes.csv', 'r')
    node_md = metadata.NodeMetadata(node_file, 3, 'Id')
    node_file.close()
    edge_file = open('inputs/test/test_edges.csv', 'r')
    edge_md = metadata.EdgeMetadata(edge_file, 3, 'Id')
    edge_file.close()
    self.g = graph.Graph(node_md, edge_md, 'inputs/test/test_nodes.csv', 
                         'inputs/test/test_edges.csv')
    self.gr = GraphRenderer(self.g, None)
  
  def test_constructor(self):
    self.assertIs(self.gr.graph, self.g)
    self.assertEqual(len(self.gr.node_renderers), 6) 

    # EdgeRenderers should be sorted by depth
    self.assertEqual(len(self.gr.edge_renderers), 4)
    self.assertEqual(self.gr.edge_renderers[0].depth, 0.1)
    self.assertEqual(self.gr.edge_renderers[3].depth, 0.9)

    self.assertAlmostEqual(self.gr.lobe_extents['Lobe1_R'][0], -40.79638642722060)
    self.assertAlmostEqual(self.gr.lobe_extents['Lobe1_R'][1], 69.2036135727794)
    self.assertAlmostEqual(self.gr.lobe_extents['Lobe3_L'][0], 184.2036135727794)
    self.assertAlmostEqual(self.gr.lobe_extents['Lobe3_L'][1], 309.2036135727794)

    self.assertEqual(self.gr.node_extents['0'], 
                     (-40.796386427220604, 9.203613572779396))
    self.assertEqual(self.gr.node_extents['1'], 
                     (9.203613572779396, 69.20361357277939))
    self.assertEqual(self.gr.node_extents['5'], 
                     (184.2036135727794, 239.20361357277937))

  def test_lobe_offset(self):
    node_file = open('inputs/test/test_nodes2.csv', 'r')
    node_md = metadata.NodeMetadata(node_file, 3, 'Id')
    node_file.close()
    edge_file = open('inputs/test/test_edges2.csv', 'r')
    edge_md = metadata.EdgeMetadata(edge_file, 3, 'Id')
    edge_file.close()
    g = graph.Graph(node_md, edge_md, 'inputs/test/test_nodes2.csv', 
                         'inputs/test/test_edges2.csv')
    gr = GraphRenderer(g, None)
    self.assertAlmostEqual(gr.lobe_extents['Lobe1_R'][0], -25.17309277278332)
    self.assertAlmostEqual(gr.lobe_extents['Lobe1_R'][1], 159.9488584467289)
    self.assertAlmostEqual(gr.lobe_extents['Lobe2_L'][0], 174.9488584467289)
    self.assertAlmostEqual(gr.lobe_extents['Lobe2_L'][1], 319.8269072272167)
    
class NodeRendererTests(TestCase):
  def setUp(self):
    node_file = open('inputs/test/test_nodes.csv', 'r')
    node_md = metadata.NodeMetadata(node_file, 3, 'Id')
    node_file.close()
    edge_file = open('inputs/test/test_edges.csv', 'r')
    edge_md = metadata.EdgeMetadata(edge_file, 3, 'Id')
    edge_file.close()
    self.g = graph.Graph(node_md, edge_md, 'inputs/test/test_nodes.csv', 
                         'inputs/test/test_edges.csv')
  
  def test_constructor(self):
    nr = NodeRenderer(self.g.nodes['0'], 0.0, 55.0)
    self.assertEqual(nr.start_theta, 0.0)
    self.assertEqual(nr.end_theta, 55.0)

class EdgeRendererTests(TestCase):
  def setUp(self):
    node_file = open('inputs/test/test_nodes.csv', 'r')
    node_md = metadata.NodeMetadata(node_file, 3, 'Id')
    node_file.close()
    edge_file = open('inputs/test/test_edges.csv', 'r')
    edge_md = metadata.EdgeMetadata(edge_file, 3, 'Id')
    edge_file.close()
    self.g = graph.Graph(node_md, edge_md, 'inputs/test/test_nodes.csv', 
                         'inputs/test/test_edges.csv')
  
  def test_constructor(self):
    er = EdgeRenderer(self.g.edges[0])

    self.assertEqual(er.color, '#BC5228')
    self.assertAlmostEqual(er.width, 1.818181818, places=4)
    self.assertEqual(er.depth, 0.2)
    self.assertEqual(er.label, 'A')

  def test_edge_order(self):
    er0 = EdgeRenderer(self.g.edges[0])
    er3 = EdgeRenderer(self.g.edges[3])
    
    self.assertEqual(er0.depth, 0.2)
    self.assertEqual(er3.depth, 0.1)
    self.assertLess(er3, er0)

if __name__ == '__main__':
  main()
