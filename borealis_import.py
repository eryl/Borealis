'''
Created on 11 aug 2010

@author: erik
'''

import bpy
from bpy.props import *

from . import borealis_lowlevel_mdl
from mathutils import Quaternion
from bpy_extras.io_utils import ExportHelper, ImportHelper
import os

class BorealisImport(bpy.types.Operator, ImportHelper):
    '''
    Load STL triangle mesh data
    '''
    bl_idname = "import_mesh.nwn_mdl"
    bl_label = "Import NWN Mdl"

    filename_ext = ".mdl"

    filter_glob = StringProperty(default="*.mdl", options={'HIDDEN'})

    files = CollectionProperty(name="File Path",
                          description="File path used for importing "
                                      "the MDL file",
                          type=bpy.types.OperatorFileListElement)

    directory = StringProperty(subtype='DIR_PATH')
    
    IMAGE_EXTENSIONS = ["tga", "dds", "TGA", "DDS"]
    DEFAULT_IMG_SIZE = 128

    objects = []
    context = None
    static_poses = {}
    def execute(self, context):
        self.context = context
        paths = [os.path.join(self.directory, name.name) for name in self.files]
        if not paths:
            paths.append(self.filepath)
        
        for path in paths:
            self.load_mdl(path)
            
        return {'FINISHED'}

    def setup_texture(self, mesh, node, filename):
        #if the node has no texture vertices, do nothing
        if not node.get_prop_value("tverts"):
            return
        
        ##load image ###
        image_name = node.get_prop_value("bitmap")
        image_name = image_name.lower()
        image = None
        if image_name not in bpy.data.images:
            image_path_base = os.path.join(os.path.dirname(filename), image_name)
            for ext in self.IMAGE_EXTENSIONS:
                path = image_path_base + "." + ext
                if os.path.exists(path):
                    bpy.ops.image.open(filepath=path)
                    image = bpy.data.images[os.path.basename(path)]
                    image.name = image_name
                    break
            
            #if the file couldnt be found, we create a dummy image with the right name
            if not image:
                bpy.ops.image.new(name=image_name, width=self.DEFAULT_IMG_SIZE,
                                          height=self.DEFAULT_IMG_SIZE)
                image = bpy.data.images[image_name]
                
        else:
            image = bpy.data.images[image_name]
        
        #we slice the vert since tverts has one value too many
        texture_verts = [[float(comp) for comp in vert[:2]] for vert in node.get_prop_value("tverts")]
        
        ## the face list points out which texture_verts to use
        nwn_uv_faces = [[int(vert) for vert in face[4:7]] for face in node.get_prop_value("faces")]
        
        mesh.uv_textures.new()
        mesh_uv_faces = mesh.uv_textures.active.data[:]
        
        for index, uv_face in enumerate(mesh_uv_faces):
            nwn_uv_face = nwn_uv_faces[index]
            uv_face.image = image
            uv_face.use_image = True 
            uv_face.uv1 = texture_verts[nwn_uv_face[0]]
            uv_face.uv2 = texture_verts[nwn_uv_face[1]]
            uv_face.uv3 = texture_verts[nwn_uv_face[2]]

    def import_geometry(self, mdl_object, filename):
        #create meshes from all nodes
        for node in mdl_object.geometry.nodes:
            ob = None
            
            if node.type == "dummy":
                ob = bpy.data.objects.new(node.name, None)

                
            elif node.type == "trimesh" or node.type=="danglymesh" or node.type=="skin":
                mesh = bpy.data.meshes.new(node.name+"Mesh")
                ob = bpy.data.objects.new(node.name, mesh)
                
                ### set up geometry ###
                
                verts = [[float(comp) for comp in vert] for vert in node.get_prop_value("verts")]
                faces = [[int(vert) for vert in face[:3]] for face in node.get_prop_value("faces")]
                mesh.from_pydata(verts,[],faces)
                
                ### set up texture and uv-coords ###
                self.setup_texture(mesh, node, filename)
                
                mesh.validate()
                mesh.update()
                
                
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
                
                mesh.validate()
                mesh.update()
                
            
            #set up parent
            parent_name = node.get_prop_value("parent")
            
            try:
                parent_ob = bpy.data.objects[parent_name]
            except KeyError:
                print("No such object: %s" % parent_name)
            else:
                ob.parent = parent_ob
            
            #set up location
            location = node.get_prop_value("position")
            if not location:
                location = [0,0,0]
            ob.location = location
            
            #set up rotation
            orientation = node.get_prop_value("orientation")
            if orientation:
                axis = orientation[:3]
                angle = orientation[3]
                
                ob.rotation_mode="AXIS_ANGLE"
                ob.rotation_axis_angle = [angle] + axis 

                            
            bpy.context.scene.objects.link(ob)
            self.objects.append(ob)
            
            ### set up properties for the object ###
            ## We're making the assumption that the custom properties from BorealisTools are
            #already registered for all objects
            ob.nwn_props.node_type = node.type
            
            if node.name == mdl_object.name:
                ob.nwn_props.is_aurabase = True
                ob.nwn_props.basic_settings.classification = mdl_object.classification
                ob.nwn_props.basic_settings.supermodel = mdl_object.supermodel
                ob.nwn_props.basic_settings.animationscale = float(mdl_object.setanimationscale)
            
            for prop in node.properties.values():
                if prop.has_blender_eq or not prop.value_written:
                    continue
                print("Adding property %s with value %s" % (prop.name, str(prop.value)))
                ob.nwn_props.node_properties[prop.name] = prop.value

    def import_animations(self, mdl_object):
        self.current_frame = 1
        bpy.ops.anim.change_frame(frame=self.current_frame)
        
        #set up the information for the static poses
        for ob in self.objects:
            poses = {}
            poses['location'] = ob.location[:]
            poses['rotation_axis_angle'] = ob.rotation_axis_angle[:]
            self.static_poses[ob] = poses
            
        self.import_animation(mdl_object.animations[0])
        
        #end by moving 10 frames ahead, like the max-script does
        self.current_frame += 10
            
        self.import_animation(mdl_object.animations[1])    
#        for animation in mdl_object.animations[:2]:
#            self.import_animation(animation)

    def import_animation(self, animation):
        fps = self.context.scene.render.fps
        
        start_frame = self.current_frame + 1
        length = animation.length * fps
        
        end_frame = start_frame + length
          
        #we start by setting the static pose before and after the animation
        bpy.ops.anim.change_frame(frame=start_frame - 1 )
        for ob in self.objects:
            #reset the static pose
            static_pose = self.static_poses[ob]
            ob.rotation_axis_angle = static_pose["rotation_axis_angle"]
            ob.location = static_pose["location"]
            
            ob.keyframe_insert(data_path='location', frame=self.current_frame, group="Location")
            ob.keyframe_insert(data_path='rotation_axis_angle', frame=self.current_frame, group="Rotation")
        
        bpy.ops.anim.change_frame(frame=end_frame + 1)
        for ob in self.objects:
            #reset the static pose
            static_pose = self.static_poses[ob]
            ob.rotation_axis_angle = static_pose["rotation_axis_angle"]
            ob.location = static_pose["location"]
            
            ob.keyframe_insert(data_path='location', frame=end_frame+1, group="Location")
            ob.keyframe_insert(data_path='rotation_axis_angle', frame=end_frame+1, group="Rotation")
        
            
        bpy.ops.anim.change_frame(frame=start_frame)
        #go back to the start frame and set the marker
        m = self.context.scene.timeline_markers.new(animation.name + "_start")
        m.frame = start_frame
        
        #set the end marker
        m = self.context.scene.timeline_markers.new(animation.name + "_end")
        m.frame = end_frame
        
        for node in animation.nodes:
            ob = bpy.data.objects[node.name]
            if not ob:
                continue
            
            for property in node.properties.values():
                if not property.value_written:
                    continue
                if property.name == "positionkey":
                    for time, x, y, z in property.value:
                        key_frame = time*fps + start_frame
#                        print("adding position key to frame %i" % key_frame)
                        bpy.ops.anim.change_frame(frame=key_frame)
                        
                        ob.location = x,y,z
                        ob.keyframe_insert(data_path='location', frame=key_frame, group="Location")
                        
                elif property.name == "orientationkey":
                    for time, x, y, z, angle in property.value:
                        key_frame = time * fps + start_frame
#                        print("adding orientation key to frame %i" % key_frame)
                        bpy.ops.anim.change_frame(frame = key_frame)
                        
                        ob.rotation_axis_angle = [angle,x,y,z]
                        ob.keyframe_insert(data_path='rotation_axis_angle', frame=key_frame, group="Rotation")
        
        self.current_frame = end_frame
        bpy.ops.anim.change_frame(frame=1)
        
    def load_mdl(self,filename, ):
        mdl_object = borealis_lowlevel_mdl.Model()
        mdl_object.from_file(filename)
        
        self.import_geometry(mdl_object, filename)
        print("Number of nodes in file: %i\tnumber of objects in scene: %i" % (len(mdl_object.geometry.nodes),len(self.objects)))
        self.import_animations(mdl_object)
        
        

                