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
    
    exported_objects = []#this will act as an accumulator, containing the objects which has been exported
    export_root(mdl, root_object, exported_objects)
    export_animations(context.scene, mdl, root_object, exported_objects)
    return {'FINISHED'}


def export_root(mdl, obj, acc):
    node = mdl.new_geometry_node("dummy", obj.name)
    node['parent'] = "NULL"
    acc.append(obj)
    for child in obj.children:
        export_node(mdl, child, obj.name, acc)
        
def export_node(mdl, obj, parent, acc):
    
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
    
    #print(str(node))

    acc.append(obj)
    for child in obj.children:
        export_node(mdl, child, obj.name, acc)
    
def export_animations(scene, mdl,root_object, exported_objects):
    animations = scene.nwn_props.animation_props.animations
    
    animation_data = build_animation_data(exported_objects, animations)
    
    for animation in animations:
        export_animation(animation_data[animation.name], scene, animation, mdl, root_object)

def export_animation(animation_data, scene, animation, mdl, root_object):
    fps = scene.render.fps
    nwn_anim = mdl.new_animation(animation.name)
    nwn_anim.animroot = root_object.name 
    
    start_frame = animation.start_frame
    end_frame = animation.end_frame
    
    nwn_anim.length = (end_frame - start_frame) / fps
    nwn_anim.transtime = animation.transtime
    
    root_node = nwn_anim.new_node("dummy", root_object.name)
    root_node.parent = 'NULL'
    
    
    for child in root_object.children:
        export_animation_node(fps, animation_data, animation, nwn_anim, mdl, child, root_object.name)
        
def export_animation_node(fps, animation_data, animation, nwn_anim, mdl, obj, parent):
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
            
    print(str(node))
    for child in obj.children:
        export_animation_node(fps, animation_data, animation, nwn_anim, mdl, child, obj.name)
    
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
    nodes = {}
    times = {}
    
    for object in objects:
        nodes[object.name] = {}
        
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
            
            if fcurve.data_path not in nodes[object.name]:
                nodes[object.name][fcurve.data_path] = {}
            data_dict = nodes[object.name][fcurve.data_path]
            
            for point in fcurve.keyframe_points:
                if point.co[0] not in data_dict:
                    data_dict[point.co[0]] = {}
                data_dict[point.co[0]][attribute_name] = point.co[1]
                
                #this sets up a nested dictionary where the topmost keys are time-points for keyframes
                # timepoint
                #    nodename
#                        data_path
#                            attribute
#                                value
                    
                if point.co[0] not in times:
                    times[point.co[0]] = {}
                if object.name not in times[point.co[0]]:
                    times[point.co[0]][object.name] = {}
                if fcurve.data_path not in times[point.co[0]][object.name]:
                    times[point.co[0]][object.name][fcurve.data_path] = {}
                times[point.co[0]][object.name][fcurve.data_path][attribute_name] = point.co[1]
    
    print(len(times))
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
    "TODO - Must get the animations to have the data of all the keyframes for their nodes"  
    
    return animation_dict 