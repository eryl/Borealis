#!BPY
# -*- coding: utf-8 -*-


"""
# Name: 'Borealis Gui Test'
# Blender: 248
# Group: 'Misc'
# Tooltip: 'Test program for the borealis gui components'
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
				
class Gui:
	def __init__(self):
		self.panel = Panel("Root Gui Panel", 1,1)
		
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
		
	def system_events(self, evt, val):
		Draw.Redraw(1)

		if evt == Draw.ESCKEY or evt == Draw.QKEY:
			stop = Draw.PupMenu("OK?%t|Stop script %x1")
			if stop == 1:
				print "Stopping NWN Tools Script"
				Draw.Exit()
				return

	def widget_events(self, evt):

		Draw.Redraw()
		if evt > 0:
			EventHandler.get_widget(evt).handle_event() #EventHandler.get_widget returns the widget with the event value evt

gui_object = Gui()

Draw.Register(gui_object.gui, gui_object.system_events, gui_object.widget_events)
