'''
Created on 2 aug 2011

@author: erik
'''
import bpy

class BorealisSettings(bpy.types.PropertyGroup):
    """
    Properties specific for the nwn models, gets attached to all objects.
    """
    nwn_node_type = bpy.props.EnumProperty(items = [("dummy","dummy","dummy")],
                                       name = "Node Type",
                                       description = "The NWN Node type of this object")
    
    is_nwn_object = bpy.props.BoolProperty(name = "Is Neverwinter Nights Object", 
                                   description="Toggles whether this object is an nwn object and should be included in exports", 
                                   default=False)
    
    danglymesh_vertexgroup = bpy.props.StringProperty(name = "Dangle Mesh vertex group")
    skin_vg_index = bpy.props.IntProperty(name="Index of selected skin vertex group")
    
    @classmethod
    def register(cls):
        
        #We create a dynamic class to use for node properties 
        classname = "BorealisNodeProps"
        attribute_dict = {"bl_idname": classname, 
                          "bl_label" : "Neverwinter Nights Node properties", 
                          "properties" : []}
        
        from . import borealis_mdl_definitions
        
        #we build the attribute dictionary by using the definitions from borealis_mdl_definitions
        for prop in borealis_mdl_definitions.GeometryNodeProperties.get_properties():
            # one case for each of the different property types
            if  prop.has_blender_eq:
                continue
            
            ##The order of the cases are important since some properties are subtypes of other
            if isinstance(prop, borealis_mdl_definitions.ColorProperty):
                attribute_dict[prop.name] = bpy.props.FloatVectorProperty(name = prop.name, size = 3, 
                                                                          subtype='COLOR', min = 0, max = 1)
                attribute_dict["properties"].append(prop)
            
            elif isinstance(prop, borealis_mdl_definitions.StringProperty):
                attribute_dict[prop.name] = bpy.props.StringProperty(name = prop.name)
                attribute_dict["properties"].append(prop)
            
            elif isinstance(prop, borealis_mdl_definitions.FloatVectorProperty):
                attribute_dict[prop.name] = bpy.props.FloatVectorProperty(name = prop.name, size = 3)
                attribute_dict["properties"].append(prop)
            
            elif isinstance(prop, borealis_mdl_definitions.BooleanProperty):
                attribute_dict[prop.name] = bpy.props.BoolProperty(name = prop.name)
                attribute_dict["properties"].append(prop)
                
            elif isinstance(prop, borealis_mdl_definitions.EnumProperty):
                items = [(name, name, name) for name in prop.enums]
                attribute_dict[prop.name] = bpy.props.EnumProperty(name = prop.name, 
                                                                   items = items)
                attribute_dict["properties"].append(prop)
            
            elif isinstance(prop, borealis_mdl_definitions.IntProperty):
                attribute_dict[prop.name] = bpy.props.IntProperty(name = prop.name)
                attribute_dict["properties"].append(prop)
            elif isinstance(prop, borealis_mdl_definitions.FloatProperty):
                attribute_dict[prop.name] = bpy.props.FloatProperty(name = prop.name)
                attribute_dict["properties"].append(prop)

            if prop.name not in attribute_dict:
                print("Failed to add property %s of type %s" % (prop.name, prop.__class__))
                      
        #we now create a dynamic class and register it so it will be usable by this class
        node_props_class = type(classname, (bpy.types.PropertyGroup,), attribute_dict)
        bpy.utils.register_class(node_props_class)
        
        cls.node_properties = bpy.props.PointerProperty(type=node_props_class)
    

class AnimationEvent(bpy.types.PropertyGroup):
    def update_name(self, foo):
        self.name = "%s %.4g" % (self.type, self.time,)
    name = bpy.props.StringProperty(name = "Name")
    events = ["cast","hit","blur_start","blur_end",
              "snd_footstep","snd_hitground","draw_arrow","draw_weapon"]
    type = bpy.props.EnumProperty("Event Type", items = [('cast','cast','cast'),
                                                        ('hit','hit','hit'),
                                                        ('blur_start','blur_start','blur_start'),
                                                        ('blur_end','blur_end','blur_end'),
                                                        ('snd_footstep','snd_footstep','snd_footstep'), 
                                                        ('snd_hitground','snd_hitground','snd_hitground'), 
                                                        ('draw_arrow','draw_arrow','draw_arrow'),
                                                        ('draw_weapon','draw_weapon','draw_weapon')],
                                  default="hit", update = update_name)
    time = bpy.props.FloatProperty("Time at which event occurs (in seconds)", default = 0.5, min = 0, step = 0.1, precision=2, update=update_name)
    
        
class Animation(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name = "Name")
    start_marker_name = bpy.props.StringProperty(name = "Start Marker")
    end_marker_name = bpy.props.StringProperty(name = "End Marker")
    transtime = bpy.props.FloatProperty(name = "Transition time", default = 1)
    events = bpy.props.CollectionProperty(type = AnimationEvent)
    event_index = bpy.props.IntProperty(name = "Current event")
    ### Since the animations are tightly coupled to the markers
    ### dynamic properties are used for it's attributes
    
    def get_start_frame(self):
        return self.get_start_marker().frame
    
    def set_start_frame(self, value):
        self.get_start_marker().frame = value
    
    def get_start_marker(self):
        return bpy.context.scene.timeline_markers[self.start_marker_name]
        
    def set_start_marker(self, value):
        self.start_marker_name = value.name
    
    def get_end_frame(self):
        return self.get_end_marker().frame
    
    def set_end_frame(self, value):
        self.get_end_marker().frame = value
    
    def get_end_marker(self):
        return bpy.context.scene.timeline_markers[self.end_marker_name]
        
    def set_end_marker(self, value):
        self.end_marker_name = value.name
    
    end_marker = property(get_end_marker, set_end_marker)
    start_marker = property(get_start_marker, set_start_marker)
    end_frame = property(get_end_frame, set_end_frame)
    start_frame = property(get_start_frame, set_start_frame)
    
    
class AnimationProperties(bpy.types.PropertyGroup):
    animations = bpy.props.CollectionProperty(type=Animation)
    animation_index = bpy.props.IntProperty(name = "Index of currently selected animation")
     

class BorealisBasicProperties(bpy.types.PropertyGroup):
    classification = bpy.props.EnumProperty(items = [("effects","Effects","Effects"),
                                                     ("character","Character","character"),
                                                     ("item","Item","Item"),
                                                     ("tile","Tile","tile")],
                                            default = "character",
                                            name = "Classification",
                                            description = "The classification of the current model")
    supermodel = bpy.props.StringProperty(name = "Supermodel")
    animationscale = bpy.props.FloatProperty(name = "Animation Scale")
    root_object_name = bpy.props.StringProperty(name = "Root object name")
        
    @classmethod
    def register(cls):
        cls.animation_props = bpy.props.PointerProperty(type = AnimationProperties)