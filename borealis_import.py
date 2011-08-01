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
                    vertex_group = ob.vertex_groups.new("danglymesh_constraints")
                    ob.nwn_props.danglymesh_vertexgroup = "danglymesh_constraints"
                    for i,[const] in enumerate(node['constraints']):
                        constraint = 255 - const #a weight of 1 is completely solid when using softbody
                        weight = constraint/255.0
                    
                        vertex_group.add([i], weight, 'ADD')
                
                elif node.type == "skin":
                    #set up the skin, this will require a non-trivial solution
                    nwn_weights = node['weights']
                    weights_dict = {}
                    for i, weight_line in enumerate(nwn_weights):
                        #this parses the line to simplify creation of the dictionary
                        line = zip([bone for i, bone in enumerate(weight_line) if i % 2 == 0],
                                    [float(weight) for i, weight in enumerate(weight_line) if i % 2 != 0])
                        for bone, weight in line:
                            if bone not in weights_dict:
                                weights_dict[bone] = {}
                            weights_dict[bone][i] = weight
                    
                    for bone, weights in weights_dict.items():
                        vertex_group_name = "nwn_skin_" + bone
                        vertex_group = ob.vertex_groups.new(vertex_group_name)
                        for index, weight in weights.items():
                            vertex_group.add([index], weight, 'ADD')
                            
                        ##add the hook modifier
                        hook_name = "nwn_skin_hook_" + bone
                        hook_mod = ob.modifiers.new(name = hook_name, type = 'HOOK')
                        hook_mod.object = bpy.data.objects[bone]
                        hook_mod.vertex_group = vertex_group_name
                        
                    
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
            
            #this has to be done after the object has been linked to the scene
            if node.type == "skin":
                bpy.ops.object.select_name(name=ob.name)
                bpy.ops.object.mode_set(mode = 'EDIT')
                for modifier in ob.modifiers:
                    if modifier.type == 'HOOK':
                        
                        bpy.ops.object.hook_reset(modifier = modifier.name)
                bpy.ops.object.mode_set(mode = 'OBJECT')
            
            ### set up properties for the object ###
            ## We're making the assumption that the custom properties from BorealisTools are
            #already registered for all objects
            if ob.type == 'EMPTY':
                ob.nwn_props.nwn_node_type = node.type
            else:
                ob.data.nwn_node_type = node.type
            ob.nwn_props.is_nwn_object = True
            
            
            for prop in node.properties.values():
                if prop.has_blender_eq or not prop.value_written:
                    continue
                ob.nwn_props.node_properties[prop.name] = prop.value

    def import_animations(self, mdl_object):
        self.current_frame = 1
        bpy.ops.anim.change_frame(frame=self.current_frame)
        
        #set up the information for the static poses
        static_poses = {}
        object_paths = {}
        animations_dict = {}
        for ob in self.objects:
            poses = {}
            poses['location'] = ob.location[:]
            poses['rotation_axis_angle'] = ob.rotation_axis_angle[:]
            static_poses[ob] = poses
            ob.animation_data_create()
            ob.animation_data.action = bpy.data.actions.new(name = "NWN animation track")
            object_paths[ob.name] = {}
            object_paths[ob.name]['location']= {}
            object_paths[ob.name]['rotation_axis_angle']= {}
            
            object_paths[ob.name]['location']['x'] = ob.animation_data.action.fcurves.new(data_path="location", index=0)
            object_paths[ob.name]['location']['y'] = ob.animation_data.action.fcurves.new(data_path="location", index=1)
            object_paths[ob.name]['location']['z'] = ob.animation_data.action.fcurves.new(data_path="location", index=2)
            
            object_paths[ob.name]['rotation_axis_angle']['w'] = ob.animation_data.action.fcurves.new(data_path="rotation_axis_angle", index=0)
            object_paths[ob.name]['rotation_axis_angle']['x'] = ob.animation_data.action.fcurves.new(data_path="rotation_axis_angle", index=1)
            object_paths[ob.name]['rotation_axis_angle']['y'] = ob.animation_data.action.fcurves.new(data_path="rotation_axis_angle", index=2)
            object_paths[ob.name]['rotation_axis_angle']['z'] = ob.animation_data.action.fcurves.new(data_path="rotation_axis_angle", index=3)
            
            animations_dict[ob.name] = {'location' : {'x' : [], 'y' : [], 'z' : []}, 
                                        'rotation_axis_angle' : {'x' : [], 'y' : [], 'z' : [], 'w' : []}}
            
        
        #the animations_dict dictionary will collect all the animation data which 
        #will later be inserted into blenders data
        
        
#        animations_dict
#            object
#                data_path
#                    array_id
#                        keyframes : list
#                            (frame, value)

        current_frame = 1

        for animation in mdl_object.animations:
            current_frame = self.set_static_frame(static_poses, animations_dict, current_frame)
            current_frame += 1
            current_frame = self.import_animation_with_direct_point_insertion(animation, animations_dict, current_frame)
            current_frame += 10
            
        self.apply_animations(animations_dict, object_paths)
    
    def apply_animations(self, animations_dict, object_paths):
        """
        Takes the information inserted in animations_dict and apply it to the channels of every object
        """
        for ob, data_paths in animations_dict.items():
            for data_path, components in data_paths.items():
                for component, values in components.items():
                    fcurve = object_paths[ob][data_path][component]
                    fcurve.keyframe_points.add(len(values))
                    for i, value in enumerate(values):
                        fcurve.keyframe_points[i].co = value
                    
    def set_static_frame(self, static_poses, animations_dict, current_frame):
        """
        Inserts the static pose for all objects for the current frame, and returns value of next frame.
        """
        for ob, poses in static_poses.items():
            loc_x, loc_y, loc_z = poses['location']
            rot_w, rot_x, rot_y, rot_z = poses['rotation_axis_angle']
            
            animations_dict[ob.name]['location']['x'].append((current_frame, loc_x))
            animations_dict[ob.name]['location']['y'].append((current_frame, loc_y))
            animations_dict[ob.name]['location']['z'].append((current_frame, loc_z))
            
            animations_dict[ob.name]['rotation_axis_angle']['w'].append((current_frame, rot_w))
            animations_dict[ob.name]['rotation_axis_angle']['x'].append((current_frame, rot_x))
            animations_dict[ob.name]['rotation_axis_angle']['y'].append((current_frame, rot_y))
            animations_dict[ob.name]['rotation_axis_angle']['z'].append((current_frame, rot_z))
        
        return current_frame
    
    def import_animation_with_blender_keyinsert(self, animation):
        """
        This version uses blenders own way of inserting keyframes. The animations seems slightly off
        and the function is really slow, especially for long animations
        """
        fps = self.context.scene.render.fps
        
        start_frame = self.current_frame + 1
        length = int(animation.length * fps)
        
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
        
        
        anim_ob = bpy.context.scene.nwn_props.animation_props.animations.add()
        anim_ob.name = animation.name
        #go back to the start frame and set the marker
        m = self.context.scene.timeline_markers.new(animation.name + "_start")
        m.frame = start_frame
        anim_ob.start_marker = m
        
        #set the end marker
        m = self.context.scene.timeline_markers.new(animation.name + "_end")
        m.frame = end_frame
        anim_ob.end_marker = m
        
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
        
        
    def import_animation_with_direct_point_insertion(self, animation, animations_dict, current_frame):
        """
        This version inserts the data directly into the channels. Might break if blenders 
        internals changes. Should be much faster than the other version.
        Returns the frame number of the last frame in the animation
        """
        fps = self.context.scene.render.fps
        
        start_frame = current_frame
        length = int(animation.length * fps)
        
        end_frame = start_frame + length
        
        #The animation object holds the borealis-specific data, such as marker information
        anim_ob = bpy.context.scene.nwn_props.animation_props.animations.add()
        anim_ob.name = animation.name
        #set the start marker
        m = self.context.scene.timeline_markers.new(animation.name + "_start")
        m.frame = start_frame
        anim_ob.start_marker = m
        
        #set the end marker
        m = self.context.scene.timeline_markers.new(animation.name + "_end")
        m.frame = end_frame
        anim_ob.end_marker = m
        
        
        for node in animation.nodes:
            for property in node.properties.values():
                if not property.value_written:
                    continue
                if property.name == "positionkey":
                    for time, x, y, z in property.value:
                        key_frame = time*fps + start_frame
#                        print("adding position key to frame %i" % key_frame)
                        animations_dict[node.name]['location']['x'].append((key_frame, x))
                        animations_dict[node.name]['location']['y'].append((key_frame, y))
                        animations_dict[node.name]['location']['z'].append((key_frame, z))
                        
                elif property.name == "orientationkey":
                    for time, x, y, z, w in property.value:
                        key_frame = time * fps + start_frame
#                        print("adding orientation key to frame %i" % key_frame)
                        animations_dict[node.name]['rotation_axis_angle']['w'].append((key_frame, w))
                        animations_dict[node.name]['rotation_axis_angle']['x'].append((key_frame, x))
                        animations_dict[node.name]['rotation_axis_angle']['y'].append((key_frame, y))
                        animations_dict[node.name]['rotation_axis_angle']['z'].append((key_frame, z))
        return end_frame
        
    def load_mdl(self,filename, ):
        mdl_object = borealis_lowlevel_mdl.Model()
        mdl_object.from_file(filename)
        
        self.import_geometry(mdl_object, filename)
        self.import_animations(mdl_object)
        
        #the basic settings for the models are assigned to the active scene object
        scene = bpy.context.scene
        scene.nwn_props.root_object_name = mdl_object.name
        
        scene.nwn_props.classification = mdl_object.classification
        scene.nwn_props.supermodel = mdl_object.supermodel
        scene.nwn_props.animationscale = float(mdl_object.setanimationscale)
        
        

                