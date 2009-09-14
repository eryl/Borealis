#!BPY
# -*- coding: utf-8 -*-

import Blender
from borealis_mdl_interface import *

class AuroraAnimationTools:

	

class AuroraLink:
	active_object = None
	aurora_base = None

	@staticmethod
	def update_active_object():
		"""
		Updates the active object from the Blender Scene.
		"""
		AuroraLink.active_object = Blender.Scene.GetCurrent().objects.active

	@staticmethod
	def set_aurora_base(aurabase_ob):
		"""
		Makes the passed aurabase_ob the currently active Aurora Base Node.
		"""
		AuroraLink.aurora_base = aurabase_ob

	@staticmethod
	def get_aurabases():
		"""
		Returns a list with all aurabase nodes in the current Blender Scene.
		"""
		aurabases = []
		
		for ob in Blender.Scene.GetCurrent().objects:
			node_type = AuroraLink.get_aurora_value("node_type", ob)
			if node_type == "aurabase":
				aurabases.append(ob)

		return aurabases
		
	@staticmethod
	def get_aurora_value(name, ob = None):
		"""
		Returns the aurora property value identified by name from the object ob. If no
		object is supplied, it will return the value from the AuroraLink.active_object
		"""

		aurora_properties = AuroraLink.get_aurora_properties(ob)

		#parsed_name = name.split('/') #the name is split with a / for nested properties, ie "danglymesh/period"
		#path, key = parsed_name[:-1], parsed_name[-1:] #split the name in path and key
		
		if aurora_properties:
			for key,value in aurora_properties.iteritems():
				if key == name:
					value = aurora_properties[key]

					if key in NodeProperties.integer_properties:
						value = int(value)
					elif key in NodeProperties.float_properties:
						value = float(value)
					elif key in NodeProperties.bool_properties:
						value = int(value)

					elif key in NodeProperties.color_properties:
						value = [float(c) for c in value.split()]

					return value
				
		#no property with this value found, return none
		return None

	@staticmethod
	def set_aurora_value(name, value, ob = None):
		"""
		Sets a IDProperty value for the object ob. If no object is supplied, it will set the property
		on the AuroraLink.active_object.
		If the "aurora_properties" Property isn't set, this will create it.
		"""

		#this will be rewritten when the mdl inteface gets a facelift

		if type(value) == list:
			if name in NodeProperties.vector_properties or name in NodeProperties.color_properties:
				value = "".join([str(val) + " " for val in value])
			elif name in NodeProperties.matrix_properties:
				return
			else:
				value = "".join(value)
				
			if not ob:
				ob = AuroraLink.active_object
			
		aurora_properties = AuroraLink.get_aurora_properties(ob)
		print ob, aurora_properties
		if not aurora_properties:
			AuroraLink.make_aurora_node(ob = ob)
			aurora_properties = AuroraLink.get_aurora_properties(ob)
		print ob, aurora_properties, name, value
		aurora_properties[name] = value

	@staticmethod
	def is_aurora_object(ob = None):
		"""
		Is the supplied object an aurora object, that is; does it have the
		IDProperty "aurora_properties". If no object is supplied, it will
		test the AuroraLink.active_object.
		"""
		if not ob:
			ob = AuroraLink.active_object
		
		if ob:
			aurora_properties = AuroraLink.get_aurora_properties(ob)
			if aurora_properties:
				if "is_aurora_object" in aurora_properties:
					if aurora_properties["is_aurora_object"] == 0:
						return False
					else:
						return True
			else:
				return False
				
		return None #This condition shouldn't be reached, if it is somethings not right
	
	@staticmethod
	def make_aurora_node(node_type = "dummy", ob = None):
		"""
		Will convert the object ob to an aurora node of supplied node_type. Defaults to node_type = "dummy".
		If no ob i passed, AuroraLink.active_object will be used.
		"""
		if not ob:
			ob = AuroraLink.active_object
		
		if ob:
			if not "aurora_properties" in ob.properties: #will only make this a node if it isn't one already
				ob.properties["aurora_properties"] = {}
				ob.properties["aurora_properties"]["node_type"] = node_type
				ob.properties["aurora_properties"]["is_aurora_object"] = True
				
				

	@staticmethod
	def get_aurora_properties(ob = None):
		"""
		Returns the IDProperty group that contains all the Aurora Properties
		for the supplied Blender object. If no object is passed it will return
		the Properties for the currently active object.
		"""
		if not ob:
			ob = AuroraLink.active_object

		
		aurora_properties = None
		if ob:
			if "aurora_properties" in ob.properties:
				aurora_properties = ob.properties["aurora_properties"]

		return aurora_properties

