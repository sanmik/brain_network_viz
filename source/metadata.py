# Library Imports
from itertools import islice 
import csv

# Local Module Imports
import config

class Metadata(object):
  """
  Base class for maintaining metadata (properties and their attributes) about
  Node and Edge objects. This base class handles parsing and storing the CSV
  data, and providing accessor methods. The NodeMetadata and EdgeMetadata add
  some specific methods.

  The top rows of an input CSV file define metadata and should look like the 
  following example. 

  +-------------+-----------+-----------+-----------+             
  | Primary Key | Property1 | Property2 | Property3 | ...             
  +-------------------------------------------------+ <-+         
  | Attribute1  |           |           |           |   |         
  +-------------------------------------------------+   |         
  | Attribute2  |           |           |           |   | Metadata
  +-------------------------------------------------+   |         
  | Attribute3  |           |           |           |   |         
  +-------------------------------------------------+ <-+         
  | Item1       |           |           |           |   |         
  +-------------------------------------------------+   |         
  | Item2       |           |           |           |   | Data    
  +-------------------------------------------------+   |         
  | Item3       |           |           |           |   |         
  +-------------+-----------+-----------+-----------+ <-+         

  Class usage example:
    m = NodeMetadata('sample_nodes.csv', 3, 'Id')
    m.get('X', 'MIN_VAL')
  """

  def __init__(self, in_file, num_rows, prime_key):
    """
    Construct a Metadata object

    Args:
      in_file: A file handle for an input csv file 
      num_rows: The number of rows of the csv file defining metadata
      prime_key: The name of the column of primary keys. EG: Attribute names or
                 Item (Node, Edge) IDs.
    """
    # 'data' will contain the property name row + all metadata rows as lists
    self.data = []
    # Lookup table mapping property names to column indices
    self.prop_indices = {}
    # Lookup table mapping attribute names to row indices
    self.attr_indices = {}

    # Detect and use correct delimiter. Commas and Tabs are supported.
    dialect = csv.Sniffer().sniff(in_file.read(1024), delimiters=",\t")
    in_file.seek(0)
    reader = csv.reader(in_file, dialect)
    # Populate data structs
    while reader.line_num < num_rows + 1:
      row = next(reader)
      if reader.line_num == 1:
        for i, name in enumerate(row):
          self.prop_indices[name] = i
      self.attr_indices[row[0]] = reader.line_num - 1
      self.data.append(row)

  def get(self, prop, attr):
    """
    Gets the value of a specific property attribute.

    Treats the CSV matrix shown up top as a 2D array, using prop to lookup 
    the column, and attr to lookup the row.

    EG: To get the minimum value of a node's x coordinate.
      m = Metadata('sample_nodes.csv', 3, 'Name')
      m.get('X', 'MIN_VAL')
    
    Args:
      prop: The metadata property
      attr: The attribute of that given property

    Return:
      The string value of the specified metadata property attribute
    """
    # Get indices into 2D data array
    j = self.getPropIdx(prop)
    i = self.getAttrIdx(attr)
    # Get value
    return self.data[i][j]

  def getPropIdx(self, prop):
    """
    Gets the index of a metadata property (Column index).

    Args:
      prop: The name of the metadata property 
    Return:
      Integer column index
    """
    return self.prop_indices[prop]

  def getAttrIdx(self, attr):
    """
    Gets the index of a metadata attribute (Row index).

    Args:
      attr: The name of the metadata attribute 
    Return:
      Integer row index
    """
    return self.attr_indices[attr]

class NodeMetadata(Metadata):
  """
  Subclass to implement Node specific Metadata functionality
  """
  def __init__(self, in_file, num_rows, prime_key):
    super(NodeMetadata, self).__init__(in_file, num_rows, prime_key)

    """
    A list of dicts for looking up Property names by layer: 
      self.layers[0] => 
        {
          'C': (Property Name, CSV column index, min val, max val),
          'D': (Property Name, CSV column index, min val, max val),
          ...
        }.     
    And to get the property name used for color in layer 2 you would access as:
      self.layers[0]['C'][0]

    In the value tuples, Property Name and CSV column index will be None if
    no such property is specified in the input file.
    """
    self.layers = [{k: None for k in config.NODE_USE_AS_KEYS}]

    # Populate self.layers
    row_i = self.attr_indices['USE_AS']
    for col_i in range(config.NODE_LAYER_COLS_BEGIN, len(self.data[0])):
      prop_use_as = self.data[row_i][col_i]
      assert prop_use_as in config.NODE_USE_AS_KEYS

      # Find or create the destination layer object and property
      dest_layer = None
      for layer in self.layers:
        if not layer[prop_use_as]:
          dest_layer = layer
          break
      if not dest_layer:
        dest_layer = {k: None for k in config.NODE_USE_AS_KEYS}
        self.layers.append(dest_layer)
      
      #min_val   = self.data[self.getAttrIdx('MIN_VAL')][col_i]
      min_val   = self.data[self.getAttrIdx('MIN_VAL')][col_i]
      max_val   = self.data[self.getAttrIdx('MAX_VAL')][col_i]
      prop_name = self.data[self.getAttrIdx(prime_key)][col_i]
      dest_layer[prop_use_as] = (prop_name, col_i, min_val, max_val)

    """ Fill in any gaps in self.layers. If a layer didn't have property 
    metadata explicitly set - it takes on default metadata values """
    for layer_i, layer in enumerate(self.layers):
      for use_as_key, v in layer.items():
        if not v:
          layer[use_as_key] = config.NODE_DEFAULT_META[use_as_key] 

  def getPropertyName(self, use_as, layer_i):
    """
    Get the Property name associated with the given USE_AS string for the given
    layer.

    Args:
      use_as: A USE_AS value. EG: C, D, etc.
      layer_i: The layer index
    Return:
      The string name of the associated property. None if that property wasn't
      set in the input file.
    """
    return self.layers[layer_i][use_as][0]

  def getPropertyIdx(self, use_as, layer_i):
    """
    Get the CSV column of the Property associated with the given USE_AS value
    for every node's layer i.

    Return
      Numeric index of the CSV colum. None that property was not set in the
      input file.  
    """
    return self.layers[layer_i][use_as][1]

  def getPropertyMinVal(self, use_as, layer_i):
    """
    Get the minimum value of the Property associated with the given USE_AS 
    value for every node's layer i.

    Return:
      String minimum value for the property.     
    """
    return self.layers[layer_i][use_as][2]

  def getPropertyMaxVal(self, use_as, layer_i):
    """
    Get the maximum value of the Property associated with the given USE_AS 
    value for every node's layer i.

    Return
      String maximum value for the property.
    """
    return self.layers[layer_i][use_as][3]

  def numLabeledLayers(self):
    """
    Return the number of node layers that a label property explicitly set. 
    """
    return len(filter(lambda l: l['L'][0] != None, self.layers))
    # TODO: Write Unit Test

class EdgeMetadata(Metadata):
  """
  Subclass to implement Node specific Metadata functionality

  TODO: Consider constructing a lookup table in the same way NodeMetadata does.
  """

  def getPropertyName(self, use_as):
    """
    Get the Property name associated with the given USE_AS string.

    Args:
      use_as: A USE_AS value. EG: C, D, etc.
    Return:
      The string name of the associated property
    """
    row_i = self.getAttrIdx('USE_AS')
    use_as_row = self.data[row_i]
    col_i = 0
    for val in use_as_row:
      if val == use_as:
        return self.data[0][col_i]
      col_i += 1
