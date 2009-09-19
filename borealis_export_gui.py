#!BPY
# -*- coding: utf-8 -*-
""" Registration info for Blender menus
Name:	'Bioware NWN, ASCII (.mdl)...'
Blender: 248
Group:   'Export'
Tip:	 'Export a Neverwinter Nights model'
"""


__author__ = 'Erik Yliää'
__version__ = '0.1'
#__url__ = ["No url"]
__email__ = ["Erik Ylipää, erik.ylipaa:gmail*com"]
__bpydoc__ = """\

This is an export script for Bioware Neverwinter Nights ASCII models.
It will export the selected aurabase objects with all their child objects 
to the selected output directory.

 Shortcuts:<br>
   Esc or Q: quit.<br>

 Supported:<br>
   Exports most values correctly, as long as the porperties are named correctly. 
   Animations are not implemented yet.

 Known issues:<br>
   Animations are not supported yet
"""

import Blender
from Blender import Window, Scene, Object, Image, Mathutils, Ipo, Modifier, Armature, Constraint
from event_handler import *
from aurora_link import *
from aurora_widgets import *
from borealis_export import *
				
class BorealisExportGui:
	def __init__(self, caller = None):
		self.caller = caller #if this object is created within another gui, this is a reference to that gui
		self.panel = Panel("Root Export Panel", 1,1, widget_size = (200,20), padding=(5,20))
		self.bases_panel = Panel("Aurabases", 1, 1)
		self.panel.add(self.bases_panel)
		bases = AuroraLink.get_aurabases()
		self.export_bases = {}
		self.bases_panel.add(TextLabel("Select bases to export"))
		if not bases:
			self.bases_panel.add(TextLabel("No Aurabase objects in the scene"))
		#adds a toggle for every aurabase in the scene
		for base in bases:
			self.bases_panel.add(Toggle(base.name, callback=self.toggle_base_callback, callback_args=[base]))

		self.directory_browser = DirectoryBrowser("Output Directory: ", size=(300, 20))
		registry_dict = Blender.Registry.GetKey("Borealis Export", True)
		if registry_dict:
			if "out_dir" in registry_dict:
				self.directory_browser.value = registry_dict["out_dir"]
		
		self.panel.add(self.directory_browser)
		self.export_anims_toggle = Toggle("Export animations")
		self.panel.add(self.export_anims_toggle)

		self.execute_panel = Panel("Export Controls", 1 ,1, widget_size=(150,20))
		self.panel.add(self.execute_panel)
		
		self.execute_panel.add(Button("Export Selected", callback=self.export_callback))
		self.execute_panel.add(Button("Cancel", callback=self.cancel_callback))

	def run_gui(self):
		Draw.Register(self.gui, self.system_events, self.widget_events)

	def exit_gui(self):
		if self.caller:
			self.caller.run_gui()
		else:
			Draw.Exit()
		
	def export_callback(self, caller):
		#We should give some feedback to the user that export is actually proceeding
		print self.export_bases
		#save path for the export
		Blender.Registry.SetKey("Borealis Export", {"out_dir":self.directory_browser.value}, True)
		export_ob = AuroraExporter(self.export_bases.values(), self.directory_browser.value, self.export_anims_toggle)
		#exit after export is done
		self.exit_gui()

	def toggle_base_callback(self, caller, baseob):
		#if the toggle has been pressed, add the base to the export dictionary
		if caller.value == 1:
			self.export_bases[baseob.name] = baseob
		#if it's not active, remove it from the dictionary
		if caller.value == 0:
			if baseob.name in self.export_bases:
				del self.export_bases[baseob.name]

	def cancel_callback(self, caller):
		stop = Draw.PupMenu("Cancel export?%t|Yes%x1")
		if stop == 1:
			self.exit_gui()
			return
		
	def gui(self):

		self.panel.update()
		size = Blender.Window.GetAreaSize()
		self.panel.draw(0, 0, size[0], size[1])
		
	def system_events(self, evt, val):
		Draw.Redraw(1)

		if evt == Draw.ESCKEY or evt == Draw.QKEY:
			stop = Draw.PupMenu("OK?%t|Stop script %x1")
			if stop == 1:
				self.exit_gui()
				

	def widget_events(self, evt):

		Draw.Redraw()
		if evt > 0:
			EventHandler.get_widget(evt).handle_event() #EventHandler.get_widget returns the widget with the event value evt

if __name__ == "__main__":
	gui_object = BorealisExportGui()
	Draw.Register(gui_object.gui, gui_object.system_events, gui_object.widget_events)
