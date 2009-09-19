#!BPY
# -*- coding: utf-8 -*-

from widgets import *
from aurora_link import *
import Blender

def set_aurora_value(caller, name):
	AuroraLink.set_aurora_value(name, caller.value)

def make_aurora(caller):
	AuroraLink.make_aurora_node(caller.value)

def get_aurora_value(caller, name):
	value = AuroraLink.get_aurora_value(name)
	if value:
		caller.value = value



class AuWidget(Widget):
	"""
	Extended widget specialized on handling Aurora values.
	"""
	def __init__(self, name, aurora_property, size = None, default_value = 0):
		"""
		This widget will handle the aurora property named as the string argument aurora_property.
		"""
		
		Widget.__init__(self, name, size)
		self.value = 0
		self.default_value = default_value
		self.aurora_property = aurora_property

	def update(self):
		value = AuroraLink.get_aurora_value(self.aurora_property)
		print self.name,  value
		if value:
			self.value = value
		else:
			self.value = self.default_value

	def handle_event(self):
		
		AuroraLink.set_aurora_value(self.aurora_property, self.value)

class AuButton(AuWidget, Button):
	pass

class AuToggle(AuWidget, Toggle):
	def draw(self, x, y, width, height):
		Toggle.draw(self, x, y, width, height)

	def handle_event(self):
		self.value = self.blender_widget.val
		AuWidget.handle_event(self)

	def update(self):
		AuWidget.update(self)
		self.value = int(self.value)

class AuInteger(AuWidget, Integer):
	def __init__(self, name, aurora_property, size = None, default_value = 0, min = 0, max = 10):
		AuWidget.__init__(self, name, aurora_property, size, default_value)
		self.value = int(self.value)
		self.min = int(min)
		self.max = int(max)
		
	def draw(self, x, y, width, height):
		Integer.draw(self, x, y, width, height)

	def handle_event(self):
		self.value = self.blender_widget.val
		AuWidget.handle_event(self)

	def update(self):
		AuWidget.update(self)
		self.value = int(self.value)
		
class AuFloat(AuWidget, Float):
	def __init__(self, name, aurora_property, size = None, default_value = 0, min = 0, max = 10):
		AuWidget.__init__(self, name, aurora_property, size, default_value)
		self.value = float(self.value)
		self.min = float(min)
		self.max = float(max)
		
	def draw(self, x, y, width, height):
		Float.draw(self, x, y, width, height)

	def handle_event(self):
		self.value = self.blender_widget.val
		AuWidget.handle_event(self)

	def update(self):
		AuWidget.update(self)
		self.value = float(self.value)
		
class AuStringEntry(AuWidget, StringEntry):
	def __init__(self, name, aurora_property, size = None):
		AuWidget.__init__(self, name, aurora_property, size)
		self.value = ""
		self.default_value = ""
		
	def draw(self, x, y, width, height):
		StringEntry.draw(self, x, y, width, height)

	def handle_event(self):
		self.value = self.blender_widget.val
		AuWidget.handle_event(self)
		
class AuMenu(AuWidget, Menu):
	def __init__(self, name, aurora_property, size = None, menuitems = {}, default_item = None):
		AuWidget.__init__(self, name, aurora_property, size)
		self.menuitems = menuitems # menuitems is a dictionary with "Title" : value, where "title" is the items displayed in the menu
		self.menukeys = self.menuitems.keys() #the list is constructed to be deterministic
		self.menuvalues = self.menuitems.values() #has the same order as the above
		self.current_item = 0

		if self.menuitems:
			self.value = self.menukeys[0]
			if default_item:
				self.default_value = default_item
			else:
				self.default_value = self.value

	def draw(self, x, y, width, height):
		Menu.draw(self, x, y, width, height)
		
	def handle_event(self):
		Menu.handle_event(self)
		AuWidget.handle_event(self)

	def update(self):
		value = AuroraLink.get_aurora_value(self.aurora_property)
		if value:
			index = self.menuvalues.index(value)
			self.value = self.menukeys[index]
			self.current_item = index
			
		else:
			self.value = self.default_value
			self.current_item = self.menukeys.index(self.default_value)
		
	
class AuMenuNamed(AuMenu, MenuNamed):
	def draw(self, x, y, width, height):
		MenuNamed.draw(self, x, y, width, height)
		
class AuTextLabel(AuWidget, TextLabel):
	pass
	
class AuColorPicker(AuWidget, ColorPicker):
	def __init__(self, name, aurora_property, size = None, color = [0.0,0.0,0.0], picker_rect = None):
		AuWidget.__init__(self, name, aurora_property, size)
		self.value = color
		self.default_value = self.value
		self.picker_rect = picker_rect
		
	def draw(self, x, y, width, height):
		ColorPicker.draw(self, x, y, width, height)
		
	def handle_event(self):
		self.value = self.blender_widget.val
		AuWidget.handle_event(self)
		
	def update(self):
		AuWidget.update(self)
		if type(self.value) == list:
			self.value = [float(c) for c in self.value]
		elif type(self.value) == str:
			self.value = [float(c) for c in self.value.split()]

	
class AuColorPickerNamed(AuColorPicker, ColorPickerNamed):
	def draw(self, x, y, width, height):
		ColorPickerNamed.draw(self, x, y, width, height)


class AuDynamicPanel(Panel):
	def __init__(self, name, columns, rows, aurora_property, widget_size = None, size = None, padding = (0,0), is_root = False, panel_dict = {}):
		"""
		Creates a new DynamicPanel 
		"""
		Panel.__init__(self, name, columns, rows, widget_size, size, padding, is_root)
		self.panel_dict = panel_dict #dictionary with values as keys and the panel to show for a specific key as values
		self.aurora_property = aurora_property
		self.current_panel = None
		if self.panel_dict:
			for panel_condition, panel in self.panel_dict.items():
				panel.make_parent(self)
		
	def update(self):
		value = AuroraLink.get_aurora_value(self.aurora_property)
		if value in self.panel_dict:
			self.current_panel = self.panel_dict[value]
			self.size = self.current_panel.size
			
		if self.current_panel:
			self.current_panel.update()

	def draw(self, x, y, width, height):
		if self.current_panel:
			self.current_panel.draw(x, y, width, height)
	
	def make_parent(self, parent):
		Panel.make_parent(self, parent)
		if self.panel_dict:
			for panel_condition, panel in self.panel_dict.items():
				panel.make_parent(self)
