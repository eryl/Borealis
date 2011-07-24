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
                                        ("light","light","light")],
                                       name = "Node Type",
                                       description = "The NWN Node type of this object")

class OBJECT_PT_borealis_basic(bpy.types.Panel):
    bl_idname = "OBJECT_PT_borealis_basic"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "NWN Basic Settings"
    bl_context = "object"
    
    def draw(self,context):
        pass
    
class OBJECT_PT_borealis_animations(bpy.types.Panel):
    bl_idname = "OBJECT_PT_borealis_animations"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "NWN Animation Controls"
    bl_context = "object"
    
    def draw(self,context):
        pass

class OBJECT_PT_node_tools(bpy.types.Panel):
    bl_idname = "OBJECT_PT_nwn_tools"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "NWN Node tools"
    bl_context = "object"
    
    def draw(self,context):
        pass
    
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
        
        for key in obj.nwn_props.keys():
            print(key)
            row = layout.row()
        
            row.prop(obj.nwn_props, key)
        
        
        
        box = layout.box()
        box.label("Selection Tools")
        box.operator("object.select_all")
        row = box.row()
        row.operator("object.select_inverse")
        row.operator("object.select_random")
    
    @classmethod
    def register(cls):
        bpy.utils.register_class(BorealisSettings)
        bpy.types.Object.nwn_props = bpy.props.PointerProperty(type=BorealisSettings)
        



                                       

class OBJECT_OT_make_nwn_object(bpy.types.Operator):
    bl_idname = "nwn.make_nwn_object"
    bl_label = "Make this an nwn object"
    
    def execute(self, context):
        pass

