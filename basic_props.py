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
    TAB_SPACE = 2
    gui_group = None
    
    def __init__(self, name, nodes, blender_ignore = False, default_value = "", show_in_gui = True, gui_group = "default"):
        
        self.name = name
        self.nodes = nodes
        self.blender_ignore = blender_ignore
        self.default_value = default_value
        self.show_in_gui
        self.gui_group = gui_group
        
    def read_value(self, current_line, model_data):
        try:
            self.value = self.data_type(current_line[1])
            self.value_written = True
        except:
            print("foo")
    
    def output_values(self):
        yield " "*self.TAB_SPACE + "%s %s" % (self.name, str(self.value))
    
    def __str__(self):
        return "\n".join(line for line in self.output_values())
    
    def update_value(self, value):
        self.value = value
        self.value_written = True
    
class NumberProperty(Property):
    pass
#    min_value = None
#    max_value = None
#    def __init__(self, name, nodes, blender_ignore = False, 
#                 default_value = 0, min_value = None, max_value = None):
#        self.min_value = min_value
#        self.max_value = max_value
#        Property.__init__(self, name, nodes, blender_ignore, default_value)

#vector properties are properties that have many values on one row
class VectorProperty(Property):
    data_type = str
    
    def read_value(self, current_line, model_data):
        self.value = [self.data_type(val) for val in current_line[1:]]
        self.value_written = True
    
    def update_value(self, value):
        self.value = [self.data_type(val) for val in value]
        self.value_written = True
    
    def output_values(self):
        yield " "*self.TAB_SPACE+ "%s %s" % (self.name, " ".join([str(val) for val in self.value]))
    
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
                self.value.append([self.data_type(value) for value in line])
        else:
            lines = int(current_line[-1])
            while lines:
                line = model_data.pop(0)
                if not line: #skip empty lines
                    continue
                self.value.append([self.data_type(value) for value in line])
                
                lines -= 1
        
        self.value_written = True
    
    def update_value(self, value):
        """
        Updates the value of the matrix. value must be a matrix, a sequence of sequences
        """
        self.value = [[self.data_type(val) for val in row] for row in value]
        self.value_written = True
    
    def output_values(self):
        yield " "*self.TAB_SPACE + "%s %i" % (self.name, len(self.value))
        for row in self.value:
            yield " "*self.TAB_SPACE*2 + " ".join([str(val) for val in row])

class StringProperty(Property):
    data_type = str

class BooleanProperty(Property):
    data_type = bool
    
    def output_values(self):
        value = "0"
        if self.value:
            value = "1"
        yield " " * self.TAB_SPACE + "%s %s" % (self.name, value)

class EnumProperty(Property):
    enums = []
    def __init__(self, name, nodes, enums, *args, **kwargs):
        self.enums = enums
        Property.__init__(self, name, nodes, *args, **kwargs);


class IntProperty(NumberProperty):
    data_type = int
    
class IntVectorProperty(VectorProperty):
    data_type = int

class IntMatrixProperty(MatrixProperty):
    data_type = int

class FloatProperty(NumberProperty):
    data_type = float
    
    def output_values(self):
        # This tidies values, like the max export script seems to do
        yield " "*self.TAB_SPACE + "%s %.9g" % (self.name, self.value)
        
class FloatVectorProperty(VectorProperty, FloatProperty):
    data_type = float

    def output_values(self):
        yield " "*self.TAB_SPACE+ "%s %s" % (self.name, " ".join(["%.9g" % val for val in self.value]))
        
class FloatMatrixProperty(MatrixProperty, FloatProperty):
    data_type = float
    
    def output_values(self):
        yield " "*self.TAB_SPACE + "%s %i" % (self.name, len(self.value))
        for row in self.value:
            yield " "*self.TAB_SPACE*2 + " ".join(["%.9g" % val for val in row])
    
class ColorProperty(FloatVectorProperty):
    data_type = float
    min_value = 0
    max_value = 1

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
        """
        Updates the value of the matrix. value must be a matrix, a sequence of sequences
        """
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
    props_list = [StringProperty("parent", nodes = ["dummy", "trimesh", "danglymesh", "skin", "emitter", "light", "aabb", "reference"], blender_ignore=True),
                FloatVectorProperty("position", nodes = ["dummy", "trimesh", "danglymesh", "skin", "aabb", "emitter", "light", "reference"], blender_ignore=True),
                FloatVectorProperty("orientation", nodes = ["dummy", "trimesh", "danglymesh", "skin", "aabb", "emitter", "light", "reference"], blender_ignore=True),
                
                ### mesh ###
                ColorProperty("ambient", nodes = ["trimesh", "danglymesh", "skin", "aabb"]),
                ColorProperty("diffuse", nodes = ["trimesh", "danglymesh", "skin", "aabb"]),
                ColorProperty("specular", nodes = ["trimesh", "danglymesh", "skin", "aabb"]),
                IntProperty("shininess", nodes = ["trimesh", "danglymesh", "skin", "aabb"]),
                BooleanProperty("shadow", nodes = ["trimesh", "danglymesh", "skin", "aabb"], gui_group="Render Options"),
                StringProperty("bitmap", nodes = ["trimesh", "danglymesh", "skin", "aabb"], blender_ignore=True),
                FloatMatrixProperty("verts", nodes = ["trimesh", "danglymesh", "skin", "aabb"], blender_ignore=True),
                FloatMatrixProperty("tverts", nodes = ["trimesh", "danglymesh", "skin", "aabb"], blender_ignore=True),
                IntMatrixProperty("faces", nodes = ["trimesh", "danglymesh", "skin", "aabb"], blender_ignore=True),
                FloatProperty("alpha", nodes = ["trimesh", "danglymesh", "skin"]),
                FloatProperty("scale", nodes = ["trimesh", "danglymesh", "skin"]),
                ColorProperty("selfillumcolor", nodes = ["trimesh", "danglymesh", "skin"]),
                BooleanProperty('rotatetexture', nodes = ["trimesh", "danglymesh", "skin"], gui_group="Render Options"),
                BooleanProperty('tilefade', nodes = ["trimesh", "danglymesh", "skin"]),
                BooleanProperty('transparencyhint', nodes = ["trimesh", "danglymesh", "skin", "aabb"]),
                BooleanProperty('beaming', nodes = ["trimesh", "danglymesh", "skin"], gui_group="Render Options"),
                BooleanProperty('inheritcolor', nodes = ["trimesh", "danglymesh", "skin"]),
                BooleanProperty('center', nodes = ["trimesh", "danglymesh", "skin"]),
                ColorProperty("wireocolor", nodes = ["trimesh", "danglymesh", "skin", "aabb", "reference"]),
                BooleanProperty('render', nodes = ["trimesh", "danglymesh", "skin"], gui_group="Render Options"),
                ColorProperty('colors', nodes = ["trimesh", "danglymesh", "skin"]),
                
                ### danglymesh ###
                FloatProperty("displacement", nodes = ["danglymesh"]),
                IntProperty("period", nodes = ["danglymesh"]),
                IntProperty("tightness", nodes = ["danglymesh"]),
                IntMatrixProperty("constraints", nodes = ["danglymesh"], blender_ignore=True),
                
                ### skin ###
                MatrixProperty("weights", nodes = ["skin"], blender_ignore=True),
                
                ### aabb ### 
                AABBTree("aabb", nodes = ["aabb"], blender_ignore=True),
                
                ### Emitter properties ###
                ColorProperty('colorstart', nodes = ["emitter"]),
                ColorProperty('colorend', nodes = ["emitter"]),
                FloatProperty('alphastart', nodes = ["emitter"]), 
                FloatProperty('alphaend', nodes = ["emitter"]),
                FloatProperty('sizestart', nodes = ["emitter"]),
                FloatProperty('sizeend', nodes = ["emitter"]),
                FloatProperty('sizestart_y', nodes = ["emitter"]),
                FloatProperty('sizeend_y', nodes = ["emitter"]), 
                IntProperty('framestart', nodes = ["emitter"]), 
                IntProperty('frameend', nodes = ["emitter"]), 
                IntProperty('birthrate', nodes = ["emitter"]), 
                IntProperty('spawntype', nodes = ["emitter"]),
                FloatProperty('lifeexp', nodes = ["emitter"]),
                FloatProperty('mass', nodes = ["emitter"]), 
                FloatProperty('spread', nodes = ["emitter"]), 
                FloatProperty('particlerot', nodes = ["emitter"]), 
                FloatProperty('velocity', nodes = ["emitter"]), 
                FloatProperty('randvel', nodes = ["emitter"]), 
                IntProperty('fps', nodes = ["emitter"]),
                BooleanProperty('random', nodes = ["emitter"]),
                BooleanProperty('inherit', nodes = ["emitter"]),
                BooleanProperty('inherit_local', nodes = ["emitter"]),
                BooleanProperty('inherit_part', nodes = ["emitter"]),
                BooleanProperty('inheritvel', nodes = ["emitter"]),
                IntProperty('xsize', nodes = ["emitter"]),
                IntProperty('ysize', nodes = ["emitter"]),
                BooleanProperty('bounce', nodes = ["emitter"]),
                FloatProperty('bounce_co', nodes = ["emitter"]),
                BooleanProperty('loop', nodes = ["emitter"]),
                EnumProperty('update', nodes = ["emitter"], enums = ["Fountain"]), #Fountain - Unknown
                EnumProperty('render', nodes = ["emitter"], enums = ["Normal, Linked, Motion_blur"]), #[Normal | linked | Motion_blur]  - Unknown. Probably controls how the particles are drawn in some way.
                EnumProperty('blend', nodes = ["emitter"], enums = ["Normal", "Lighten"]),  # [Normal | lighten]  - Unknown.
                BooleanProperty('update_sel', nodes = ["emitter"]),
                BooleanProperty('render_sel', nodes = ["emitter"]),
                BooleanProperty('blend_sel', nodes = ["emitter"]),
                FloatProperty('deadspace', nodes = ["emitter"]),
                FloatProperty('opacity', nodes = ["emitter"]),
                FloatProperty('blurlength', nodes = ["emitter"]), 
                FloatProperty('lightningdelay', nodes = ["emitter"]), 
                FloatProperty('lightningradius', nodes = ["emitter"]), 
                FloatProperty('lightningscale', nodes = ["emitter"]),
                FloatProperty('blastradius', nodes = ["emitter"]),
                FloatProperty('blastlength', nodes = ["emitter"]),
                BooleanProperty('twosidedtex', nodes = ["emitter"]), 
                BooleanProperty('p2p', nodes = ["emitter"]), 
                BooleanProperty('p2p_sel', nodes = ["emitter"]), 
                EnumProperty('p2p_type', nodes = ["emitter"], enums = ["Bezier", "Gravity"]), #[Bezier|Gravity]
                FloatProperty('p2p_bezier2', nodes = ["emitter"]), 
                FloatProperty('p2p_bezier3', nodes = ["emitter"]),
                FloatProperty('combinetime', nodes = ["emitter"]), 
                FloatProperty('drag', nodes = ["emitter"]), 
                FloatProperty('grav', nodes = ["emitter"]), 
                FloatProperty('threshold', nodes = ["emitter"]),
                StringProperty('texture', nodes = ["emitter"]),
                IntProperty('xgrid', nodes = ["emitter"]), 
                IntProperty('ygrid', nodes = ["emitter"]), 
                EnumProperty('affectedbywind', nodes = ["emitter"], enums = ['true', 'false']), #[true|false]
                BooleanProperty('m_istinted', nodes = ["emitter"]), 
                IntProperty('renderorder', nodes = ["emitter"]), 
                BooleanProperty('splat', nodes = ["emitter"]), 
                
                
                ### Light properties ###
                ColorProperty('color', nodes = ["light"], blender_ignore=True),        #The color of the light source.
                FloatProperty('multiplier', nodes = ["light"]), #Unknown
                FloatProperty('radius', nodes = ["light"], blender_ignore=True),        #Probably the range of the light.
                BooleanProperty('ambientonly', nodes = ["light"]),        #This controls if the light is only an ambient lightsource or if it is directional as well.
                BooleanProperty('isdynamic', nodes = ["light"]),       #Unknown.
                BooleanProperty('affectdynamic', nodes = ["light"]),        #Unknown.
                IntProperty('lightpriority', nodes = ["light"]),        #Unknown. I'm not sure what this does,' but a reasonable guess would be it controls when the lightsource casts a shadow. We know that in NWN only the strongest lightsource in an area casts shadows,' this may be the value that determines that. Or it could be a flag of some kind.
                BooleanProperty('shadow', nodes = ["light"]),        #Probably determines if this light is capable of casting shadows.
                BooleanProperty('lensflares', nodes = ["light"]),            #Possibly causes the light source to produce a lens flare effect,' sounds cool anyway.
                FloatProperty('flareradius', nodes = ["light"]),
                BooleanProperty('fadinglight', nodes = ["light"]),        #Unknown. Might activate some kind of distance fall off for the light. Or it could do just about anything.                   
                
                ### Reference Properties ###
                StringProperty('refModel', nodes = ["reference"]),
                BooleanProperty('reattachable', nodes = ["reference"]),
                ]


                
class AnimationNodeProperties(NodeProperties):
    """
    Class containing all animation node properties
    """
    
    props_list = [#general properties
                  StringProperty("parent", nodes = ["dummy", "trimesh", "danglymesh", "skin", "emitter", "light"], blender_ignore=True),
                  FloatMatrixProperty("orientationkey", nodes = ["dummy", "trimesh", "danglymesh", "skin", "emitter", "light"]),
                  FloatMatrixProperty("positionkey", nodes = ["dummy", "trimesh", "danglymesh", "skin", "emitter", "light"]),
                  
                  #emitter properties
                  FloatMatrixProperty("alphaEndkey", nodes = ["emitter"]),
                  FloatMatrixProperty("alphaStartkey", nodes = ["emitter"]),
                  FloatMatrixProperty("alphakey", nodes = ["emitter"]),
                  FloatMatrixProperty("birthratekey", nodes = ["emitter"]),
                  FloatMatrixProperty("colorEndkey", nodes = ["emitter"]),
                  FloatMatrixProperty("colorStartkey", nodes = ["emitter"]),
                  FloatMatrixProperty("colorkey", nodes = ["emitter"]),
                  FloatMatrixProperty("fpskey", nodes = ["emitter"]),
                  FloatMatrixProperty("frameEndkey", nodes = ["emitter"]),
                  FloatMatrixProperty("frameStartkey", nodes = ["emitter"]),
                  FloatMatrixProperty("lifeExpkey", nodes = ["emitter"]),
                  FloatMatrixProperty("masskey", nodes = ["emitter"]),
                
                  FloatMatrixProperty("radiuskey", nodes = ["emitter"]),
                  FloatMatrixProperty("randvelkey", nodes = ["emitter"]),
                  FloatMatrixProperty("sizeEndkey", nodes = ["emitter"]),
                  FloatMatrixProperty("sizeStartkey", nodes = ["emitter"]),
                  FloatMatrixProperty("spreadkey", nodes = ["emitter"]),
                  FloatMatrixProperty("velocitykey", nodes = ["emitter"]),
                  FloatMatrixProperty("xsizekey", nodes = ["emitter"]),
                  FloatMatrixProperty("ysizekey", nodes = ["emitter"])
                ]
