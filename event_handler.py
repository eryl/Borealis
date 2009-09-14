#!BPY
# -*- coding: utf-8 -*-

class EventHandler:
	"""
	Static class for managing events from and to blender widgets.
	"""
	event_list = [None]

	@staticmethod
	def add_widget(widget):
		"""
		Adds a widget to the widget list and returns the index (event) value for the widget.
		The widget can then be reached by calling EventHandler.get_widget with the triggered event.
		"""
		EventHandler.event_list.append(widget)

		#hopefully this returns the correct index value for the newly added widget, not very threadsafe
		return (len(EventHandler.event_list) - 1)

	@staticmethod
	def get_event_value(widget):
		"""
		Returns the event value for the first occurance of the widget in the widget list.
		"""
		#might be a problem if there's two exactly similar widget, but since every widget has a unique even it shouldnt be possible
		return EventHandler.event_list.index(widget)

	@staticmethod
	def get_widget(event):
		"""
		Returns the Widget instance that corresponds to the passed event value.
		"""
		print event
		return EventHandler.event_list[event]
