'''
Created on 11 aug 2010

@author: erik
'''
import bpy, mathutils

class BorealisTools(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "NWN Model tools"
#    bl_context = "objectmode"

    nw_property = bpy.props.BoolProperty(name="nw_prop",
                          description="NWN property to set/unset")
    
    node_list = ["dummy","trimesh","danglymesh","skin","light","emitter"]
    node_types = bpy.props.EnumProperty(items=[(type, type, type+"ara") for type in node_list], name="Node type")
    col = mathutils.Color()
    
    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.label(text="Hello world!", icon='WORLD_DATA')

        row = layout.row()
        row.label(text="Active object is: " + obj.name)
        row = layout.row()
        
       
        row.prop(self, "nw_property")
        row = layout.row()
        row.prop(self, "node_types", text="Node type")
        if "NWN_properties" in obj.keys():
            row.prop(obj,"NWN_properties")

class OBJECT_OT_nwnboolean(bpy.types.Operator):
    bl_idname = "nwnboolean"
    bl_label = "nw_boolean"



    def execute(self, context):
        self.load_mdl(self.properties.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.manager
        wm.add_fileselect(self)

        return {'RUNNING_MODAL'}
print("foo")
bpy.types.register(OBJECT_OT_nwnboolean)