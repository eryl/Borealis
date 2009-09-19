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
