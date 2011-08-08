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
import bpy

class OBJECT_PT_nwn_colors(bpy.types.Panel):
    bl_idname = "SCENE_PT_nwn_basic_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "NWN Walkmesh Colors"
    bl_context = "vertexpaint"
    def draw(self, context):
        layout = self.layout
        for color in context.scene.nwn_props.walkmesh_colors:
            row = layout.row()
            col = row.prop(color, "color")
            col.active = False
            row.label(text = color.type)
            

class SCENE_PT_nwn_basic_settings(bpy.types.Panel):
    bl_idname = "SCENE_PT_nwn_basic_settings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "NWN Basic Model Settings"
    bl_context = "scene"
    
    def draw(self, context):
        box = self.layout.box()
        
        box.label(text="Basic model settings")
        box.prop(context.scene.nwn_props, "classification")
        box.prop(context.scene.nwn_props, "supermodel")
        box.prop(context.scene.nwn_props, "animationscale")
        box.prop_search(context.scene.nwn_props, "root_object_name", bpy.data, "objects")
        

class OBJECT_PT_nwn_animations(bpy.types.Panel):
    bl_idname = "OBJECT_PT_nwn_animations"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "NWN Animation tools"
    bl_context = "scene"
    
    def draw(self, context):
        layout = self.layout
        ### animation settings ###
        box = layout.box()
        
        box.label(text="Animations")
        
        anim_props = context.scene.nwn_props.animation_props
        
        row = box.row()
        col = row.column()

        col.template_list(anim_props, "animations",
                          anim_props, "animation_index",
                          rows=3)
        
        col = row.column(align=True)
        col.operator("scene.add_nwn_anim", icon='ZOOMIN', text="")
        col.operator("scene.remove_nwn_anim", icon='ZOOMOUT', text="")
        
        if anim_props.animations:
            index = anim_props.animation_index
            animation = anim_props.animations[index]
            
            
            box.row().operator("scene.nwn_anim_focus")
            anim_row = box.row()
            anim_row.prop(animation, "name")
            
            anim_row = box.row()
            start_marker = animation.get_start_marker()
            end_marker = animation.get_end_marker()
            anim_row.prop(start_marker, "frame", text="Start frame")
            anim_row.prop(end_marker, "frame", text="End frame")
            
            event_box = box.box()
            row = event_box.row()
            row.label(text="Events:")
            
            row = event_box.row()
            col = row.column()
            
            col.template_list(animation, "events",
                              animation, "event_index",
                              rows=3)
            
            col = row.column(align=True)
            col.operator("scene.add_nwn_anim_event", icon='ZOOMIN', text="")
            col.operator("scene.remove_nwn_anim_event", icon='ZOOMOUT', text="")
            
            if animation.events:
                event = animation.events[animation.event_index]
                
                row = event_box.row()
                row.prop(event, "type")
                row = event_box.row()
                row.prop(event, "time")
  
            
class OBJECT_PT_nwn_node_tools(bpy.types.Panel):
    bl_idname = "OBJECT_PT_nwn_tools"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "NWN Node tools"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        if context.object is not None:
            if obj.type.upper() in ['LAMP','MESH','EMPTY']:
                return True
            
        return False
     
    def draw(self, context):
        layout = self.layout

        obj = context.object
        
        row = layout.row()
        row.prop(obj.nwn_props, "is_nwn_object", text="Aurora Object")
        
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
            
            from . import borealis_basic_types
            
            if node_type == "danglymesh":
                box.label(text = "Dangly Vertex Group:")
                box.prop_search(obj.nwn_props, "danglymesh_vertexgroup" ,obj, "vertex_groups", text = "")
            
            #Compare all possible settings for the specific node_type with the ones 
            #loaded into blender
            col_flow = box.column_flow(columns=2)
            for prop in borealis_basic_types.GeometryNodeProperties.get_node_properties(node_type):
                if prop in bpy.types.BorealisNodeProps.properties and prop.show_in_gui:
                    col_flow.prop(obj.nwn_props.node_properties, prop.name)
            
