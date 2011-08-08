# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

'''
Created on 11 aug 2010

@author: erik
'''

import os
import bpy
from bpy.props import CollectionProperty, StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper
from . import basic_props
from . import mdl
    

class BorealisExport(bpy.types.Operator, ExportHelper):
    '''Export a single object as a stanford PLY with normals, colours and texture coordinates.'''
    bl_idname = "export_mesh.nwn_mdl"
    bl_label = "Export NWN mdl"


    filepath = bpy.props.StringProperty(name="File Path",
                          description="File path used for exporting "
                                      "the active object to STL file",
                          maxlen=1024,
                          default="")
    filename_ext = ".mdl"
    filter_glob = StringProperty(default="*.mdl", options={'HIDDEN'})

    use_root_name = BoolProperty(name="Use Root Object Name", description="Use the name of the root object as the model name and filename like Neverwinter Nights expects, if false the filename will be used as the model name in the model file", default=True)
    export_animations = BoolProperty(name="Export Animations", description="Toggle whether animations should be exported or not", default=True) 
    
    
    @classmethod
    def poll(cls, context):
        ## Check to see that the root object exists
        
        return context.scene.nwn_props.root_object_name != None

    def execute(self, context):
        filepath = self.filepath
        filepath = bpy.path.ensure_ext(filepath, self.filename_ext)
        
        return export_nwn_mdl(context, **self.as_keywords(ignore=("check_existing", "filter_glob")))

        

def export_nwn_mdl(context, **kwargs):
    scene_props = context.scene.nwn_props
    root_object = context.scene.objects[scene_props.root_object_name]
    
    if kwargs['use_root_name']:
        model_name = root_object.name
    else:
        filepath = kwargs['filepath']
        base_name = os.path.basename(kwargs['filepath'])
        model_name, ext = os.path.splitext(base_name)
        
    #poll should catch this
    if not root_object:
        return {'CANCELLED'}
    
    mdl_object = mdl.Model(model_name)
    mdl_object.classification = scene_props.classification
    mdl_object.supermodel = scene_props.supermodel
    mdl_object.setanimationscale =  scene_props.animationscale
    
    #this will act as an accumulator, containing the objects which has been exported
    exported_objects = []
    export_geometry(mdl_object, root_object, exported_objects)
    
    if kwargs['export_animations']:
        export_animations(context.scene, mdl_object, root_object, exported_objects)
    
#    if os.path.exists(kwargs['filepath']):
#        print("Path exists")
#    else:
    file = open(kwargs['filepath'], 'w')
    file.write(str(mdl_object))
    file.close()
    
    return {'FINISHED'}

def export_geometry(mdl_object, obj, exported_objects):
    node = mdl_object.new_geometry_node("dummy", obj.name)
    node['parent'] = "NULL"
    exported_objects.append(obj)
    for child in obj.children:
        export_node(mdl_object, child, obj.name, exported_objects)
    
        
def export_node(mdl_object, obj, parent, exported_objects):
    
    if obj.type in ['MESH', 'LIGHT']:
        node_type = obj.data.nwn_node_type
    else:
        node_type = obj.nwn_props.nwn_node_type
        
    node = mdl_object.new_geometry_node(node_type, obj.name)
    node['parent'] = parent
    
    w, x, y, z = obj.rotation_axis_angle
    orientation = [x, y, z, w] 
    node['orientation'] = orientation
    
    node['position'] = obj.location
    
    for prop in basic_props.GeometryNodeProperties.get_node_properties(node_type):
        #only export the properties which are set in the properties group
        if prop.name in obj.nwn_props.node_properties and not prop.blender_ignore:
            node[prop.name] = eval("obj.nwn_props.node_properties." + prop.name)

    if node_type in ["trimesh", "skin", "danglymesh"]:
        export_mesh(obj, node)

    exported_objects.append(obj)
    for child in obj.children:
        export_node(mdl_object, child, obj.name, exported_objects)

def export_mesh(obj, node):
    mesh = obj.data
    uv_faces = None
    image = None
        
    if mesh.uv_textures:
        uv_faces = mesh.uv_textures.active.data
        image = uv_faces[0].image
    
    #somehow we have to accomodate for the difference in how blender and nwn
    #handles the uv-coords. In nwn every uv vertice corresponds to a geometry vertice
    #in blender, every face has it's own uv-vertices
    
    vertices = [vert.co[:] for vert in mesh.vertices]
    node['verts'] = vertices
    
    smooth_group = 1
    faces = []
    uv_verts = []
    uv_verts_dict = {}
    
    uv_verts
    for i, face in enumerate(mesh.faces):
        v1, v2, v3 = face.vertices[:]
        
        if uv_faces:
            uv_co1, uv_co2, uv_co3 = uv_faces[i].uv1, uv_faces[i].uv2, uv_faces[i].uv3
            
            if uv_co1[0] not in uv_verts_dict:
                uv_verts_dict[uv_co1[0]] = {}
            if uv_co1[1] not in uv_verts_dict[uv_co1[0]]:
                uv1 = len(uv_verts)
                uv_verts.append(uv_co1[:])
                uv_verts_dict[uv_co1[0]][uv_co1[1]] = uv1
            else:
                uv1 = uv_verts_dict[uv_co1[0]][uv_co1[1]]
            
            
            if uv_co2[0] not in uv_verts_dict:
                uv_verts_dict[uv_co2[0]] = {}
            if uv_co2[1] not in uv_verts_dict[uv_co2[0]]:
                uv2 = len(uv_verts)
                uv_verts.append(uv_co2[:])
                uv_verts_dict[uv_co2[0]][uv_co2[1]] = uv2
            else:
                uv2 = uv_verts_dict[uv_co2[0]][uv_co2[1]]
            
            if uv_co3[0] not in uv_verts_dict:
                uv_verts_dict[uv_co3[0]] = {}
            if uv_co3[1] not in uv_verts_dict[uv_co3[0]]:
                uv3 = len(uv_verts)
                uv_verts.append(uv_co3[:])
                uv_verts_dict[uv_co3[0]][uv_co3[1]] = uv3
            else:
                uv3 = uv_verts_dict[uv_co3[0]][uv_co3[1]]
        else:
            uv1, uv2, uv3 = 0,0,0
        face_line = [v1, v2, v3, smooth_group, uv1, uv2, uv3, 1] #don't know what the last value is 
        
        faces.append(face_line)
    
    #add the third value to the tverts
    tverts = [[uv1, uv2, 0] for uv1, uv2 in uv_verts]
    node['tverts'] = tverts
    node['faces'] = faces
    
    if image:
        #use the filename for the texture as primary name
        #fall back on the name of the image 
        if os.path.exists(image.filepath):
            image_filename = os.path.basename(image.filepath)
            node['bitmap'], ext = os.path.splitext(image_filename)
        else:
            node['bitmap'] = image.name
    else:
        node['bitmap'] = "NULL"
        
    if node.type == "danglymesh":
        vertex_group_name = obj.nwn_props.danglymesh_vertexgroup
        if vertex_group_name:
            vertex_group = obj.vertex_groups[vertex_group_name]
            constraints = []
            for i in range(len(mesh.vertices)):
                constraint = vertex_group.weight(i) * 255
                constraint = 255 - int(constraint)
                constraints.append([constraint])
            node['constraints'] = constraints
    
    elif node.type == "skin":
        bones = []
        hooks = [mod for mod in obj.modifiers if mod.type == 'HOOK']
        
        
        bones_list = [{} for vert in mesh.vertices]
        
        for hook in hooks:
            if not (hook.vertex_group and hook.object):
                break
            
            vertex_group = obj.vertex_groups[hook.vertex_group]
            
            for i, bones in enumerate(bones_list):
                #there doesn't seem to be any way of checking whether a vertex i in a group
                # hence this try-clause 
                try:
                    if vertex_group.weight(i) > 0:
                        bones[hook.object.name] = vertex_group.weight(i)
                except RuntimeError:
                    pass  
        
        weights = []
        for bones in bones_list:
            total_weight = 0
            for weight in bones.values():
                total_weight += weight
            norm_co = 1/total_weight
            line = []
            for bone, weight in bones.items():
                line.append(bone)
                line.append("%.9g" % (weight*norm_co))
            weights.append(line)
        
        node["weights"] = weights
        

def export_animations(scene, mdl_object,root_object, exported_objects):
    animations = scene.nwn_props.animation_props.animations
    
    if not animations:
        return
    
    animation_data = build_animation_data(exported_objects, animations)
    
    for animation in animations:
        export_animation(animation_data[animation.name], scene, animation, mdl_object, root_object)

def export_animation(animation_data, scene, animation, mdl_object, root_object):
    fps = scene.render.fps
    nwn_anim = mdl_object.new_animation(animation.name)
    nwn_anim.animroot = root_object.name 
    
    start_frame = animation.start_frame
    end_frame = animation.end_frame
    
    nwn_anim.length = (end_frame - start_frame) / fps
    nwn_anim.transtime = animation.transtime
    
    for event in animation.events:
        nwn_anim.events.append((event.time, event.type))
    root_node = nwn_anim.new_node("dummy", root_object.name)
    root_node.parent = 'NULL'
    
    
    for child in root_object.children:
        export_animation_node(fps, animation_data, animation, nwn_anim, mdl_object, child, root_object.name)
        
def export_animation_node(fps, animation_data, animation, nwn_anim, mdl_object, obj, parent):
    if obj.type in ['MESH', 'LIGHT']:
        node_type = obj.data.nwn_node_type
    else:
        node_type = obj.nwn_props.nwn_node_type
    
    node = nwn_anim.new_node("dummy", obj.name)
    node['parent'] = parent
    start_frame = animation.start_frame
    if obj.name in animation_data['nodes']:
        if "location" in animation_data['nodes'][obj.name]:
            locations = sorted(animation_data['nodes'][obj.name]["location"].items())
            positionkeys = [[(time - start_frame) / fps, pos['x'], pos['y'], pos['z']] for time, pos in locations]
            node['positionkey'] = positionkeys
           
        if "rotation_axis_angle" in animation_data['nodes'][obj.name]:
            rotations = sorted(animation_data['nodes'][obj.name]["rotation_axis_angle"].items())
            orientationkey = [[(time - start_frame) / fps, ori['x'], ori['y'], ori['z'], ori['w']] for time, ori in rotations]
            node['orientationkey'] = orientationkey
            
    for child in obj.children:
        export_animation_node(fps, animation_data, animation, nwn_anim, mdl_object, child, obj.name)
    
def build_animation_data(objects, animations):
    """
    We create a complete dictionary of all objects and their animation data for simplified
    access later on
    """
    #We build a tree with all the animation n
    
    animation_list = [{"name" : animation.name, 
                       "start_frame" : animation.start_frame,
                       "end_frame" : animation.end_frame,
                       "nodes" : {}} for animation in animations]
    
    animation_list.sort(key=lambda x: x["start_frame"])
    
    #we build a mighty dictionary where the keyframe points are gathered depending on 
    #time, and not seperate channels for every object
    times = {}
    
    for object in objects:
        if not object.animation_data:
            continue
        for fcurve in object.animation_data.action.fcurves:
            attribute_name = "foo"
            if fcurve.data_path == "location":
                if fcurve.array_index == 0:
                    attribute_name = "x"
                elif fcurve.array_index == 1:
                    attribute_name = "y"
                elif fcurve.array_index == 2:
                    attribute_name = "z"    
            elif fcurve.data_path == "rotation_axis_angle":
                if fcurve.array_index == 0:
                    attribute_name = "w"
                elif fcurve.array_index == 1:
                    attribute_name = "x"
                elif fcurve.array_index == 2:
                    attribute_name = "y"   
                elif fcurve.array_index == 3:
                    attribute_name = "z"
            
            for point in fcurve.keyframe_points:
                if point.co[0] not in times:
                    times[point.co[0]] = {}
                if object.name not in times[point.co[0]]:
                    times[point.co[0]][object.name] = {}
                if fcurve.data_path not in times[point.co[0]][object.name]:
                    times[point.co[0]][object.name][fcurve.data_path] = {}
                times[point.co[0]][object.name][fcurve.data_path][attribute_name] = point.co[1]
    
    times_list = sorted(times.items())
    current_time = times_list.pop(0)
    for animation in animation_list:
        while(current_time[0] <= animation['end_frame']):    
            #if we find a time which has already 'passed', it isn't part of any animation
            #and is therefore discarded        
            if current_time[0] >= animation['start_frame']:
                for node, data_paths in current_time[1].items():
                    if node not in animation['nodes']:
                        animation['nodes'][node] = {} 
                    for path, attributes in data_paths.items():
                        if path not in animation['nodes'][node]:
                            animation['nodes'][node][path] = {}
                        animation['nodes'][node][path][current_time[0]] = attributes
            
            if not times_list:
                break;
            current_time = times_list.pop(0)        
                
        
    animation_dict = dict(zip([animation['name'] for animation in animation_list],
                               animation_list))
    
    return animation_dict 