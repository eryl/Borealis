#!BPY
# -*- coding: utf-8 -*-

import Blender
from borealis_mdl_interface import *

class AuroraLink:
	active_object = None
	aurora_base = None

	@staticmethod
	def get_all_children(parent):
		"""
		returns a list of all objects in the scene that has this as their root
		"""
		scene = Blender.Scene.GetCurrent()
		
		children = []
		for ob in scene.objects:
			if ob.parent == parent:
				children.append(ob)
				#recursive search for objects childed to this one
				children += AuroraLink.get_all_children(ob)
				
		return children

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
		
		if aurora_properties:
			for key,value in aurora_properties.iteritems():
				if key == name:
					value = aurora_properties[key]
					#print value
					##perform formatting according to value, should be passed to a method in NodeProperties instead.
					#if key in NodeProperties.integer_properties:
						#value = int(value)
					#elif key in NodeProperties.float_properties:
						#value = float(value)
					#elif key in NodeProperties.bool_properties:
						#value = int(value)

					#elif key in NodeProperties.color_properties:
						#value = [float(c) for c in value.split()]

					return value
				
		#no property with this value found, return none
		return None

	@staticmethod
	def set_aurora_value(name, value, ob = None):
		"""
		Sets a IDProperty value for the object ob. If no object is supplied, it will set the property
		on the AuroraLink.active_object.
		If the "aurora_properties" Property isn't set, this will create it. All values are stored in the IDProperty as
		strings, it's up to the user to know what to do with it.
		"""
		

		if type(value) in [list, tuple]: #formats sequences as "element element element "
			if name in NodeProperties.vector_properties or name in NodeProperties.color_properties:
				value = "".join([str(val) + " " for val in value])
			elif name in NodeProperties.matrix_properties:
				return
			else:
				value = "".join(value)
				
		if not ob:
			ob = AuroraLink.active_object
			
		if ob:
			aurora_properties = AuroraLink.get_aurora_properties(ob)

			if not aurora_properties:
				AuroraLink.make_aurora_node(ob = ob)
				aurora_properties = AuroraLink.get_aurora_properties(ob)

			print ob, aurora_properties, name, value
			aurora_properties[name] = str(value)

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


	###Below are animation methods
	@staticmethod
	def add_animation(animation_name, ob = None):
		if not ob:
			ob = AuroraLink.aurora_base

		animation_dict = {'events' : {}, 
							'transtime' : 0.0, 
							'animroot' : "null", 
							'node_ipos' : {}
						}

		children = AuroraLink.get_all_children(ob)
		
		for child in children:
			ipo = Blender.Ipo.New('Object', animation_name + '_' + child.name)
			ipo.fakeUser = True
			
			#add the node and ipo to the node_ipos dictionary
			animation_dict['node_ipos'].update({child.name : ipo.name})

		props = AuroraLink.get_aurora_properties(ob)
		props["animations"][animation_name] = animation_dict

		
	@staticmethod
	def delete_animation(animation_name, ob = None):
		if not ob:
			ob = AuroraLink.aurora_base

		anim = AuroraLink.get_animation(animation_name)
		
		for node_name, ipo_name in anim["node_ipos"].iteritems():
			ipo = Blender.Ipo.Get(ipo_name)
			ipo.fakeUser = False

		animations = AuroraLink.get_animations_dict(ob)
		animations.pop(animation_name)

		#if the deleted animation is the active, set another one as active
		if AuroraLink.get_active_animation(ob) == animation_name:
			AuroraLink.set_active_animation(AuroraLink.get_animations_names(ob)[0], ob)

		
	@staticmethod
	def get_active_animation(ob = None):
		"""
		Returns the currently active animation for the aurabase ob, if
		ob isn't supplied defaults to the currently active aurabase.
		"""
		if not ob:
			ob = AuroraLink.aurora_base
			
		props = AuroraLink.get_aurora_properties(ob)
		if props:
			if "active_animation" in props:
				return props["active_animation"]

		return None

	

	@staticmethod
	def set_active_animation(anim_name, ob=None):
		"""
		Sets the animation with the name anim_name as the currently active
		animation on object ob. If no ob is supplied it defaults to the currently
		active aurabase.
		"""
		if not ob:
			ob = AuroraLink.aurora_base

		#first we look up the animation
		target_anim = AuroraLink.get_animation(anim_name, ob)
		if target_anim:
			AuroraLink.apply_animation(target_anim)
			AuroraLink.set_aurora_value("active_animation", anim_name, ob)
		
		
	@staticmethod
	def apply_animation(animation):
		"""
		parses an animation dictionary and sets the ipos on the blender objects
		accordingly.
		"""
		for node, ipo in animation["node_ipos"].iteritems():
			ob = Blender.Object.Get(node)
			i = Blender.Ipo.Get(ipo)
			ob.setIpo(i)
		
		
	@staticmethod
	def get_animation(anim_name, ob=None):
		"""
		returns the animation dict for the animation named anim_named for supplied blender object ob.
		"""
		if not ob:
			ob = AuroraLink.aurora_base
			
		anims = AuroraLink.get_animations_dict(ob)
		if anims:
			if anim_name in anims:
				return anims[anim_name]

		return None


	@staticmethod
	def get_animations_dict(ob = None):
		"""
		Returns the dictionary for all the animations for supplied object ob
		"""
		if not ob:
			ob = AuroraLink.aurora_base
			
		props = AuroraLink.get_aurora_properties(ob)
		if props:
			if "animations" in props:
				return props["animations"]

	@staticmethod
	def get_animations_names(ob = None):
		"""
		Returns a list with the names of all animations for supplied object ob
		"""
		if not ob:
			ob = AuroraLink.aurora_base
		
		return_list = []
		props = AuroraLink.get_aurora_properties(ob)
		if props:
			if "animations" in props:
				for name, animation_data in props["animations"].iteritems():
					return_list.append(name)

		print return_list
		return return_list

	@staticmethod
	def add_event(time, event_type, animation_name = None):
		if not animation_name:
			animation_name = AuroraLink.get_active_animation()

		animation = AuroraLink.get_animation(animation_name)
		animation["events"].update({str(time) : event_type})

	@staticmethod
	def delete_event(time, event_type, animation_name = None):
		if not animation_name:
			animation_name = AuroraLink.get_active_animation()

		animation = AuroraLink.get_animation(animation_name)
		if str(time) in animation["events"]:
			animation["events"].pop(str(time))		
