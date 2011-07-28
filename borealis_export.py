'''
Created on 11 aug 2010

@author: erik
'''

import os
import bpy
from bpy.props import CollectionProperty, StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper


class BorealisExport(bpy.types.Operator, ExportHelper):
    '''Export a single object as a stanford PLY with normals, colours and texture coordinates.'''
    bl_idname = "export_mesh.nwn_mdl"
    bl_label = "Export NWN Mdl"


    filepath = bpy.props.StringProperty(name="File Path",
                          description="File path used for exporting "
                                      "the active object to STL file",
                          maxlen=1024,
                          default="")
    filename_ext = ".mdl"
    filter_glob = StringProperty(default="*.mdl", options={'HIDDEN'})


    use_modifiers = BoolProperty(name="Apply Modifiers", description="Apply Modifiers to the exported mesh", default=True)
    use_normals = BoolProperty(name="Normals", description="Export Normals for smooth and hard shaded faces", default=True)
    use_uv_coords = BoolProperty(name="UVs", description="Exort the active UV layer", default=True)
    use_colors = BoolProperty(name="Vertex Colors", description="Exort the active vertex color layer", default=True)
    guess_name = BoolProperty(name="Use Root Object Name", description="Use the name of the root object as the model name and filename like Neverwinter Nights expects", default=True)
    
    
    
    @classmethod
    def poll(cls, context):
        ## Check to see that the root object exists
        
        return context.scene.nwn_props.root_object_name != None

    def execute(self, context):
        filepath = self.filepath
        filepath = bpy.path.ensure_ext(filepath, self.filename_ext)
        
        return export_nwn_mdl(context, **self.as_keywords(ignore=("check_existing", "filter_glob")))

from . import borealis_lowlevel_mdl as bor
        

def export_nwn_mdl(context, **kwargs):
    mdl = bor.Model()
    scene_props = context.scene.nwn_props
    root_object = context.scene.objects[scene_props.root_object_name]
    
    #poll should catch this
    if not root_object:
        return {'CANCELLED'}
    
    mdl.name = root_object.name
    mdl.classification = scene_props.classification
    mdl.supermodel = scene_props.supermodel
    mdl.setanimationscale =  scene_props.animationscale
    
    export_root(mdl, root_object)
    
    return {'FINISHED'}

def export_root(mdl, obj):
    node = mdl.new_geometry_node("dummy", obj.name)
    node['parent'] = "NULL"

    for child in obj.children:
        export_node(mdl, child, obj.name)
        
def export_node(mdl, obj, parent):
    
    if obj.type in ['MESH', 'LIGHT']:
        node_type = obj.data.nwn_node_type
    else:
        node_type = obj.nwn_props.nwn_node_type
        
    node = mdl.new_geometry_node(node_type, obj.name)
    node['parent'] = parent
    
    print("Exporting node %s of type: %s" % (obj.name, node_type))
    
    from . import borealis_mdl_definitions
    
    w, x, y, z = obj.rotation_axis_angle
    orientation = [x, y, z, w] 
    node['orientation'] = orientation
    
    node['position'] = obj.location
    
    for prop in borealis_mdl_definitions.GeometryNodeProperties.get_node_properties(node_type):
        #only export the properties which are set in the properties group
        if prop.name in obj.nwn_props.node_properties and not prop.has_blender_eq:
            node[prop.name] = eval("obj.nwn_props.node_properties." + prop.name)
    
    print(str(node))

    for child in obj.children:
        export_node(mdl, child, obj.name)
    
    