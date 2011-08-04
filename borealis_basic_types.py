'''
Created on 24 jul 2011

@author: erik
'''

class Property:
    nodes = []
    name = ""
    has_blender_eq = False
    value = None
    data_type = str
    value_written = False
    default_value = None
    
    TAB_SPACE = 2
    
    def __init__(self, name, nodes, has_blender_eq = False, default_value = ""):
        
        self.name = name
        self.nodes = nodes
        self.has_blender_eq = has_blender_eq
        self.default_value = default_value
    
    
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
    min_value = None
    max_value = None
    def __init__(self, name, nodes, has_blender_eq = False, 
                 default_value = 0, min_value = None, max_value = None):
        self.min_value = min_value
        self.max_value = max_value
        Property.__init__(self, name, nodes, has_blender_eq, default_value)

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
    def __init__(self, name, nodes, enums, has_blender_eq = False):
        self.enums = enums
        Property.__init__(self, name, nodes, has_blender_eq);


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
#    def __init__(self, name, nodes, has_blender_eq = False, 
#                 default_value = 0, min_value = 0, max_value = 1):
#        self.min_value = min_value
#        self.max_value = max_value
#        FloatVectorProperty.__init__(self, name, nodes, has_blender_eq, default_value)

class NodeProperties():
    node_types = None
    props_list = None
    props_dict = None
    
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
    
    
class GeometryNodeProperties(NodeProperties):
    props_list = [StringProperty("parent", nodes = ["dummy", "trimesh", "danglymesh", "skin", "emitter", "light"], has_blender_eq=True),
                       FloatVectorProperty("position", nodes = ["dummy", "trimesh", "danglymesh", "skin", "emitter", "light"], has_blender_eq=True),
                       FloatVectorProperty("orientation", nodes = ["dummy", "trimesh", "danglymesh", "skin", "emitter", "light"], has_blender_eq=True),
                
                    ### mesh ###
                    ColorProperty("ambient", nodes = ["trimesh", "danglymesh", "skin"]),
                    ColorProperty("diffuse", nodes = ["trimesh", "danglymesh", "skin"]),
                    ColorProperty("specular", nodes = ["trimesh", "danglymesh", "skin"]),
                    IntProperty("shininess", nodes = ["trimesh", "danglymesh", "skin"]),
                    BooleanProperty("shadow", nodes = ["trimesh", "danglymesh", "skin"]),
                    StringProperty("bitmap", nodes = ["trimesh", "danglymesh", "skin"], has_blender_eq=True),
                    FloatMatrixProperty("verts", nodes = ["trimesh", "danglymesh", "skin"], has_blender_eq=True),
                    FloatMatrixProperty("tverts", nodes = ["trimesh", "danglymesh", "skin"], has_blender_eq=True),
                    IntMatrixProperty("faces", nodes = ["trimesh", "danglymesh", "skin"], has_blender_eq=True),
                    FloatProperty("alpha", nodes = ["trimesh", "danglymesh", "skin"]),
                    FloatProperty("scale", nodes = ["trimesh", "danglymesh", "skin"]),
                    ColorProperty("selfillumcolor", nodes = ["trimesh", "danglymesh", "skin"]),
                    
                    ##not often used ##
                    BooleanProperty('rotatetexture', nodes = ["trimesh", "danglymesh", "skin"]),
                    BooleanProperty('tilefade', nodes = ["trimesh", "danglymesh", "skin"]),
                    BooleanProperty('transparencyhint', nodes = ["trimesh", "danglymesh", "skin"]),
                    BooleanProperty('beaming', nodes = ["trimesh", "danglymesh", "skin"]),
                    BooleanProperty('inheritcolor', nodes = ["trimesh", "danglymesh", "skin"]),
                    BooleanProperty('center', nodes = ["trimesh", "danglymesh", "skin"]),
                    #BooleanProperty('render', nodes = ["trimesh", "danglymesh", "skin"]),
                    ColorProperty('colors', nodes = ["trimesh", "danglymesh", "skin"]),
                    
                    ### danglymesh ###
                    FloatProperty("displacement", nodes = ["danglymesh"]),
                    IntProperty("period", nodes = ["danglymesh"]),
                    IntProperty("tightness", nodes = ["danglymesh"]),
                    IntMatrixProperty("constraints", nodes = ["danglymesh"], has_blender_eq=True),
                    
                    ### skin ###
                    MatrixProperty("weights", nodes = ["skin"], has_blender_eq=True),
                    
                    ### aabb ### 
                    MatrixProperty("aabb", nodes = ["aabb"], has_blender_eq=True),
                    
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
                    ColorProperty('color', nodes = ["light"], has_blender_eq=True),        #The color of the light source.
                    FloatProperty('multiplier', nodes = ["light"]), #Unknown
                    FloatProperty('radius', nodes = ["light"], has_blender_eq=True),        #Probably the range of the light.
                    BooleanProperty('ambientonly', nodes = ["light"]),        #This controls if the light is only an ambient lightsource or if it is directional as well.
                    BooleanProperty('isdynamic', nodes = ["light"]),       #Unknown.
                    BooleanProperty('affectdynamic', nodes = ["light"]),        #Unknown.
                    IntProperty('lightpriority', nodes = ["light"]),        #Unknown. I'm not sure what this does,' but a reasonable guess would be it controls when the lightsource casts a shadow. We know that in NWN only the strongest lightsource in an area casts shadows,' this may be the value that determines that. Or it could be a flag of some kind.
                    BooleanProperty('shadow', nodes = ["light"]),        #Probably determines if this light is capable of casting shadows.
                    BooleanProperty('lensflares', nodes = ["light"]),            #Possibly causes the light source to produce a lens flare effect,' sounds cool anyway.
                    FloatProperty('flareradius', nodes = ["light"]),
                    BooleanProperty('fadinglight', nodes = ["light"]),        #Unknown. Might activate some kind of distance fall off for the light. Or it could do just about anything.                   
                    ]


                
class AnimationNodeProperties(NodeProperties):
    
    props_list = [#general properties
                  StringProperty("parent", nodes = ["dummy", "trimesh", "danglymesh", "skin", "emitter", "light"], has_blender_eq=True),
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
