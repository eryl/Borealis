'''
Created on 11 aug 2010

@author: erik
'''

import bpy
from bpy.props import *

class BorealisExport(bpy.types.Operator):
    '''
    Save STL triangle mesh data from the active object
    '''
    bl_idname = "export_mesh.nwn_mdl"
    bl_label = "Export NWN Mdl"

    filepath = bpy.props.StringProperty(name="File Path",
                          description="File path used for exporting "
                                      "the active object to STL file",
                          maxlen=1024,
                          default="")
  

    def execute(self, context):
                
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.manager
        wm.add_fileselect(self)
        return {'RUNNING_MODAL'}