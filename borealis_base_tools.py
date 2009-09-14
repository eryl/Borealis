#!BPY
# -*- coding: utf-8 -*-

import Blender
from event_handler import *
from aurora_widgets import *
from aurora_link import *
from copy import copy
import animation_panel

class ActiveAuraLabel(TextLabel):
	def update(self):
		if AuroraLink.aurora_base:
			self.name = "Active Aurabase: " + AuroraLink.aurora_base.name
		else:
			self.name = "Active Aurabase: No aurabase set"

		self.size = (Blender.Draw.GetStringWidth(self.name, "normalfix"), 20)


class AuAnimationScale(AuFloat):
	def update(self):
		base = AuroraLink.aurora_base
		if base:
			value = AuroraLink.get_aurora_value(self.aurora_property, base)
			if value:
				self.value = float(value)

			else:
				self.value = self.default_value

	def handle_event(self):
		self.value = self.blender_widget.val
		base = AuroraLink.aurora_base
		if base:
			AuroraLink.set_aurora_value(self.aurora_property, self.value, base)


class AuBasesMenu(MenuNamed):
	def __init__(self, name, size = None):
		Widget.__init__(self, name, size)
		self.value = 0
		self.default_value = 0
		self.current_item = 0
		#the call below might cause problems, the dict is non-deterministic as might AuroraLink.get_aurabases be.
		self.menuitems = dict([(ob.name, ob) for ob in AuroraLink.get_aurabases()])
		self.menukeys = self.menuitems.keys()

	def handle_event(self):
		self.current_item = self.blender_widget.val
		self.value = self.menukeys[self.current_item]
		au_object = self.menuitems[self.value]
		AuroraLink.set_aurora_base(au_object)

	def update(self):
		self.menuitems = dict([(ob.name, ob) for ob in AuroraLink.get_aurabases()])
		self.menukeys = self.menuitems.keys()



class AuSupermodelString(AuStringEntry):
	def update(self):
		base = AuroraLink.aurora_base
		if base:
			value = AuroraLink.get_aurora_value(self.aurora_property, base)
			if value:
				self.value = value
			else:
				self.value = self.default_value

	def handle_event(self):
		self.value = self.blender_widget.val
		base = AuroraLink.aurora_base
		if base:
			AuroraLink.set_aurora_value(self.aurora_property, self.value, base)

class AuClassificationMenu(AuMenuNamed):
	def handle_event(self):
		self.value = self.menuvalues[self.blender_widget.val]
		base = AuroraLink.aurora_base
		if base:
			AuroraLink.set_aurora_value(self.aurora_property, self.value, base)

	def update(self):
		base = AuroraLink.aurora_base
		if base:
			value = AuroraLink.get_aurora_value(self.aurora_property, base)
			if value:
				index = self.menuvalues.index(value)
				self.value = self.menukeys[index]
				self.current_item = index

			else:
				self.value = self.default_value
				self.current_item = self.menukeys.index(self.default_value)


	

widget_size = (150, 20)
root_panel = Panel("BaseTool Root", 1, 1, widget_size = widget_size, padding = (5, 20))

aurabase_panel = TogglePanel("Aurabase Panel", 2, 3, color=(1.0,0.3,0.3))
root_panel.add(aurabase_panel)
aurabase_panel.add(ActiveAuraLabel("Active Aurora Base: "))
aurabase_panel.add(AuBasesMenu("Aurora Bases"))
aurabase_panel.add(AuClassificationMenu("Classification:", "classification", menuitems = {"Character" : "character", "Tile" : "tile", "Effects" : "effects", "Item" : "item"}))
aurabase_panel.add(AuSupermodelString("Supermodel: ", "setsupermodel"))
aurabase_panel.add(AuAnimationScale("Animation Scale:", "setanimationscale"))

root_panel.add(animation_panel.root_panel)

