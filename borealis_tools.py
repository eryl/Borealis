'''
Created on 11 aug 2010

@author: erik
'''
import bpy, mathutils

class BorealisSettings(bpy.types.PropertyGroup):
    """
    Properties specific for the nwn models, gets attached to all objects.
    """
    node_type = bpy.props.EnumProperty(items = [("dummy","dummy","dummy"),
                                        ("trimesh","trimesh","trimesh"),
                                        ("danglymesh","danglymesh","danglymesh"),
                                        ("skin","skin","skin"),
                                        ("emitter","emitter","emitter"),
                                        ("aabb","aabb","aabb"),
                                        ("light","light","light")],
                                       name = "Node Type",
                                       description = "The NWN Node type of this object")
    is_aurabase = bpy.props.BoolProperty(name = "Is Aurabase Object", 
                                   description="Toggles this as a aurabase object. There should only be one for every nwn model", 
                                   default=False)
    
    @classmethod
    def register(cls):
        
        #We create a dynamic class to use for node properties 
        classname = "BorealisNodeProps"
        attribute_dict = {"bl_idname": classname, "bl_label" : "BorealisNodeProps", "properties" : []}
        
        from . import borealis_mdl_definitions
        #we build the attribute dictionary by using the definitions from borealis_mdl_definitions
        for prop in borealis_mdl_definitions.GeometryNodeProperties.get_properties():
            # one case for each of the different property types
            if  prop.has_blender_eq:
                continue
            
            if isinstance(prop, borealis_mdl_definitions.StringProperty):
                attribute_dict[prop.name] = bpy.props.StringProperty(name = prop.name)
                attribute_dict["properties"].append(prop)
            elif isinstance(prop, borealis_mdl_definitions.VectorProperty):
                pass
            elif isinstance(prop, borealis_mdl_definitions.BooleanProperty):
                attribute_dict[prop.name] = bpy.props.BoolProperty(name = prop.name)
                attribute_dict["properties"].append(prop)
            elif isinstance(prop, borealis_mdl_definitions.EnumProperty):
                pass
            elif isinstance(prop, borealis_mdl_definitions.ColorProperty):
                attribute_dict[prop.name] = bpy.props.FloatVectorProperty(name = prop.name, subtype='COLOR')
                attribute_dict["properties"].append(prop)
            elif isinstance(prop, borealis_mdl_definitions.IntProperty):
                attribute_dict[prop.name] = bpy.props.IntProperty(name = prop.name)
                attribute_dict["properties"].append(prop)
            elif isinstance(prop, borealis_mdl_definitions.FloatProperty):
                attribute_dict[prop.name] = bpy.props.FloatProperty(name = prop.name)
                attribute_dict["properties"].append(prop)

            
        #we now create a dynamic class and register it so it will be usable by this class
        node_props_class = type(classname, (bpy.types.PropertyGroup,), attribute_dict)
        bpy.utils.register_class(node_props_class)
        
        cls.node_properties = bpy.props.PointerProperty(type=node_props_class)
        
        bpy.utils.register_class(BorealisBasicProperties)
        cls.basic_settings = bpy.props.PointerProperty(type=BorealisBasicProperties)
        
class BorealisBasicProperties(bpy.types.PropertyGroup):
    classification = bpy.props.EnumProperty(items = [("effects","Effects","Effects"),
                                                     ("character","Character","character"),
                                                     ("item","Item","Item"),
                                                     ("tile","Tile","tile")],
                                       name = "Classification",
                                       description = "The classification of the current model")
    supermodel = bpy.props.StringProperty(name = "Supermodel")
    animationscale = bpy.props.FloatProperty(name = "Animation Scale")
    

class OBJECT_PT_borealis_basic(bpy.types.Panel):
    bl_idname = "OBJECT_PT_borealis_basic"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "NWN Basic Settings"
    bl_context = "object"
    
    def draw(self,context):
        layout = self.layout
        obj = context.object
        
        row = layout.row()
        row.prop(obj.nwn_props, "is_aurabase")
        
        if obj.nwn_props.is_aurabase:
            row = layout.row()
            row.prop(obj.nwn_props.basic_settings, "classification")
            row = layout.row()
            row.prop(obj.nwn_props.basic_settings, "supermodel")
            row = layout.row()
            row.prop(obj.nwn_props.basic_settings, "animationscale")
    
   
    
class OBJECT_PT_borealis_animations(bpy.types.Panel):
    bl_idname = "OBJECT_PT_borealis_animations"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "NWN Animation Controls"
    bl_context = "object"
    
    @classmethod
    def poll(cls, context):
        return (context.object is not None)
    
    def draw(self,context):
        layout = self.layout
        obj = context.object
        
        

class OBJECT_PT_node_tools(bpy.types.Panel):
    bl_idname = "OBJECT_PT_node_tools"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "NWN Node tools"
    bl_context = "object"
    
    @classmethod
    def poll(cls, context):
        return (context.object is not None)
    
    def draw(self,context):
        layout = self.layout
        obj = context.object
        node_type = obj.nwn_props.node_type
        
        from . import borealis_mdl_definitions
        
        #Compare all possible settings for the specific node_type with the ones 
        #loaded into blender
        for prop in borealis_mdl_definitions.GeometryNodeProperties.get_node_properties(node_type):
            if prop in bpy.types.BorealisNodeProps.properties:
                row = layout.row()
                row.prop(obj.nwn_props.node_properties, prop.name)
            
            
    
class BorealisTools(bpy.types.Panel):
    bl_idname = "OBJECT_PT_nwn_tools"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "NWN Model tools"
    bl_context = "object"

    node_list = ["dummy","trimesh","danglymesh","skin","light","emitter"]
    node_triplets = [(type, type, type) for type in node_list]
    node_type  = bpy.props.EnumProperty(node_triplets, name="node_type")
    
    @classmethod
    def poll(cls, context):
        return (context.object is not None)
     
    def draw(self, context):
        layout = self.layout

        obj = context.object
        
        row = layout.row()
        row.label(text="Hello world!", icon='WORLD_DATA')
        
        row = layout.row()
        row.prop(obj.nwn_props, "node_type")

    
    @classmethod
    def register(cls):
        bpy.utils.register_class(BorealisSettings)
        bpy.utils.register_class(OBJECT_PT_borealis_basic)
        bpy.utils.register_class(OBJECT_PT_node_tools)
        bpy.types.Object.nwn_props = bpy.props.PointerProperty(type=BorealisSettings)
        



                                       

class OBJECT_OT_make_nwn_object(bpy.types.Operator):
    bl_idname = "nwn.make_nwn_object"
    bl_label = "Make this an nwn object"
    
    def execute(self, context):
        pass

