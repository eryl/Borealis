'''
Created on 11 aug 2010

@author: erik
'''

import bpy
from bpy.props import *

from borealis_lowlevel_mdl import *
from mathutils import Quaternion

class BorealisImport(bpy.types.Operator):
    '''
    Load STL triangle mesh data
    '''
    bl_idname = "import_mesh.nwn_mdl"
    bl_label = "Import NWN Mdl"

    filepath = bpy.props.StringProperty(name="File Path",
                          description="File path used for importing "
                                      "the STL file",
                          maxlen=1024,
                          default="")

    def execute(self, context):
        self.load_mdl(self.properties.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.manager
        wm.add_fileselect(self)

        return {'RUNNING_MODAL'}


    def load_mdl(self,filename):
        mdl_object = Model()
        #mdl_object.from_file(self.properties.filepath)
        mdl_object.from_file(filename)
        
        #create meshes from all nodes
        for node in mdl_object.geometry.nodes:
            ob = None
            
            if node.type == "dummy":
                ob = bpy.data.objects.new(node.name, None)

                
            elif node.type == "trimesh" or node.type=="danglymesh" or node.type=="skin":
                mesh = bpy.data.meshes.new(node.name+"Mesh")
                ob = bpy.data.objects.new(node.name, mesh)
                
                
                verts = [[float(comp) for comp in vert] for vert in node.get_prop_value("verts")]
                faces = [[int(vert) for vert in face[:3]] for face in node.get_prop_value("faces")]
                mesh.from_pydata(verts,[],faces)
                
                mesh.update
                
                if node.type == "danglymesh":
                    #set up a weight-map for the danlgymesh
                    pass
                
                elif node.type == "skin":
                    #set up the skin, this will require a non-trivial solution
                    pass
                    
            elif node.type == "light":
                pass
            
            elif node.type == "emitter":
                #set up a dummy mesh used as the emitter
                mesh = bpy.data.meshes.new(node.name+"Mesh")
                ob = bpy.data.objects.new(node.name, mesh)
                
                verts = [[0,0,0]]
                faces = []
                mesh.from_pydata(verts,[],[])
                
                mesh.update
            
            #set up parent
            parent_name = node.get_prop_value("parent")[0]
            
            try:
                parent_ob = bpy.data.objects[parent_name]
            except KeyError:
                print("No such object: %s" % parent_name)
            else:
                ob.parent = parent_ob
            
            #set up location
            location = [float(comp) for comp in node.get_prop_value("position")]
            if not location:
                location = [0,0,0]
            ob.location = location
            
            #set up rotation
            orientation = [float(comp) for comp in node.get_prop_value("orientation")]
            if orientation:
                axis = orientation[:3]
                angle = orientation[3]
                
                ob.rotation_mode="AXIS_ANGLE"
                ob.rotation_axis_angle = [angle] + axis 

            ob.draw_name = False
                
            bpy.context.scene.objects.link(ob)
                
            ### set up properties for the object ###
            ob["NWN_info"] = {}
            ob["NWN_info"]["type"] = node.type
            
            
            ob["NWN_properties"] = {}
            for prop in node.properties:
                if prop.has_blender_eq:
                    continue
                ob["NWN_properties"][prop.name] = prop.value

                