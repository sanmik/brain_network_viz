"""
  A set of helper functions that have no other home.
"""
from math import degrees, radians, pi, sqrt, cos, sin
import numpy

def centerOfMass(positions, weights):
  """
  Calculate the center of mass of a set of weighted positions.

  Args:
    positions: A list of (x,y,z) position tuples
    weights: A list of position weights 
  Return:
    A tuple of floats representing the coordinates of the center of mass.
  """
  tot_weight = sum(weights) 
  assert tot_weight != 0
  zipped = zip(positions, weights)
  [x, y, z] = [0.0, 0.0, 0.0]
  for (pos, weight) in zipped:
    x += pos[0] * weight 
    y += pos[1] * weight 
    z += pos[2] * weight 
  return tuple(map(lambda k: k / tot_weight, [x,y,z]))

"""
  Return the cartesian coordinates corresponding to the given polar coords.

  Args:
    r: Radial coordinate
    theta: Angular coordinate (in degrees)
  Return:
    Cartesian coordinate 2-tuple
"""
def polar2Cartesian(r, theta):
  x = r * cos(radians(theta))
  y = r * sin(radians(theta))
  return (x, y)

def cartesian2Polar(x, y):
  """
  Return the polar coordinates corresponding to the given cartesian coords.

  Args:
    x: Cartesian x coordinate
    y: Cartesian y coordinate
  Return:
    Polar coordinate tuple (r, theta) with theta in degrees [0,359]
  """
  r = sqrt(x ** 2 + y ** 2)
  theta = degrees(numpy.arctan2(y, x)) % 360
  return (r, theta)

"""
  Return the angular midpoint of the 2 given angular coordinates.
"""
def midTheta(theta1, theta2):
  return (theta1 + theta2) / 2

"""
  Find out which Cartesian quadrant the given theta lies in.
  
  Args:
    theta Angular coordinate (in degrees)
  Return:
    Integer quadrant number
"""
def theta2Quadrant(theta):
  theta = theta % 360.0 
  if theta >= 0 and theta < 90.0:
    return 1
  if theta < 180.0:
    return 2
  if theta < 270.0:
    return 3
  return 4

def calcColor(col1, col2, u, min_u, max_u):
  """
  Args:
    col1: String of first color
    col2: String of first color
    u: Interpolation parameter in range [min_u, max_u]
    min_u
    max_u
  Return:
    Hex string interpolated color
  """
  assert type(u) is float
  assert type(min_u) is float
  assert type(max_u) is float

  # Remove '#'
  col1 = col1[1:]
  col2 = col2[1:]

  # Calculate decimal RGB vals
  col1_rgb = [int(col1[:2], 16), int(col1[2:4], 16), int(col1[4:], 16)]
  col2_rgb = [int(col2[:2], 16), int(col2[2:4], 16), int(col2[4:], 16)]
  result_rgb = [0,0,0]

  # Calculate normalized parameter u
  assert max_u - min_u != 0.0
  # v = (u - min_u) / (max_u - min_u)
  v = mapRangeParam(u, min_u, max_u, 0.0, 1.0)
  assert 0.0 <= v <= 1.0

  for i in range(3):
    result_rgb[i] = int(v * (col2_rgb[i] - col1_rgb[i]) + col1_rgb[i])
    0 <= result_rgb[i] <= 255

  result_str = "#%0.2X" % result_rgb[0]
  result_str += "%0.2X" % result_rgb[1]
  result_str += "%0.2X" % result_rgb[2]
  return result_str

def mapRangeParam(u, min_u, max_u, min_v, max_v):
  """
  Linearly map a floating point value u in the range [min_u, max_u] to a value 
  v in the range defined by [min_v, max_v].

  Args:
    See description.
  Return:
    Floating point value v 
  """
  assert type(u) is float
  assert type(min_u) is float
  assert type(max_u) is float
  assert type(min_v) is float
  assert type(max_v) is float

  return ((max_v - min_v) * (u - min_u)) / float(max_u - min_u) + min_v

def minNetDiff(a, b):
  """
  Returns an offset s that minimizes (zeros) the net difference between the 
  equal length lists a and b. Net difference is the sum of all pairwise 
  differences: a_elem - (b_elem + s).

  Let n = number of elements in a (and in b)
  E = -(n * s) + sum(a) - sum(b)
  
  Args:
    a: A list of values
    b: A list of values
  Return:
    A floating point offset
  """
  assert len(a) == len(b)
  assert len(a) != 0

  # Find the root
  s = (sum(a) - sum(b)) / float(len(a))
  return s

def topRange(l, s):
  """
  Given a list of values, determines a range in which the values in the top 
  s% must lie.

  Args:
    l: A list of values
    s: A percentage
  Return:
    A tuple (lowest value that could be in top s%, max value in l)
  """
  mx = max(l)
  mn = min(l)
  if s is 100:
    return (mn, mx)
  dx = (mx - mn) / 100.0      # Width of 1% in the range covered by l's vals
  min_thresh = mx - (s * dx)  
  return (min_thresh, mx)

def angularExtentsOverlap(a1, a2, b1, b2):
  """
  Determine if 2 angular intervals overlap.

  a1, a2: The start and end angles definining interval a
  b1, b2: The start and end angles definining interval b
  """
  if a1 < b1:
    return (a2 >= b1)
  else:
    return (a1 <= b2)

def findRenderer(fig):
  """
  Look up the matplotlib renderer instance given a figure instance.
  Source: https://stackoverflow.com/questions/22667224/matplotlib-get-text-bounding-box-independent-of-backend?lq=1
  """
  if hasattr(fig.canvas, "get_renderer"):
    renderer = fig.canvas.get_renderer()
  else:
    import io
    fig.canvas.print_pdf(io.BytesIO())
    renderer = fig._cachedRenderer
  return(renderer)
