<<<<<<< HEAD
#!BPY
# -*- coding: utf-8 -*-


"""
# Name: 'Borealis Gui'
# Blender: 248
# Group: 'Misc'
# Tooltip: 'Tool-panel for editing Bioware Aurora Models from Neverwinter Nights'
"""

__author__ = 'Erik Ylipää'
__version__ = '0.3'
#__url__ = ["No url"]
__email__ = ["Erik Ylipää, erik.ylipaa:gmail*com"]
__bpydoc__ = """\
This script is a toolset for working with Bioware Aurora Models,
specifically for Neverwinter Nights

There are sets of panels which controls different aspects of the model

 Shortcuts:<br>
   Esc or Q: quit.<br>

 Supported:<br>
   Most controls for character type models

 Known issues:<br>
   
"""

from event_handler import *
import borealis_node_tools
import borealis_base_tools
from aurora_widgets import *
from borealis_export_gui import BorealisExportGui
				
class Gui:
	def __init__(self, caller=None):
		self.caller = caller
		self.panel = Panel("Root Gui Panel", 1,1)

		self.control_buttons = Panel("Control buttons", 1, 1, widget_size=(150, 20))
		self.panel.add(self.control_buttons)

		self.control_buttons.add(Button("Export", callback=self.run_export_gui))
		
		self.panel.add(borealis_base_tools.root_panel)
		self.panel.add(borealis_node_tools.root_panel)
		
		#activate first aurabase in the scene, if there is one
		bases = AuroraLink.get_aurabases()
		if bases:
			AuroraLink.set_aurora_base(bases[0])


	def gui(self):
		
		AuroraLink.update_active_object()
		self.panel.update()
		size = Blender.Window.GetAreaSize()
		self.panel.draw(0, 0, size[0], size[1])

	def run_gui(self):
		Draw.Register(self.gui, self.system_events, self.widget_events)

	def exit_gui(self):
		if self.caller:
			self.caller.run_gui()
		else:
			Draw.Exit()

	def run_export_gui(self,caller):
		export_gui = BorealisExportGui(self)
		export_gui.run_gui()
		
	def system_events(self, evt, val):
		Draw.Redraw(1)

		if evt == Draw.ESCKEY or evt == Draw.QKEY:
			stop = Draw.PupMenu("OK?%t|Stop script %x1")
			if stop == 1:
				print "Stopping NWN Tools Script"
				self.exit_gui()

	def widget_events(self, evt):

		Draw.Redraw()
		if evt > 0:
			EventHandler.get_widget(evt).handle_event() #EventHandler.get_widget returns the widget with the event value evt

if __name__ == "__main__":
	gui_object = Gui()

	Draw.Register(gui_object.gui, gui_object.system_events, gui_object.widget_events)
=======
'''
Created on 11 aug 2010

@author: erik
'''
import bpy

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
  
            
class BorealisTools(bpy.types.Panel):
    bl_idname = "OBJECT_PT_nwn_tools"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "NWN Model tools"
    bl_context = "object"
    
    @classmethod
    def register(cls):
        register()
    
    @classmethod
    def poll(cls, context):
        return (context.object is not None)
     
    def draw(self, context):
        layout = self.layout

        obj = context.object
        
        #only display nwn modeling tools if the selected object is relevant in nwn
        if obj.type.upper() not in ['LAMP','MESH','EMPTY']:
            row = layout.row()
            row.label(text="Not compatible object")
            row = layout.row()
            row.label(text="Select a lamp, mesh or empty object")
            
            return
        
        box = layout.box()
        
        box.label(text="Basic model settings")
        box.prop(context.scene.nwn_props, "classification")
        box.prop(context.scene.nwn_props, "supermodel")
        box.prop(context.scene.nwn_props, "animationscale")
        box.prop_search(context.scene.nwn_props, "root_object_name", bpy.data, "objects")
        
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

            anim_row = box.row()
            anim_row.prop(animation, "name")
            
            anim_row = box.row()
            start_marker = animation.get_start_marker()
            end_marker = animation.get_end_marker()
            anim_row.prop(start_marker, "frame", text="Start frame")
            anim_row.prop(end_marker, "frame", text="End frame")
            
        
        row = layout.row()
        row.prop(obj.nwn_props, "is_nwn_object", text="Toggle NWN object")
        
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
            elif node_type == "skin":
                box.template_list(obj.nwn_props, "skin_vertexgroups", obj.nwn_props, "skin_vg_index")

            
            #Compare all possible settings for the specific node_type with the ones 
            #loaded into blender
            col_flow = box.column_flow(columns=2)
            for prop in borealis_basic_types.GeometryNodeProperties.get_node_properties(node_type):
                if prop in bpy.types.BorealisNodeProps.properties:
                    col_flow.prop(obj.nwn_props.node_properties, prop.name)
            

def register():
    from . import properties
    bpy.types.Object.nwn_props = bpy.props.PointerProperty(type=properties.BorealisSettings)
    bpy.types.Scene.nwn_props = bpy.props.PointerProperty(type=properties.BorealisBasicProperties)
    
    
    #we set different node type enum lists, to make sure only node types relevant to the 
    #selected blender object are allowed
    bpy.types.Mesh.nwn_node_type = bpy.props.EnumProperty(items = [("trimesh","trimesh","trimesh"),
                                    ("danglymesh","danglymesh","danglymesh"),
                                    ("skin","skin","skin"),
                                    ("emitter","emitter","emitter"),
                                    ("aabb","aabb","aabb")],
                                   name = "Node Type",
                                   description = "The NWN Node type of this object")
    
    bpy.types.Lamp.nwn_node_type = bpy.props.EnumProperty(items = [("light","light","light")],
                                   name = "Node Type",
                                   description = "The NWN Node type of this object")

def unregister():
    pass
>>>>>>> 781f1c2a147e6bd3346e959433dec04030dbc26f
