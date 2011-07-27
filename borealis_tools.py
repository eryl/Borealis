'''
Created on 11 aug 2010

@author: erik
'''
import bpy, mathutils


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
                attribute_dict[prop.name] = bpy.props.FloatVectorProperty(name = prop.name, 
                                                                          subtype='COLOR')
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

        
class Animation(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name = "Name")
    start_frame = bpy.props.IntProperty(name = "Start Frame")
    end_frame = bpy.props.IntProperty(name = "End Frame")
    start_marker_name = bpy.props.StringProperty(name = "Start Marker")
    end_marker_name = bpy.props.StringProperty(name = "Start Marker")
    def get_start_marker(self):
        return bpy.context.scene.timeline_markers[self.start_marker_name]
        
    def set_start_marker(self, value):
        self.start_marker_name = value.name
    
    start_marker = property(get_start_marker, set_start_marker)
    
    
    
class AnimationProperties(bpy.types.PropertyGroup):
    current_animation = bpy.props.IntProperty(name = "current animation")
    animations = bpy.props.CollectionProperty(type=Animation)
    
class OBJECT_OT_add_animation(bpy.types.Operator):
    bl_idname = "object.add_nwn_animation"
    bl_label = "Add animation"
 
    name = bpy.props.StringProperty(name = "Name")
    start_frame = bpy.props.IntProperty(name = "Start Frame")
    end_frame = bpy.props.IntProperty(name = "End Frame")
 
   
    @classmethod
    def poll(cls, context):
        obj = context.object
        if not obj:
            return False
        return True
 
    def execute(self, context):
        obj = context.object
        if not obj.nwn_props:
            return {'CANCELLED'}
        
        #find the aurora base object
        
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
       

class BorealisBasicProperties(bpy.types.PropertyGroup):
    classification = bpy.props.EnumProperty(items = [("effects","Effects","Effects"),
                                                     ("character","Character","character"),
                                                     ("item","Item","Item"),
                                                     ("tile","Tile","tile")],
                                       name = "Classification",
                                       description = "The classification of the current model")
    supermodel = bpy.props.StringProperty(name = "Supermodel")
    animationscale = bpy.props.FloatProperty(name = "Animation Scale")
    root_object_name = bpy.props.StringProperty(name = "Root object name")
        
    @classmethod
    def register(cls):
        bpy.utils.register_class(Animation)
        bpy.utils.register_class(AnimationProperties)
        cls.animation_props = bpy.props.PointerProperty(type = AnimationProperties)
        
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
        
        #only display nwn modeling tools if the selected object is relevant in nwn
        if obj.type.upper() not in ['LAMP','MESH','EMPTY']:
            row = layout.row()
            row.label(text="Not compatible object")
            row = layout.row()
            row.label(text="Select a lamp, mesh or empty object")
            
            return
        
        box = layout.box()
        
        box.label(text="Basic model settings")
        box.prop(context.scene.nwn_props, "classification")
        box.prop(context.scene.nwn_props, "supermodel")
        box.prop(context.scene.nwn_props, "animationscale")
        box.prop_search(context.scene.nwn_props, "root_object_name", bpy.data, "objects")
        
        ### animation settings ###
        box = layout.box()
        
        box.label(text="Animation settings")
        
        row = layout.row()
        row.prop(obj.nwn_props, "is_nwn_object", text="Toggle NWN object")
        
        if obj.nwn_props.is_nwn_object:
            ### node settings ###
            box = layout.box()
            
            box.label(text="Node settings")

            node_type = "dummy"
            
            #only display the node types which makes sense for the selected blender object
            if not obj.data:
                box.prop(obj.nwn_props, "nwn_node_type")
                node_type = obj.nwn_props.nwn_node_type
            else:
                box.prop(obj.data, "nwn_node_type")
                node_type = obj.data.nwn_node_type
            
            from . import borealis_mdl_definitions
            
            #Compare all possible settings for the specific node_type with the ones 
            #loaded into blender
            col_flow = box.column_flow(columns=2)
            for prop in borealis_mdl_definitions.GeometryNodeProperties.get_node_properties(node_type):
                if prop in bpy.types.BorealisNodeProps.properties:
                    col_flow.prop(obj.nwn_props.node_properties, prop.name)
            
            
            
    
    @classmethod
    def register(cls):
        bpy.utils.register_class(BorealisSettings)
        bpy.types.Object.nwn_props = bpy.props.PointerProperty(type=BorealisSettings)
        
        
        bpy.utils.register_class(BorealisBasicProperties)
        bpy.types.Scene.nwn_props = bpy.props.PointerProperty(type=BorealisBasicProperties)
        
        bpy.utils.register_class(OBJECT_OT_add_animation)
        
        #we set different node type enum lists, to make sure only node types relevant to the 
        #selected blender object are allowed
        bpy.types.Mesh.nwn_node_type = bpy.props.EnumProperty(items = [("trimesh","trimesh","trimesh"),
                                        ("danglymesh","danglymesh","danglymesh"),
                                        ("skin","skin","skin"),
                                        ("emitter","emitter","emitter"),
                                        ("aabb","aabb","aabb")],
                                       name = "Node Type",
                                       description = "The NWN Node type of this object")
        
        bpy.types.Lamp.nwn_node_type = bpy.props.EnumProperty(items = [("light","light","light")],
                                       name = "Node Type",
                                       description = "The NWN Node type of this object")

