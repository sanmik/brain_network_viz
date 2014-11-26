"""
  A class to maintain render properties about a Graph instance and provide
  methods for rendering that graph.
"""

# Library Imports
import bisect
import csv
import matplotlib
matplotlib.use("PDF")
import matplotlib.pyplot as plt
import matplotlib.axes as axes
from matplotlib.colors import hex2color, LinearSegmentedColormap, Normalize
from matplotlib.cm import ScalarMappable
import matplotlib.colorbar as colorbar
from matplotlib.patches import Circle, Wedge, Polygon, FancyBboxPatch, PathPatch, Rectangle
from matplotlib.path import Path
from matplotlib.text import _get_textbox
from matplotlib.collections import PatchCollection
from matplotlib.lines import Line2D
from math import degrees, radians, pi, cos, sin, floor, ceil
import numpy as np

# Local Module Imports
import config
from helper import polar2Cartesian, cartesian2Polar, midTheta, theta2Quadrant, \
                   minNetDiff, topRange, mapRangeParam, findRenderer, \
                   angularExtentsOverlap
from edge_renderer import EdgeRenderer
from node_renderer import NodeRenderer

class GraphRenderer:
  
  def __init__(self, graph, lobe_filename):
    """
    Constructor

    Args:
      graph: A Graph instance.
      lobe_filename: Filename of lobe file explicitly setting lobe extents. 
        None if no lobe file specified.
    """
    self.graph = graph
    self.node_renderers = [] # Unsorted
    self.edge_renderers = [] # Sorted by depth

    """ Lookup table for start and end thetas of lobes. 
        {(Lobe Name): (start_theta, end_theta)}         """
    self.lobe_extents = {}

    """ Lookup table for angular coords of nodes. For use by EdgeRenderers. 
        {(node name): theta}                                                """
    self.node_extents = {}

    self.fig = plt.figure(figsize=(8,8))
    self.ax = self.fig.add_axes([0,0,1,1])
    self.ax.set_xlim(-1.5, 1.5)
    self.ax.set_ylim(-1.5, 1.5)
    self.ax.set_aspect(1)
    self.ax.axis("off")

    # CASE I: Lobe File Specified
    # TODO: This no longer works now that lobes aren't uniquely identified by their name
    if lobe_filename:
      with open(lobe_filename, 'rb') as lobe_file:
        reader = csv.reader(lobe_file, delimiter='\t')
        for row in reader:
          lobe_name    = row[0]
          start_extent = float(row[1])
          end_extent   = float(row[2])
          self.lobe_extents[lobe_name] = [start_extent, end_extent]

    # CASE II: No Lobe File Specified - Layout based on node widths (weights)
    else:
      # Angular gap between lobes
      gap_wdth = config.TOTAL_GAP_DEGREES / len(self.graph.lobes)

      # Calculate Lobe extents
      extent_centers = []
      start_theta    = 0.0
      curr_theta     = start_theta
      for lobe in self.graph.sorted_lobes:
        # Calculate thetas counterclockwise from starting point curr_theta
        assert(len(lobe.nodes) > 0)
        lobe_wt = sum([n.weight() for n in lobe.nodes])
        lobe_wdth = (360.0 - config.TOTAL_GAP_DEGREES) * (lobe_wt / self.graph.total_wt)
        self.lobe_extents[lobe.uID] = [curr_theta, curr_theta + lobe_wdth]
        extent_centers.append(midTheta(curr_theta, curr_theta + lobe_wdth))
        curr_theta += lobe_wdth + gap_wdth
      assert(abs(curr_theta - 360.0) < 0.00001)

      # Calculate list of lobe centers of mass
      mass_centers = []
      for l in self.graph.sorted_lobes:
        center = l.centerOfMass()
        (r, theta) = cartesian2Polar(center[0], center[1])
        mass_centers.append(theta)

      # Shift lobe extents to more accurately reflect their physical locations
      self.offset = minNetDiff(mass_centers, extent_centers)
      for k in self.lobe_extents.keys():
        lex = self.lobe_extents[k]
        lex[0] += self.offset
        lex[1] += self.offset

    # Instantiate a RenderNode for each Node in self.graph.
    for lobe in self.graph.sorted_lobes:
      lex = self.lobe_extents[lobe.uID]
      lobe_start = lex[0]
      curr_theta = lex[0]
      for node in lobe.nodes:
        node_wt   = node.weight()
        node_wdth = (lex[1] - lex[0]) * (node_wt / lobe.weight())
        node_start = curr_theta
        curr_theta += node_wdth
        node_end   = curr_theta
        self.node_renderers.append(NodeRenderer(node, node_start, node_end))
        self.node_extents[node.uID] = (node_start, node_end) 
      assert(abs(curr_theta - lex[1]) < 0.00001)

    # Instantiate a RenderEdge for each Edge in self.graph
    for edge in self.graph.edges:
      bisect.insort(self.edge_renderers, EdgeRenderer(edge))

  def render(self, out_filename, edge_thresh):
    """
    Render this instance to a PDF.

    Args:
      out_filename: A string filename to save this PDF as.
      edge_thresh: A tuple defining an edge weight threshold, in the following 
        form, (percentage, use style code)
    """

    # Render each NodeRenderer
    for nr in self.node_renderers:
      nr.render(self.ax)

    # Render Node Labels
    self.renderNodeLabels()

    # Render EdgeRenderers
    to_render = []
    if edge_thresh:
      percent = edge_thresh[0]
      use_style = edge_thresh[1]
      if (use_style == config.EDGE_THRESH_1):
        edge_weights = [er.width for er in self.edge_renderers]
        thresh = topRange(edge_weights, percent)[0]
        to_render = [er for er in self.edge_renderers if er.width > thresh]
      elif (use_style == config.EDGE_THRESH_2):
        weight_sorted = sorted(self.edge_renderers, key=lambda er: er.width, reverse=True)
        num_edges = int(ceil(len(self.edge_renderers) * (percent / 100.0)))
        to_render = weight_sorted[:num_edges]
    else:
      to_render = self.edge_renderers
    for er in to_render:
      er.render(self.ax, self.node_extents)

    # Render each Lobe label
    self.renderLobeLabels()
      
    # Render Legends
    self.renderRingLegends()
    cur_y = 1.4
    (w, h) = self.renderEdgeLegend(-1.5, cur_y, 0.4)
    cur_y -= (h + 0.05)
    (w, h) = self.renderLabelLegend(-1.5, cur_y, 0.4)

    # OK. We're set to render ax.
    plt.savefig(out_filename)

  def renderLobeLabels(self):
    """
    Render all text lobe labels, detecting and resolving any text overlaps. 
    """
    renderer       = findRenderer(self.fig)
    lobes          = self.graph.lobes
    sorted_lobes   = self.graph.sorted_lobes

    """ level determines the radial distance of the label from the origin. 
    Increasing the level for some labels is the way we resolve overlaps. """
    level          = 0  

    last_txt       = None
    to_render      = [lobe.uID for lobe in sorted_lobes]
    next_to_render = []

    while to_render:
      for lobe_id in to_render:
        lobe = lobes[lobe_id]
        extents = self.lobe_extents[lobe_id]

        # Calculate lobe label position
        mid_theta = midTheta(*extents)
        quadrant  = theta2Quadrant(mid_theta)
        radius  = config.RING_RADIUS 
        radius += (len(self.graph.node_md.layers) + 1.5) * config.RING_DEPTH
        radius += level * (.4 * config.RING_DEPTH)
        (label_x, label_y) = polar2Cartesian(radius, mid_theta)

        # Draw lobe label 
        props = {
          'fontsize': 6,
          'va': 'center',
          'ha': 'center',
          'rotation_mode': 'anchor'
        }
        if quadrant == 1 or quadrant == 2:
          props["rotation"] = mid_theta - 90
        else:
          props["rotation"] = mid_theta + 90
        t = self.ax.text(label_x, label_y, lobe.name, props)

        # Get lobe label bounding box and transform it to data coords
        # http://matplotlib.org/users/transforms_tutorial.html?highlight=transform
        disp_to_data = self.ax.transData.inverted()
        bbox = t.get_window_extent(renderer).transformed(disp_to_data) 

        # Calculate cartesian endpoints of label text
        if quadrant == 2 or quadrant == 4:
          text_start = (bbox.x0, bbox.y0)
          text_end = (bbox.x1, bbox.y1)
        else:
          text_start = (bbox.x0 + bbox.width, bbox.y0)
          text_end = (bbox.x0, bbox.y1)

        # Ensure start and end in counterclockwise order
        v1 = text_start 
        v2 = (text_end[0] - text_start[0], text_end[1] - text_start[1])
        cross = np.cross(v1, v2)
        if cross < 0:
          tmp = text_start
          text_start = text_end
          text_end = tmp

        # Calculate angular start and end of label
        r, text_start_theta = cartesian2Polar(*text_start)
        r, text_end_theta   = cartesian2Polar(*text_end)

        # Case I: This text overlaps the last rendered. Move it to next level.
        if last_txt and \
           angularExtentsOverlap(last_txt[0], last_txt[1], 
                                 text_start_theta, text_end_theta):
          t.remove()
          next_to_render += [lobe_id]
        else:
          last_txt = (text_start_theta, text_end_theta)
          """ Uncomment to see line that I'm using to approximate text position
          self.ax.add_line(Line2D((text_start[0], text_end[0]), 
                                  (text_start[1], text_end[1]), 
                                  linewidth=0.5, color='red'))
          """
      level += 1
      last_txt = None
      to_render = next_to_render
      next_to_render = []

  def renderRingLegends(self):
    """
    Render legend boxes describing the properties visualized by each ring 
    (layer).
    """
    nodes = (n for n in self.graph.nodes.values())
    node = next(nodes)
    num_rings = len(node.md.layers)
    x = 1.1
    cur_y = 1.4
    width  = 0.4
    for i in range(num_rings):
      (w, h) = self.renderRingLegend(x, cur_y, width, i)
      cur_y -= (h + 0.05)

  def renderRingLegend(self, x, y, w, layer_i):
    """
    Render legend boxes showing metadata about the properties visualized by a 
    given ring (layer).

    Args:
      x, y: Coordinate of top left coordinate of this legend
      w: Width of the legend box
      layer_i: Layer index 
    Return:
      Tuple of final dimensions (w, h)
    """
    node  = next((n for n in self.graph.nodes.values()))
    md    = self.graph.node_md
    color_prop_name  = md.getPropertyName('C', layer_i)
    width_prop_name = md.getPropertyName('W', layer_i)
    thick_prop_name = md.getPropertyName('D', layer_i)
    if not (color_prop_name or thick_prop_name or width_prop_name):
      return (0.0, 0.0)

    dh = 0.045
    dw = w / 10.0
    title_size   = 6
    heading_size = 5
    text_size    = 4
    cur_y        = y

    # Ring Title
    title  = 'Ring ' + str(layer_i + 1)
    props  = {'va': 'center', 'ha': 'center', 'size': title_size}
    cur_y -= 1 * dh
    self.ax.text(x + w/2, cur_y, title, props)

    # Color Bar
    if color_prop_name:
      num_gradients    = len(config.NODE_COLOR_GRADIENTS)
      grad_start_color = config.NODE_COLOR_GRADIENTS[layer_i % num_gradients][0]
      grad_end_color   = config.NODE_COLOR_GRADIENTS[layer_i % num_gradients][1]
      color_min_val    = md.getPropertyMinVal('C', layer_i)
      color_max_val    = md.getPropertyMaxVal('C', layer_i)
      props = {'va': 'center', 'ha': 'left', 'size': heading_size}
      s = 'Color: ' + color_prop_name
      cur_y -= 1 * dh
      self.ax.text(x + dw, cur_y, s, props)

      colors = [grad_start_color, grad_end_color]
      index  = [0.0, 1.0]
      cm = LinearSegmentedColormap.from_list('my_colormap', zip(index, colors))

      """
      Create gradient effect with a series of small rectangles. Define an increasing set of
      values and use those values for lookup in a color map linearly interpolating between
      the start and end color.
      """
      grad_w = dw * 8 
      num_grad_segs = 100
      cur_y -= 1.0 * dh
      x0 = x + dw 
      values = np.array(xrange(num_grad_segs))
      dx = grad_w / num_grad_segs 
      grad_segs = []
      for j in xrange(num_grad_segs):
        grad_segs += [Rectangle((x0 + j * dx, cur_y), dx + .005, dh/2.0)]
      p = PatchCollection(grad_segs, edgecolors='none')
      p.set(array=values, cmap=cm)
      self.ax.add_collection(p)

      props = {'va': 'center', 'ha': 'left', 'size': text_size}
      cur_y -= 0.5 * dh
      self.ax.text(x + dw, cur_y, color_min_val, props)
      self.ax.text(x + 8.75 * dw, cur_y, color_max_val, props)
    
    # Width
    if width_prop_name:
      lobe_wt = sum((l.weight() for l in self.graph.sorted_lobes))
      coeff   = (360.0 - config.TOTAL_GAP_DEGREES) / lobe_wt 
      s = 'Width in degrees: '
      props = {'va': 'center', 'ha': 'left', 'size': heading_size}
      cur_y -= 1 * dh
      self.ax.text(x + dw, cur_y, s, props)
      props = {'va': 'center', 'ha': 'left', 'size': text_size}
      s = '({:s} val) x {:.2f}'.format(width_prop_name, coeff)
      cur_y -= 0.75 * dh
      self.ax.text(x + dw, cur_y, s, props)

    # Thickness 
    if thick_prop_name: # Don't render if its a default
      thick_min_val   = md.getPropertyMinVal('D', layer_i)
      thick_max_val   = md.getPropertyMaxVal('D', layer_i)
      props = {'va': 'center', 'ha': 'left', 'size': heading_size}
      s = 'Thickness: ' + thick_prop_name
      cur_y -= 1 * dh
      self.ax.text(x + dw, cur_y, s, props)

      start_x = x + dw
      end_x = start_x + config.RING_DEPTH
      cur_y -= 0.75 * dh
      self.ax.add_line(Line2D((start_x, end_x), (cur_y, cur_y), linewidth=0.5, color=cm(0.5)))
      tick_h = 0.1 * dh
      self.ax.add_line(Line2D((start_x, start_x), 
                              (cur_y - tick_h, cur_y + tick_h), 
                              linewidth=0.5, color=cm(0.5)))
      self.ax.add_line(Line2D((end_x, end_x), 
                              (cur_y - tick_h, cur_y + tick_h), 
                              linewidth=0.5, color=cm(0.5)))
      props = {'va': 'center', 'ha': 'left', 'size': text_size}
      s = '[' + str(thick_min_val) + ',  ' + str(thick_max_val) + ']'
      self.ax.text(end_x + 0.2 * dw, cur_y, s, props)
    
    # Outer Boundary
    cur_y -= 1 * dh
    h = abs(y - cur_y)
    self.renderRectangle(x, y, w, h)
    return (w, h)

  def renderEdgeLegend(self, x, y, w):
    """
    Render legend boxes showing metadata about the properties visualized by 
    graph edges.

    Args:
      x, y: Coordinate of top left coordinate of this legend
      w: Width and height of the legend box
    Return:
      Tuple of final dimensions (w, h). (0,0) if there are no edge properties 
      defined.
    """
    md = self.graph.edge_md
    color_prop_name = md.getPropertyName('C')
    thick_prop_name = md.getPropertyName('W')
    depth_prop_name = md.getPropertyName('D')
    if not (color_prop_name or thick_prop_name or depth_prop_name):
      return (0.0, 0.0)

    dh = 0.048
    dw = w / 10.0
    title_size   = 6
    heading_size = 5
    text_size    = 4
    cur_y        = y

    # Title
    title = 'Edges' 
    props = {'va': 'center', 'ha': 'center', 'size': title_size}
    cur_y -= 1 * dh
    self.ax.text(x + w/2, cur_y, title, props)
    cur_y -= 0.5 * dh

    # Color Bar
    if color_prop_name:
      props = {'va': 'center', 'ha': 'left', 'size': heading_size}
      s = 'Color: ' + color_prop_name
      cur_y -= 1 * dh
      self.ax.text(x + dw, cur_y, s, props)

      prop_idx         = md.getPropIdx(color_prop_name)
      attr_idx         = md.getAttrIdx('MIN_VAL')
      color_min_val    = md.data[attr_idx][prop_idx]
      attr_idx         = md.getAttrIdx('MAX_VAL')
      color_max_val    = md.data[attr_idx][prop_idx]
      grad_start_color = config.EDGE_COLOR_GRADIENT[0]
      grad_end_color   = config.EDGE_COLOR_GRADIENT[1]

      colors = [grad_start_color, grad_end_color]
      index  = [0.0, 1.0]
      cm = LinearSegmentedColormap.from_list('my_colormap', zip(index, colors))

      grad_w = dw * 8 
      num_grad_segs = 100
      x0 = x + dw 
      cur_y -= 1 * dh
      values = np.array(xrange(num_grad_segs))
      dx = grad_w / num_grad_segs 
      grad_segs = []
      for i in xrange(num_grad_segs):
        grad_segs += [Rectangle((x0 + i * dx, cur_y), dx + .005, dh/2)]
      p = PatchCollection(grad_segs, edgecolors='none')
      p.set(array=values, cmap=cm)
      self.ax.add_collection(p)

      props = {'va': 'center', 'ha': 'left', 'size': text_size}
      cur_y -= 0.3 * dh
      self.ax.text(x + dw, cur_y, color_min_val, props)
      self.ax.text(x + 8.75 * dw, cur_y, color_max_val, props)
    
    # Thickness 
    if thick_prop_name:
      prop_idx      = md.getPropIdx(thick_prop_name) 
      attr_idx      = md.getAttrIdx('MIN_VAL')
      thick_min_val = md.data[attr_idx][prop_idx]
      attr_idx      = md.getAttrIdx('MAX_VAL')
      thick_max_val = md.data[attr_idx][prop_idx]
      props = {'va': 'center', 'ha': 'left', 'size': heading_size}
      s = 'Thickness: ' + thick_prop_name
      cur_y -= 1 * dh
      self.ax.text(x + dw, cur_y, s, props)
      props = {'va': 'center', 'ha': 'left', 'size': text_size}
      s = '[' + str(thick_min_val) + '  -  ' + str(thick_max_val) + ']'
      cur_y -= 0.5 * dh
      self.ax.text(x + dw, cur_y, s, props)

    # Draw Order 
    if depth_prop_name:
      prop_idx      = md.getPropIdx(depth_prop_name) 
      attr_idx      = md.getAttrIdx('MIN_VAL')
      depth_min_val = md.data[attr_idx][prop_idx]
      attr_idx      = md.getAttrIdx('MAX_VAL')
      depth_max_val = md.data[attr_idx][prop_idx]
      props = {'va': 'center', 'ha': 'left', 'size': heading_size}
      s = 'Draw Order: ' + depth_prop_name
      cur_y -= 1.5 * dh
      self.ax.text(x + dw, cur_y, s, props)
      props = {'va': 'center', 'ha': 'left', 'size': text_size}
      s = '[bottom - top]: [' + str(depth_min_val) + '  -  ' + str(depth_max_val) + ']'
      cur_y -= 0.5 * dh
      self.ax.text(x + dw, cur_y, s, props)
    
    # Outer Boundary
    cur_y -= 1 * dh
    h = abs(y - cur_y)
    self.renderRectangle(x, y, w, h)
    return (w, h)

  def renderLabelLegend(self, x, y, w):
    """
    Render a legend box describing the order and property association of the
    set of labels accompanying each node.

    Args:
      x, y: Coordinate of top left coordinate of this legend
      w: Width of the legend box
    Return:
      Tuple of final dimensions (w, h). (0,0) if there are no labels to render.
    """
    md = self.graph.node_md
    num_labeled_layers = md.numLabeledLayers()
    if num_labeled_layers <= 1:
      return (0.0, 0.0)

    dh = 0.045
    dw = w / 10.0
    title_size   = 6
    heading_size = 5
    text_size    = 4
    cur_y        = y

    # Title
    title = 'Labels' 
    props = {'va': 'center', 'ha': 'center', 'size': title_size}
    cur_y -= 1.5 * dh
    self.ax.text(x + w/2, cur_y, title, props)

    # Labels 
    cur_y -= 2 * dh
    for layer_i, layer in enumerate(md.layers):
      prop_name  = md.getPropertyName('L', layer_i)
      if not prop_name:
        pass
      else:
        num_colors = len(config.LAYER_LABEL_COLORS)
        color = config.LAYER_LABEL_COLORS[layer_i % num_colors]
        props = {'va': 'center', 'ha': 'left', 'size': heading_size, 
                 'color': color}
        self.ax.text(x + dw, cur_y, prop_name, props)
        cur_y -= 0.75 * dh

    # Outer Boundary
    cur_y -= 1 * dh
    h = abs(y - cur_y)
    self.renderRectangle(x, y, w, h)
    return (w, h)

  def renderRectangle(self, x, y, w, h):
    """
    Render a rectangle on this graph_renderer's axes instance.

    Args:
      x, y: Bottom left corner coords
      w, h: Width and Height dimensions
    """
    verts = [
      (x + 0., y + 0.), # left, bottom
      (x + 0., y - h),  # left, top
      (x + w,  y - h),  # right, top
      (x + w,  y + 0.), # right, bottom
      (x + 0., y + 0.), # ignored
    ]
    codes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]
    path = Path(verts, codes)
    patch = PathPatch(path, facecolor='none', lw=0.2)
    self.ax.add_patch(patch)

  def renderNodeLabels(self):
    """
    Render all Node labels. 
    """
    md = self.graph.node_md
    num_labeled_layers = md.numLabeledLayers()

    # CASE I: No Labels
    if num_labeled_layers == 0:
      return

    # CASE II: Nodes Have 1 Label 
    if num_labeled_layers == 1:
      for nr in self.node_renderers:
        mid_theta   = midTheta(nr.start_theta, nr.end_theta)
        quadrant    = theta2Quadrant(mid_theta)
        radius      = config.RING_RADIUS
        radius     += len(md.layers) * config.RING_DEPTH
        radius     += 0.1 * config.RING_DEPTH
        node_width  = nr.end_theta - nr.start_theta
        num_pads    = 1

        label_theta        = mid_theta 
        (label_x, label_y) = polar2Cartesian(radius, label_theta)
        props = {
          'fontsize': 2.5,
          'color': '#000000',
          'rotation_mode': 'anchor'
        }
        if quadrant == 1 or quadrant == 4:
          props['rotation'] = label_theta
          props['va'] = 'center'
          props['ha'] = 'left'
        else:
          props['rotation'] = label_theta - 180
          props['va'] = 'center'
          props['ha'] = 'right'
        self.ax.text(label_x, label_y, nr.node.getLayerLabel(0), props)

    # CASE III: Nodes Have Multiple Labels
    else:
      num_labels = num_labeled_layers * len(self.node_renderers)
      label_w = 360.0 / num_labels
      cur_theta = self.offset 
      label_radius  = config.RING_RADIUS
      label_radius += len(md.layers) * config.RING_DEPTH
      label_radius += 0.3 * config.RING_DEPTH
      for nr in self.node_renderers:
        arc_start_theta = cur_theta + 0.5 * label_w
        arc_end_theta   = arc_start_theta + label_w * (num_labeled_layers - 1)
        for layer_i in range(num_labeled_layers):
          layer_label_text = nr.node.getLayerLabel(layer_i)

          label_theta = cur_theta + label_w / 2 
          quadrant    = theta2Quadrant(label_theta)
          (label_x, label_y) = polar2Cartesian(label_radius, label_theta)

          num_colors = len(config.LAYER_LABEL_COLORS)
          color      = config.LAYER_LABEL_COLORS[layer_i % num_colors]

          props = {
            'fontsize': 2.5,
            'color': color,
            'rotation_mode': 'anchor'
          }
          if quadrant == 1 or quadrant == 4:
            props['rotation'] = label_theta
            props['va']       = 'center'
            props['ha']       = 'left'
          else:
            props['rotation'] = label_theta - 180
            props['va']       = 'center'
            props['ha']       = 'right'
          self.ax.text(label_x, label_y, layer_label_text, props)
          cur_theta += label_w

        # Render label-grouping arc 
        label_arc_radius = label_radius - 0.01
        self.ax.add_patch(Wedge(config.RING_ORIGIN, 
                           label_arc_radius, 
                           arc_start_theta, arc_end_theta, 
                           width=0.001,
                           edgecolor='none',
                           facecolor='#555555'))

        # Draw a line from the label group arc to the node
        node_theta = midTheta(nr.start_theta, nr.end_theta)
        arc_len = arc_end_theta - arc_start_theta
        if (abs(node_theta - arc_start_theta) < abs(node_theta - arc_end_theta)):
          p1_theta = arc_start_theta + arc_len * 0.15
        else:
          p1_theta = arc_end_theta - arc_len * 0.15 
        p1 = polar2Cartesian(label_arc_radius - 0.001, p1_theta)

        last_layer_i = len(md.layers) - 1
        min_depth_csv    = md.getPropertyMinVal('D', last_layer_i)
        max_depth_csv    = md.getPropertyMaxVal('D', last_layer_i)
        layer_depth_csv  = nr.node.getLayerDepth(last_layer_i) 
        last_layer_depth = mapRangeParam(float(layer_depth_csv), float(min_depth_csv), 
                                         float(max_depth_csv), 0.0, -config.RING_DEPTH)
        r  = config.RING_RADIUS 
        r += config.RING_DEPTH * last_layer_i 
        r += -last_layer_depth
        p2 = polar2Cartesian(r, node_theta)
        self.ax.add_line(Line2D((p1[0], p2[0]), (p1[1], p2[1]), 
                                linewidth=0.1, color='#555555'))
