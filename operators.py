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
Created on 2 aug 2011

@author: erik
'''
import bpy

class SCENE_OT_remove_nwn_animation(bpy.types.Operator):
    bl_idname ="scene.remove_nwn_anim"
    bl_label = "Remove NWN animation"
    
    animation_name = bpy.props.StringProperty("Name of animation to remove")
    
    @classmethod
    def poll(cls, context):
        if context.scene.nwn_props.animation_props.animations:
            return True
        else:
            return False
        
    def execute(self, context):
        anim_props = context.scene.nwn_props.animation_props
        index = anim_props.animation_index
        scene = context.scene
        
        animation = anim_props.animations[index]
        m = animation.start_marker
        scene.timeline_markers.remove(m)
        m = animation.end_marker
        scene.timeline_markers.remove(m)
        anim_props.animations.remove(index)
        context.area.tag_redraw() #force the gui to redraw
        return {'FINISHED'}
    
    def invoke(self,context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)
    
class SCENE_OT_add_nwn_animation(bpy.types.Operator):
    bl_idname ="scene.add_nwn_anim"
    bl_label = "Add a new NWN animation"
    
    name = bpy.props.StringProperty("Animation name")
    length = bpy.props.IntProperty("Animation length (frames)", default=50, min=0)
    
    def execute(self, context):
        print("add animation")
        scene = context.scene
        #find the last marker to get a good place to insert the new animation
        last_frame = 0
        for marker in scene.timeline_markers:
            if marker.frame > last_frame:
                last_frame = marker.frame
        
        start_frame = last_frame + 10
        end_frame = start_frame + self.length
        
        anim_ob = scene.nwn_props.animation_props.animations.add()
        anim_ob.name = self.name
        
        marker = scene.timeline_markers.new(self.name + "_start")
        marker.frame = start_frame
        anim_ob.start_marker = marker
        
        marker = scene.timeline_markers.new(self.name + "_end")
        marker.frame = end_frame
        anim_ob.end_marker = marker
        
        context.area.tag_redraw() #force the gui to redraw
        
        return {'FINISHED'}


    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class SCENE_OT_remove_nwn_anim_event(bpy.types.Operator):
    bl_idname ="scene.remove_nwn_anim_event"
    bl_label = "Remove an event from a NWN animation"
    
    
    @classmethod
    def poll(cls, context):
        anim_props = context.scene.nwn_props.animation_props
        
        if anim_props.animations:
            index = anim_props.animation_index
            animation = anim_props.animations[index]
        
            if animation.events:
                return True
        
        return False
        
    def execute(self, context):
        anim_props = context.scene.nwn_props.animation_props
        index = anim_props.animation_index
        
        animation = anim_props.animations[index]
        
        event_index = animation.event_index
        animation.events.remove(event_index)
        context.area.tag_redraw() #force the gui to redraw
        return {'FINISHED'}
    
    def invoke(self,context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)
    
class SCENE_OT_add_nwn_anim_event(bpy.types.Operator):
    bl_idname ="scene.add_nwn_anim_event"
    bl_label = "Add a new event to a NWN animation"

    @classmethod
    def poll(cls, context):
        anim_props = context.scene.nwn_props.animation_props
        
        if anim_props.animations:
            return True
        
        return False
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self.event, "type")
        row = layout.row()
        row.prop(self.event, "time")
    
    def execute(self, context):
        self.event.update_name(None)
        
        context.area.tag_redraw() #force the gui to redraw
        
        return {'FINISHED'}


    def invoke(self, context, event):
        wm = context.window_manager
        
        anim_props = context.scene.nwn_props.animation_props
        index = anim_props.animation_index
        animation = anim_props.animations[index]
        self.event = animation.events.add()
        
        return wm.invoke_props_dialog(self)

class SCENE_OT_nwn_anim_focus(bpy.types.Operator):
    bl_idname ="scene.nwn_anim_focus"
    bl_label = "Focus on animation"
    bl_description = "Adjust scene start and end frame to the selected animation"
    
    @classmethod
    def poll(cls, context):
        if context.scene.nwn_props.animation_props.animations:
            return True
        else:
            return False
    
    def execute(self, context):
        scene = context.scene

        anim_props = context.scene.nwn_props.animation_props
        index = anim_props.animation_index
        
        animation = anim_props.animations[index]
        start_frame = animation.start_frame
        scene.frame_start = start_frame
        scene.frame_end = animation.end_frame
        scene.frame_current = start_frame
        scene.frame_start = start_frame # for some reason theres a bug if frame_start is set only once
        
        return {'FINISHED'}