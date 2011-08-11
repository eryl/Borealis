# -*- coding: utf-8 -*-
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>
'''
Contains basic properties for handling node properties.

This module contains a set of classes for interfacing between blenders custom 
properties and the properties used in Neverwinter Nights models. The basic
information about which nodes has which properties are contained herein.

:Classes:
`Property`: Base class for all properties.



@author: Erik Ylipää
'''

TAB_SPACE = 2

class Property:
    nodes = []
    name = ""
    blender_ignore = False
    value = None
    data_type = str
    value_written = False
    default_value = None
    show_in_gui = True
    gui_group = None
    
    def __init__(self, name="", nodes=[], description = "", gui_name = "", 
                 blender_ignore=False, default_value=None, show_in_gui=True, 
                 gui_group="Ungrouped"):
        
        self.name = name
        self.nodes = nodes
        self.description = description
        if gui_name:
            self.gui_name = gui_name
        else:
            self.gui_name = self.name
        self.blender_ignore = blender_ignore
        self.default_value = default_value
        self.show_in_gui
        self.gui_group = gui_group
        
    def get_default_value(self):
        return self.default_value
    
    def read_value(self, current_line, model_data):
        try:
            self.value = self.format_input(current_line[1])
            self.value_written = True
        except:
            print("foo")
    
    def output_values(self):
        yield " "*TAB_SPACE + "%s %s" % (self.name, str(self.value))
    
    def __str__(self):
        return "\n".join(line for line in self.output_values())
    
    def update_value(self, value):
        self.value = self.format_input(value)
        self.value_written = True
    
    def format_input(self, input):
        return self.data_type(input)
    
class NumberProperty(Property):
    min = None
    max = None
    
    def __init__(self, min = None, max = None, **kwargs):
        self.min = min
        self.max = max
        super().__init__(**kwargs)

#vector properties are properties that have many values on one row
class VectorProperty(Property):
    data_type = str
    size = None
    
    def __init__(self, size = 3, **kwargs):
        self.size = size
        super().__init__(**kwargs)
            
    def read_value(self, current_line, model_data):
        self.value = [self.format_input(val) for val in current_line[1:]]
        self.value_written = True
    
    def update_value(self, value):
        self.value = [self.format_input(val) for val in value]
        self.value_written = True
    
    def output_values(self):
        yield " "*TAB_SPACE+ "%s %s" % (self.name, " ".join([str(val) for val in self.value]))
    
#matrix properties are properties that have values on multiple rows
class MatrixProperty(Property):
    data_type = str
    def read_value(self, current_line, model_data):
        self.value = []
        #if the current line has less than two tokens, the list is terminated with an endlist 
        #token instead of a given number of rows
        if len(current_line) < 2:
            done_reading = False
            while not done_reading:
                line = model_data.pop(0)
                if not line: #skip empty lines
                    continue
                if line[0] == "endlist":
                    break
                self.value.append([self.format_input(value) for value in line])
        else:
            lines = int(current_line[-1])
            while lines:
                line = model_data.pop(0)
                if not line: #skip empty lines
                    continue
                self.value.append([self.format_input(value) for value in line])
                
                lines -= 1
        
        self.value_written = True
    
    def update_value(self, value):
        """
        Updates the value of the matrix. value must be a matrix, a sequence of sequences
        """
        self.value = [[self.format_input(val) for val in row] for row in value]
        self.value_written = True
    
    def output_values(self):
        yield " "*TAB_SPACE + "%s %i" % (self.name, len(self.value))
        for row in self.value:
            yield " "*TAB_SPACE*2 + " ".join([str(val) for val in row])

class StringProperty(Property):
    data_type = str

class BooleanProperty(Property):
    data_type = bool
    
    def format_input(self, input):
        #Ugly, but it makes sure float strings are first cast to int, then bool
        # It will convert values between (1,1) to False. I had an issue where
        # a bool value was written as 0.0 in the ascii file
        return bool(int(float(input)))
    
    def output_values(self):
        value = "0"
        if self.value:
            value = "1"
        yield " " * TAB_SPACE + "%s %s" % (self.name, value)

class EnumProperty(Property):
    """ A property that can only assume a fixed set of values.
    
        The values are supplied to the constructor as a list or a dictionary,
        but will always be stored as a dictionary. The keys are the names of 
        the enums, while the values are the output in the mdl file.
        The name is used as values in Blender, while the outputs are used as
        values in the ascii .mdl file.
    """
    enums = {}
    """ The dictionary which holds the enums in the form {name: output } """
    inverse_enums = {}
    """ An inverse dictionary of the enum in the form {output: name} """
    def __init__(self, enums = {}, **kwargs):
        """ The constructor takes the enums as a keyword argument. 
            It can be supplied as a list for compability with how it was
            handled before. A list will be converted to a dictionary with keys the
            same as values """
        self.enums = {}
        self.inverse_enums = {}
        
        if isinstance(enums, list):
            enums = dict(zip(enums, enums))
        
        #this simply makes sure the values are all strings
        for name, output in enums.items():
            name = str(name)
            output = str(output)
            self.enums[name] = output
            self.inverse_enums[output] = name
            
        super().__init__(**kwargs)

    def update_value(self, value):
        # Make sure the value is saved as the name, which is what blender expects
        value = str(value)
        if value in self.enums:
            self.value = value
        elif value in self.inverse_enums:
            self.value = self.inverse_enums[value]
        else:
            raise ValueError("Not a valid Enum: %s for %s" % (value, self.name))
        self.value_written = True

    def read_value(self, current_line, model_data):
        val = str(current_line[1])
        print("Enum %s reading value %s" % (self.name, val))
        if val in self.enums:
            self.value = val
        elif val in self.inverse_enums:
            self.value = self.inverse_enums[val]
        else:
            print(self.enums)
            print(self.inverse_enums)
            raise ValueError("Not a valid Enum: %s for %s" % (val, self.name))
        print("Enum %s value set to %s" % (self.name, self.value))
        
        self.value_written = True
        
    def output_values(self):
        if self.value in self.enums:
            val = self.enums[self.value]
        else:
            val = self.value
        yield " " * TAB_SPACE + "%s %s" % (self.name, val)
    
    def get_blender_items(self):
        return [(name, name, name) for name, output in self.enums.items()]

class IntProperty(NumberProperty):
    data_type = int
    
    def format_input(self, input):
        # Some export scripts export values that should be integers as floats
        # and the int constructor won't accept float strings as input,
        # therefore we first cast the string to a float, then an int
        return int(float(input))
    
class IntVectorProperty(IntProperty, VectorProperty):
    data_type = int

class IntMatrixProperty(IntProperty, MatrixProperty):
    data_type = int

class FloatProperty(NumberProperty):
    data_type = float
    
    def output_values(self):
        # This tidies values, like the max export script seems to do
        yield " "*TAB_SPACE + "%s %.9g" % (self.name, self.value)
        
class FloatVectorProperty(FloatProperty, VectorProperty):
    data_type = float

    def output_values(self):
        yield " "*TAB_SPACE+ "%s %s" % (self.name, " ".join(["%.9g" % val for val in self.value]))
        
class FloatMatrixProperty(MatrixProperty, FloatProperty):
    data_type = float
    
    def output_values(self):
        yield " "*TAB_SPACE + "%s %i" % (self.name, len(self.value))
        for row in self.value:
            yield " "*TAB_SPACE*2 + " ".join(["%.9g" % val for val in row])
    
class ColorProperty(FloatVectorProperty):
    data_type = float
        
class AABBTree(MatrixProperty):
    def read_value(self, current_line, model_data):
        def new_node(x1,y1,z1, x2, y2, z2, index, parent = None):
            tree_node = {"co1": [float(x1), float(y1), float(z1)], 
                         "co2": [float(x2), float(y2), float(z2)],
                         "left": None,
                         "right": None,
                         "index": int(index),
                         "parent": parent}
            return tree_node
        
        aabb, x1, y1, z1, x2, y2, z2, index = current_line
        root_node = new_node(x1, y1, z1, x2, y2, z2, index)
        node_stack = [root_node]
        self.value = root_node
        done = False
        
        while(not done):
            #Peek ahead to see if the next line is also a node in the tree
            if len(model_data[0]) == 7:
                current_line = model_data.pop(0)
                x1, y1, z1, x2, y2, z2, index = current_line
                parent = node_stack[-1]
                current_node = new_node(x1,y1,z1, x2, y2, z2,
                                         index, parent)
                if not parent["left"]:
                    parent["left"] = current_node
                else:
                    parent["right"] = current_node
                    node_stack.pop()
                    
                if current_node["index"] == -1:
                    node_stack.append(current_node)
            else:
                done = True
        self.value_written = True
    
    def update_value(self, value):
        self.value = value
        self.value_written = True
    
    def output_values(self):
        root_node = self.value
        x1, y1, z1 = root_node["co1"]
        x2, y2, z2 = root_node["co2"]
        index = root_node["index"]
        yield " "*TAB_SPACE + "aabb %.7f %.7f %.7f %.7f %.7f %.7f %d" % (x1, y1, z1, 
                                                         x2, y2, z2, index)
        level = 2
        node_stack = []
        node_stack.append((level, root_node["right"],))
        node_stack.append((level, root_node["left"],))

        while node_stack:
            level, current_node = node_stack.pop()
            x1, y1, z1 = current_node["co1"]
            x2, y2, z2 = current_node["co2"]
            index = current_node["index"]
            yield (" "*TAB_SPACE*level + 
                   "%.7f %.7f %.7f %.7f %.7f %.7f %d" % 
                   (x1, y1, z1, x2, y2, z2, index))
            
            left = current_node["left"]
            right = current_node["right"]
            if right:
                node_stack.append((level+1, current_node["right"],))
            if left:
                node_stack.append((level+1, current_node["left"],))
            
    
class NodeProperties():
    node_types = None
    props_list = None
    props_dict = None
    gui_groups = None
    node_gui_groups = None
    
    @classmethod
    def build_dictionary(cls):
        cls.props_dict = {}
        if cls.props_list:
            for prop in cls.props_list:
                for node in prop.nodes:
                    if node in cls.props_dict:
                        cls.props_dict[node].append(prop)
                    else:
                        cls.props_dict[node] = [prop]
    
    @classmethod
    def get_node_properties(cls, node_type):
        if not cls.props_dict:
            cls.build_dictionary()
        return cls.props_dict[node_type]
    
    @classmethod
    def get_properties(cls):
        return cls.props_list
    
    @classmethod
    def get_node_types(cls):
        if not cls.node_types:
            cls.build_types()
        return cls.node_types
    
    @classmethod
    def build_types(cls):
        if not cls.props_dict:
            cls.build_dictionary()
        cls.node_types = cls.props_dict.keys()
    
    @classmethod
    def get_gui_groups(cls):
        if not cls.gui_groups:
            cls.gui_groups = {"default": []}
            for prop in cls.props_list:
                if prop.gui_group:
                    if prop.gui_group not in cls.gui_groups:
                        cls.gui_groups[prop.gui_group] = []
                    cls.gui_groups[prop.gui_group].append(prop)
                else:
                    cls.gui_groups["default"].append(prop)
        return cls.gui_groups
    
    @classmethod
    def get_node_gui_groups(cls, node_type):
        if not cls.node_gui_groups:
            cls.node_gui_groups = {}
            for node_type_ in cls.get_node_types():
                group_dict = {}
                for prop in cls.get_node_properties(node_type_):
                    if prop.gui_group not in group_dict:
                        group_dict[prop.gui_group] = []
                    group_dict[prop.gui_group].append(prop)
                cls.node_gui_groups[node_type_] = group_dict
        return cls.node_gui_groups[node_type]
            
    
class GeometryNodeProperties(NodeProperties):
    """ Class for collecting all geometry-node properties
    """
    props_list = [StringProperty(name="parent", nodes = ["dummy", "trimesh", "danglymesh", "skin", "emitter", "light", "aabb", "reference"], blender_ignore=True),
                FloatVectorProperty(name="position", nodes = ["dummy", "trimesh", "danglymesh", "skin", "aabb", "emitter", "light", "reference"], blender_ignore=True),
                FloatVectorProperty(name="orientation", nodes = ["dummy", "trimesh", "danglymesh", "skin", "aabb", "emitter", "light", "reference"], blender_ignore=True),
                
                ### mesh ###
                ColorProperty(name="ambient", nodes = ["trimesh", "danglymesh", "skin", "aabb"]),
                ColorProperty(name="diffuse", nodes = ["trimesh", "danglymesh", "skin", "aabb"]),
                ColorProperty(name="specular", nodes = ["trimesh", "danglymesh", "skin", "aabb"]),
                IntProperty(name="shininess", nodes = ["trimesh", "danglymesh", "skin", "aabb"]),
                BooleanProperty(name="shadow", nodes = ["trimesh", "danglymesh", "skin", "aabb"], gui_group="Render Options"),
                StringProperty(name="bitmap", nodes = ["trimesh", "danglymesh", "skin", "aabb"], blender_ignore=True),
                FloatMatrixProperty(name="verts", nodes = ["trimesh", "danglymesh", "skin", "aabb"], blender_ignore=True),
                FloatMatrixProperty(name="tverts", nodes = ["trimesh", "danglymesh", "skin", "aabb"], blender_ignore=True),
                IntMatrixProperty(name="faces", nodes = ["trimesh", "danglymesh", "skin", "aabb"], blender_ignore=True),
                FloatProperty(name="alpha", nodes = ["trimesh", "danglymesh", "skin"]),
                FloatProperty(name="scale", nodes = ["trimesh", "danglymesh", "skin"]),
                ColorProperty(name="selfillumcolor", nodes = ["trimesh", "danglymesh", "skin"], gui_name="Self illumination color"),
                BooleanProperty(name='rotatetexture', nodes = ["trimesh", "danglymesh", "skin"], gui_group="Render Options"),
                EnumProperty(name='tilefade', nodes = ["trimesh", "danglymesh", "skin"], enums = {"Don't fade": 0, "Fade": 1, "Neighbour": 2, "Base": 4}),
                BooleanProperty(name='transparencyhint', nodes = ["trimesh", "danglymesh", "skin", "aabb"]),
                BooleanProperty(name='beaming', nodes = ["trimesh", "danglymesh", "skin"], gui_group="Render Options"),
                BooleanProperty(name='inheritcolor', nodes = ["trimesh", "danglymesh", "skin"]),
                BooleanProperty(name='center', nodes = ["trimesh", "danglymesh", "skin"]),
                ColorProperty(name="wireocolor", nodes = ["trimesh", "danglymesh", "skin", "aabb", "reference"]),
                BooleanProperty(name='render', nodes = ["trimesh", "danglymesh", "skin"], gui_group="Render Options"),
                FloatMatrixProperty(name='colors', nodes = ["trimesh", "danglymesh", "skin"], blender_ignore = True),
                
                ### danglymesh ###
                FloatProperty(name="displacement", nodes = ["danglymesh"]),
                IntProperty(name="period", nodes = ["danglymesh"]),
                IntProperty(name="tightness", nodes = ["danglymesh"]),
                IntMatrixProperty(name="constraints", nodes = ["danglymesh"], blender_ignore=True),
                
                ### skin ###
                MatrixProperty(name="weights", nodes = ["skin"], blender_ignore=True),
                
                ### aabb ### 
                AABBTree("aabb", nodes = ["aabb"], blender_ignore=True),
                
                ### Emitter properties ###
                ColorProperty(name='colorstart', nodes = ["emitter"]),
                ColorProperty(name='colorend', nodes = ["emitter"]),
                FloatProperty(name='alphastart', nodes = ["emitter"]), 
                FloatProperty(name='alphaend', nodes = ["emitter"]),
                FloatProperty(name='sizestart', nodes = ["emitter"]),
                FloatProperty(name='sizeend', nodes = ["emitter"]),
                FloatProperty(name='sizestart_y', nodes = ["emitter"]),
                FloatProperty(name='sizeend_y', nodes = ["emitter"]), 
                IntProperty(name='framestart', nodes = ["emitter"]), 
                IntProperty(name='frameend', nodes = ["emitter"]), 
                IntProperty(name='birthrate', nodes = ["emitter"]), 
                IntProperty(name='spawntype', nodes = ["emitter"]),
                FloatProperty(name='lifeexp', nodes = ["emitter"]),
                FloatProperty(name='mass', nodes = ["emitter"]), 
                FloatProperty(name='spread', nodes = ["emitter"]), 
                FloatProperty(name='particlerot', nodes = ["emitter"]), 
                FloatProperty(name='velocity', nodes = ["emitter"]), 
                FloatProperty(name='randvel', nodes = ["emitter"]), 
                IntProperty(name='fps', nodes = ["emitter"]),
                BooleanProperty(name='random', nodes = ["emitter"]),
                BooleanProperty(name='inherit', nodes = ["emitter"]),
                BooleanProperty(name='inherit_local', nodes = ["emitter"]),
                BooleanProperty(name='inherit_part', nodes = ["emitter"]),
                BooleanProperty(name='inheritvel', nodes = ["emitter"]),
                IntProperty(name='xsize', nodes = ["emitter"]),
                IntProperty(name='ysize', nodes = ["emitter"]),
                BooleanProperty(name='bounce', nodes = ["emitter"]),
                FloatProperty(name='bounce_co', nodes = ["emitter"]),
                BooleanProperty(name='loop', nodes = ["emitter"]),
                EnumProperty(name='update', nodes = ["emitter"], enums = ["Fountain", "Single"]),
                EnumProperty(name='render', nodes = ["emitter"], enums = ["Normal", "Linked", "Motion_blur"]), #[Normal | linked | Motion_blur]  - Unknown. Probably controls how the particles are drawn in some way.
                EnumProperty(name='blend', nodes = ["emitter"], enums = ["Normal", "Lighten"]),  # [Normal | lighten]  - Unknown.
                BooleanProperty(name='update_sel', nodes = ["emitter"]),
                BooleanProperty(name='render_sel', nodes = ["emitter"]),
                BooleanProperty(name='blend_sel', nodes = ["emitter"]),
                FloatProperty(name='deadspace', nodes = ["emitter"]),
                FloatProperty(name='opacity', nodes = ["emitter"]),
                FloatProperty(name='blurlength', nodes = ["emitter"]), 
                FloatProperty(name='lightningdelay', nodes = ["emitter"]), 
                FloatProperty(name='lightningradius', nodes = ["emitter"]), 
                FloatProperty(name='lightningscale', nodes = ["emitter"]),
                FloatProperty(name='blastradius', nodes = ["emitter"]),
                FloatProperty(name='blastlength', nodes = ["emitter"]),
                BooleanProperty(name='twosidedtex', nodes = ["emitter"]), 
                BooleanProperty(name='p2p', nodes = ["emitter"]), 
                BooleanProperty(name='p2p_sel', nodes = ["emitter"]), 
                EnumProperty(name='p2p_type', nodes = ["emitter"], enums = ["Bezier", "Gravity"]), #[Bezier|Gravity]
                FloatProperty(name='p2p_bezier2', nodes = ["emitter"]), 
                FloatProperty(name='p2p_bezier3', nodes = ["emitter"]),
                FloatProperty(name='combinetime', nodes = ["emitter"]), 
                FloatProperty(name='drag', nodes = ["emitter"]), 
                FloatProperty(name='grav', nodes = ["emitter"]), 
                FloatProperty(name='threshold', nodes = ["emitter"]),
                StringProperty(name='texture', nodes = ["emitter"]),
                IntProperty(name='xgrid', nodes = ["emitter"]), 
                IntProperty(name='ygrid', nodes = ["emitter"]), 
                EnumProperty(name='affectedbywind', nodes = ["emitter"], enums = ['true', 'false']), #[true|false]
                BooleanProperty(name='m_istinted', nodes = ["emitter"]), 
                IntProperty(name='renderorder', nodes = ["emitter"]), 
                BooleanProperty(name='splat', nodes = ["emitter"]), 
                
                
                ### Light properties ###
                BooleanProperty(name='ambientonly', nodes = ["light"]),        #This controls if the light is only an ambient lightsource or if it is directional as well.
                BooleanProperty(name='shadow', nodes = ["light"]),        #Probably determines if this light is capable of casting shadows.
                BooleanProperty(name='isdynamic', nodes = ["light"]),       #Unknown.
                BooleanProperty(name='affectdynamic', nodes = ["light"]),        #Unknown.
                IntProperty(name='lightpriority', nodes = ["light"], min=1, max=5),
                BooleanProperty(name='fadinglight', nodes = ["light"]),        #Unknown. Might activate some kind of distance fall off for the light. Or it could do just about anything.                   
                BooleanProperty(name='lensflares', nodes = ["light"]),            #Possibly causes the light source to produce a lens flare effect,' sounds cool anyway.
                FloatProperty(name='flareradius', nodes = ["light"]),
                ColorProperty(name='color', nodes = ["light"], blender_ignore=True),        #The color of the light source.
                FloatProperty(name='multiplier', nodes = ["light"]), #Unknown
                FloatProperty(name='radius', nodes = ["light"], blender_ignore=True),        #Probably the range of the light.
                 
                ### Reference Properties ###
                StringProperty(name='refModel', nodes = ["reference"]),
                BooleanProperty(name='reattachable', nodes = ["reference"]),
                ]

                
class AnimationNodeProperties(NodeProperties):
    """
    Class containing all animation node properties
    """
    
    props_list = [#general properties
                  StringProperty(name="parent", nodes = ["dummy", "trimesh", "danglymesh", "skin", "emitter", "light"], blender_ignore=True),
                  FloatMatrixProperty(name="orientationkey", nodes = ["dummy", "trimesh", "danglymesh", "skin", "emitter", "light"]),
                  FloatMatrixProperty(name="positionkey", nodes = ["dummy", "trimesh", "danglymesh", "skin", "emitter", "light"]),
                  
                  #emitter properties
                  FloatMatrixProperty(name="alphaEndkey", nodes = ["emitter"]),
                  FloatMatrixProperty(name="alphaStartkey", nodes = ["emitter"]),
                  FloatMatrixProperty(name="alphakey", nodes = ["emitter"]),
                  FloatMatrixProperty(name="birthratekey", nodes = ["emitter"]),
                  FloatMatrixProperty(name="colorEndkey", nodes = ["emitter"]),
                  FloatMatrixProperty(name="colorStartkey", nodes = ["emitter"]),
                  FloatMatrixProperty(name="colorkey", nodes = ["emitter"]),
                  FloatMatrixProperty(name="fpskey", nodes = ["emitter"]),
                  FloatMatrixProperty(name="frameEndkey", nodes = ["emitter"]),
                  FloatMatrixProperty(name="frameStartkey", nodes = ["emitter"]),
                  FloatMatrixProperty(name="lifeExpkey", nodes = ["emitter"]),
                  FloatMatrixProperty(name="masskey", nodes = ["emitter"]),
                
                  FloatMatrixProperty(name="radiuskey", nodes = ["emitter"]),
                  FloatMatrixProperty(name="randvelkey", nodes = ["emitter"]),
                  FloatMatrixProperty(name="sizeEndkey", nodes = ["emitter"]),
                  FloatMatrixProperty(name="sizeStartkey", nodes = ["emitter"]),
                  FloatMatrixProperty(name="spreadkey", nodes = ["emitter"]),
                  FloatMatrixProperty(name="velocitykey", nodes = ["emitter"]),
                  FloatMatrixProperty(name="xsizekey", nodes = ["emitter"]),
                  FloatMatrixProperty(name="ysizekey", nodes = ["emitter"])
                ]
    
walkmesh_materials =     [{"name": "Dirt", "color": (0.3,0.3,0.2)},
                           {"name": "Obscuring", "color": (1,1,1)},
                           {"name": "Grass", "color": (0, 0.5, 0)},
                           {"name": "Stone", "color": (0.2, 0.2, 0.2)},
                           {"name": "Wood", "color": (0.04,0.01, 0.01)},
                           {"name": "Water", "color": (0, 0, 0.7)}, 
                           {"name": "Nonwalk", "color": (0.7, 0, 1)},
                           {"name": "Transparent", "color": (0, 1, 1)},
                           {"name": "Carpet", "color": (0.2, 0.05, 0.1)},
                           {"name": "Metal", "color": (0.02,0.02,0.02)},
                           {"name": "Puddles", "color": (0, 0.5, 0.5)}, 
                           {"name": "Swamp", "color": (0, 0.25, 0)},
                           {"name": "Mud", "color": (0.36, 0.2, 0.1)},
                           {"name": "Leaves", "color": (0, 0.75, 0)},
                           {"name": "Lava", "color": (0.75, 0, 0)},
                           {"name": "BottomlessPit", "color": (0.015, 0.005, 0.03)}, 
                           {"name": "DeepWater", "color": (0, 0.005, 0.08)},
                           {"name": "Door", "color": (0.14, 0.05, 0.02)}, 
                           {"name": "Snow", "color": (0.5,0.5,1)}, 
                           {"name": "Sand", "color": (0.4, 0.3, 0.1)}
                 ]