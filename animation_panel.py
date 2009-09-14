#!BPY
# -*- coding: utf-8 -*-

from event_handler import *
from aurora_widgets import *
from aurora_link import *
from copy import copy




class ActiveAnimationsLabel(TextLabel):
	def update(self):
		animation = AuroraLink.get_active_animation()

		if animation:
			self.name = "Active Animation: " + animation
		else:
			self.name = "Active Aurabase: No active animation"

		self.size = (Blender.Draw.GetStringWidth(self.name, "normalfix"), 20)


class AuAnimationsMenu(MenuNamed):
	"""
	Specialized Menu for keeping track of animations.
	"""
	def __init__(self, name, size = None):
		Widget.__init__(self, name, size)
		self.value = AuroraLink.get_active_animation()
		self.default_value = self.value

		self.menukeys = AuroraLink.get_animations_names()
		
		if self.value and self.menukeys:
			self.current_item = self.menukeys.index(self.value)
		else:
			self.current_item = 0

	def handle_event(self):
		self.current_item = self.blender_widget.val
		self.value = self.menukeys[self.current_item]
		
		AuroraLink.set_active_animation(self.value)

	def update(self):
		self.menukeys = AuroraLink.get_animations_names()
		self.value = AuroraLink.get_active_animation()
		
		if self.value and self.menukeys:
			self.current_item = self.menukeys.index(self.value)
			
def add_anim_callback(caller):
	anim_name = Draw.PupStrInput("New Animation Name:", "", 32)
	if anim_name:
		AuroraLink.add_animation(anim_name)
	
def del_anim_callback(caller):
	active_anim = AuroraLink.get_active_animation()
	if active_anim:
		name = "Delete animation " + active_anim + "?|No%x0|Yes%x1"
		result = Draw.PupMenu(name)
		if result:
			AuroraLink.delete_animation(active_anim)
	else:
		Draw.PupMenu("Select a animation from the list first.%t|OK")
		
class AuEventMenu(MenuNamed):
	"""
	Specialized Menu for keeping track of events.
	"""
	def __init__(self, name, size = None):
		Widget.__init__(self, name, size)
		self.value = 0
		self.default_value = 0
		self.current_item = 0
		#the call below might cause problems, the dict is non-deterministic as might AuroraLink.get_aurabases be.
		self.menukeys = []
		
		self.current_item = 0

	def handle_event(self):
		self.current_item = self.blender_widget.val
		self.value = self.menukeys[self.current_item]
		print self.value
		

	def update(self):
		active_anim = AuroraLink.get_active_animation()
		if active_anim:
			anim_data = AuroraLink.get_animation(active_anim)
			events = anim_data["events"]
			event_list = []
			for time, event_tag in events.iteritems():
				event_list.append(time + " " + event_tag)
				
			self.menukeys = event_list

def add_event_callback(caller):
	active_anim = AuroraLink.get_active_animation()
	event_list = ["cast", "hit", "blur_start", "blur_end", "snd_footstep" , "snd_hitground", "draw_arrow", "draw_weapon"]
	if active_anim:
		at_time = Draw.PupFloatInput("Time of event", 0.5, 0.0, 30.0, 10, 2)
		name = "Event type:%t" + "".join(["|" + tag + "%x" + str(i) for i,tag in enumerate(event_list)])
		result = Draw.PupMenu(name)
		if result != -1:
			AuroraLink.add_event(at_time, event_list[result])
	else:
		Draw.PupMenu("Select a animation from the list first.%t|OK")

def del_event_callback(caller, event_menu):
	menu_item = event_menu.value
	if menu_item:
		time, tag = menu_item.split()
		result = Draw.PupMenu("Really delete event at time " + time + "?%t|No%x0|Yes%x1")
		if result == 1:
			AuroraLink.delete_event(time, tag)


### Start with panel definitions ###


root_panel = TogglePanel("Animation Tools", 1, 1)

### Basic animation settings ###
animation_header_panel = Panel("Animation Settings", 2, 1, padding=(5,5))
root_panel.add(animation_header_panel)

animation_header_panel.add(AuFloat("Transitiontime:", "transtime"))
animation_header_panel.add(AuStringEntry("Animation Root", "animroot"))

animation_panel = Panel("Animation Panel", 2, 1, padding = (5,5))
root_panel.add(animation_panel)
### sub-panel for handling events ###
event_panel = Panel("Animation Events", 1,1)
animation_panel.add(event_panel)

eventmenu = AuEventMenu("Events:")
event_panel.add(eventmenu)
event_panel.add(Button("Add New Event", callback=add_event_callback))
event_panel.add(Button("Delete Event", callback=del_event_callback, callback_args = [eventmenu]))

### Sub-panel for selecting animations ###
animation_selection_panel = Panel("Animation Selection", 1, 1)
animation_panel.add(animation_selection_panel)

animation_selection_panel.add(ActiveAnimationsLabel("Active Animation:"))
animations_menu = AuAnimationsMenu("Animations")
animation_selection_panel.add(animations_menu)

animation_selection_panel.add(Button("Add New Animation", callback=add_anim_callback))
animation_selection_panel.add(Button("Delete Selected Animation", callback=del_anim_callback))





