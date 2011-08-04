<<<<<<< HEAD
#!BPY
# -*- coding: latin-1 -*-

import Blender
from Blender import Window, Scene, Object, Image, Mathutils, Ipo, Modifier, Armature, Constraint
from aurora_link import *

import borealis_mdl_interface

try:
	from math import degrees, radians

	#if the system has a full python install, use it, otherwise use these hacks
except ImportError:
	def degrees(radian):
		return radian*57.2957795
	def radians(degrees):
		return degrees/57.2957795

#These are color values used to determine what the material ID for face should be
#by using their vertex colors. Not ideal, but blender only support 16 different material groups per mesh, nwn needs 21
material_colors = {
	1 : [189, 165, 112], #Dirt 
    2 : [0, 0, 0], #Obscuring 
    3 : [88, 228, 34], #Grass 
    4 : [255,223, 147], #Wood 
    5 : [127, 127, 127], #Stone
    6 : [100, 200, 255], #Water
    7 : [139, 20, 127], #No Walk 
    8 : [255,255,255], #Transparent
    9 : [255, 0, 255], #Carpet
    10 : [191, 191, 223], #Metal
    11 : [0, 255, 255], #Puddles
    12 : [123, 129, 0], #Swamp
    13 : [165, 0,0], #Mud
    14 : [0, 126,12], #Leaves
    15 : [255,0,0], #Lava
    16 : [80,174,168], #Bottomless Pit
    17 : [0,0,255], #Deep Water
    18 : [255,192,203], #Door
    19 : [230,230,250], #Snow
    20 : [255,165,0], #Sand
    21 : [255,255,0]  #Barebones
}

class AuroraExporter():
	models = {}
	scene = None
	bases = []
	current_base = None
	current_model = None
	
	def __init__(self, object_list, output_dir = None, export_animations = False):
		""""
		Exports the supplied list of Aurabase objects
		"""

		self.scene = Blender.Scene.GetCurrent()
		self.bases = object_list
		
		#the majority of the export code is executed in the export_aurabase function
		for aurabase in self.bases:
			self.export_aurabase(aurabase, export_animations)
		
		
		## If a output directory is passed, write data to file, otherwise to console
		if output_dir:
			for (name, model) in self.models.items():
				filename = Blender.sys.join(output_dir, name + '.mdl')
				#will not overwrite files, append number if the file exists
				counter = 1
				while Blender.sys.exists(filename) != 0:
					filename = Blender.sys.join(output_dir, '%s_%02i.mdl' % (name,counter))
					counter += 1
					
				mdl_file = open(filename, 'w')
				mdl_file.write(str(model))
		else:
			for (name, model) in self.models.items():
				print model

	def export_node(self, ob):
		"""
		Takes a blender mesh object and returns a nwn Node set to the correct type
		"""
		
		node_type = AuroraLink.get_aurora_value("node_type", ob)
		node = borealis_mdl_interface.Node(type = node_type)
		
		#handles converting all the properties to their respective nwn model values
		for property, value in AuroraLink.get_aurora_properties(ob).iteritems():
			property = property.split('/')[-1] #assign the last element to property

			##The value should only be assigned here if it isnt handled by native blender data and is in the nodes properties dictionary
			if property in node.properties:
				if len(value.split()) > 1: #if the value is a space delimited list, it's assigned as a list of strings
					node.properties[property] = value.split()
				else:
					node.properties[property] = value

		if node_type in ["trimesh", "danglymesh", "aabb", "skin"]:
			node.properties['verts'] = []
			node.properties['faces'] = []
			node.properties['tverts'] = []
			mesh_data = ob.getData(mesh = True)

			#first check for non-triangular faces
			mesh_data.sel = False
			non_tri_faces = []
			for face in mesh_data.faces:
				if len(face.verts) != 3:
					non_tri_faces.append(face)
					face.sel = 1
			#Here we should do a popup asking user what to do if there are non-triangular faces
			if non_tri_faces:
				answer = Blender.Draw.PupMenu("Mesh " + ob.name + " has non triangular faces.%t|Abort export%x1|Convert to triangles%x2")
				if answer == 1:
					raise RuntimeError, "Export aborted"
				else:
					mesh_data.quadToTriangle()
			
			#create verts
			for MVert in mesh_data.verts[:]:
				vertex = [a for a in MVert.co]
				node.properties['verts'].append(vertex)
			
			#create tverts, UV vertex is per face in blender (since we don't use sticky vertices)
			#seems like we're loosing tverts somewhere, probably here.
			uv_list = []
			if mesh_data.faceUV:
				image = None
				for face in mesh_data.faces:
					#all faces should have the same image in nwn
					if face.image != image and face.image:
						image = face.image
					for uv_vert in face.uv:
						if not uv_vert in uv_list:
							uv_list.append(uv_vert)
				
				print "image %s for mesh %s" % (image, mesh_data.name)
				if image:
					image_filename = image.getFilename()
					
					#strip path and extension from filename
					bitmap = Blender.sys.basename(image_filename)
					bitmap = Blender.sys.splitext(bitmap)[0]
					print "bitmap", bitmap
					node.properties['bitmap'] = bitmap
				
			#assign the list to the nodes.tverts, 2D so last element is always 0	
			for tverts in uv_list:
				node.properties['tverts'].append([tverts[0], tverts[1], 0.0])

			
			#creates faces
			for face in mesh_data.faces:
				face_verts = [v.index for v in face]
							
				#create indices from uv_list, since uv_vertices doesn't have any
				#only do this for faces that actually have uv set otherwise
				#assign values 0,0,0 to tverts index
				face_tverts = []
				if mesh_data.faceUV:
					for tvert in face.uv:
						index = uv_list.index(tvert)
						face_tverts.append(index)
				else:
					face_tverts = [0,0,0]

				mat_id = 1
				if node_type == 'aabb':
					#determine material id based on vertex colors
					col_r = col_g = col_b = 0
					for v_col in face.col:
						col_r += v_col.r
						col_g += v_col.g
						col_b += v_col.b

					#calculate the median color for this face	
					col_r /= len(face.col)
					col_g /= len(face.col)
					col_b /= len(face.col)

					print [col_r, col_g, col_b]
					global material_colors
					for key, value in material_colors.items():
						#allow for some tolerance since it's difficult to get the exact color
						#when doing vertex paint
						if (value[0] > col_r - 10 and value[0] < col_r + 10) and (value[1] > col_g - 10 and value[1] < col_g + 10) and (value[2] > col_b - 10 and value[2] < col_b + 10):
							mat_id = key
							break
						

						
				face_list = face_verts + [1] + face_tverts + [mat_id] #create the face-string
				node.properties['faces'].append(face_list)
		
			
			#this isn't the best way of doing this, in case the mesh has multiple materials
			if mesh_data.materials:
				material = mesh_data.materials[0]
				node.properties['diffuse'] = material.rgbCol
				node.properties['specular'] = material.specCol
				node.properties['alpha'] = material.alpha
				

			if node_type == 'danglymesh':
				if 'dangly_constraints' in mesh_data.getVertGroupNames():
					weight_verts = mesh_data.getVertsFromGroup('dangly_constraints', 1)
					constraints_list = []
							 
					for (v,w) in weight_verts:
						weight = (1.0 - w) * 255.0
						##blenders int doesnt round up correctl
						if weight % 1 > 0.5:
							constraints_list.append([int(weight)+1])
						else:
							constraints_list.append([int(weight)])
							
					node.properties['constraints'] = constraints_list
				else:
					answer = Draw.PupMenu("No dangly_constraints group in vertex groups. No constraints built. Expect problems.%t|Abort Export%x1|Continue with export%x2")
					if answer == 1:
						raise RuntimeError, "Export aborted due to undefined constraints vertex layer"
						
			if node_type == 'skin':
				#this creates the weights list based on vertex groups named after
				#the nodes that acts as bones
				
				#gets all the vertgroups
				bones_list = mesh_data.getVertGroupNames()
				#now sort through the bones_list, remove the elements which doesn't
				#correspond to nodes in the model
				if ob.name in bones_list:
					bones_list.remove(ob.name) #the weights shouldn't include the own node
				model_nodes = [bnode.name for bnode in AuroraLink.get_all_children(self.current_base)]
				for bone in bones_list:
					if bone not in model_nodes:
						bones_list.remove(bone)

				#first create a list with as many elements as vertices in the mesh, every element
				#an empty dictionary
				weight_list = [{} for v in mesh_data.verts]
				
				for group in bones_list:
					#getVertsFromGroup returns a list of touples: [(index, weight), ..] for every
					#vert in the group
					group_list = mesh_data.getVertsFromGroup(group, 1)
					for (index, weight) in group_list:
						#add the current group and its corresponding weight to the vert with the
						#correct index
						weight_list[index][group] = weight
									
				#normalize the list, the sum of the boneweights in every vert should be 1
				for index,vert in enumerate(weight_list):
					
					total_weight = 0
					for key,value in vert.items():
						if value == 0: #weights with a value of zero shouldnt be exported
							vert.pop(key)
						total_weight += float(value)
						
					#print "index[%i]:" % index, total_weight
					#if there isn't a weight assigned for this vert, one has to be assigned.
					#for now we select the vert and raise an error
					if not len(vert): 
						mesh_data.sel = False
						mesh_data.verts[index].sel = 1
						self.scene.objects.active = ob
						Blender.Window.EditMode(1)	
						raise RuntimeError, "Vertex weight not assigned, vertex has been selected"
					
					#calculate normalization ratio and normalize the values
					norm = 1.0 / total_weight
					for key, value in vert.items():
						vert[key] = value * norm
				
				#rebuilds the weight_list as a list of list instead of list of dicts
				#could need some cleaning up
				new_list = []
				for vert in weight_list:
					llist = []
					for key, value in vert.items():
						llist.extend([key,value])
					new_list.append(llist)
				
				node.properties['weights'] = new_list

			if node_type == "aabb":
				#this is converted from NwMax
				facelist =  mesh_data.faces
				aabb_data = []
				
				if len(mesh_data.faces)%2 == 1:
					print("Odd number of faces in AABB tree.  Expect problems.")
				
				self.build_aabb_tree_node(ob, facelist, 0, aabb_data)
				
				node.properties['aabb'] = aabb_data
				print aabb_data
				
			
		return node

	def build_aabb_tree_node(self, ob, facelist, level, aabb_data):
		"""
		Builds aabb nodes. This is a direct conversion from nwmax, since I
		don't clearly know whats being done yet.
		"""

		max_recursion = 100
	
		if not facelist:
			return
			
		if level > max_recursion:
		
			print("AABB Generation: Maximum recursion level reached.  Check for duplicate verticies and/or faces.")
			return
		
		#-- Calculate the size of the bounding box for the face list
		
		bot_left = Blender.Mathutils.Vector([100.0, 100.0, 100.0])
		top_right = Blender.Mathutils.Vector([-100.0, -100.0, -100.0])
		midpoint_average = Blender.Mathutils.Vector([100.0, 100.0, 100.0])
		
		for face in facelist:
			for vert in face.verts:
				#define the minimum axis aligned bounding box for the faces in facelist
				x,y,z = vert.co
				if x < bot_left.x:
					bot_left.x = x
				if y < bot_left.y:
					bot_left.y = y
				if z < bot_left.z:
					bot_left.z = z


				if x > top_right.x:
					top_right.x = x
				if y > top_right.y:
					top_right.y = y
				if z > top_right.z:
					top_right.z = z

		#Calc the mid-point average for the facelist
		midpoints_sum = Mathutils.Vector([0,0,0])
		for face in facelist:
			midpoints_sum += face.cent
		midpoint_average = Blender.Mathutils.Vector([co/len(facelist) for co in midpoints_sum])

		#-- calc the box position in 3d space. This basically the centre of the
		#-- axis aligned bounding box (aabb)
		box_pos = Blender.Mathutils.Vector([co/2 for co in (bot_left+top_right)])

		#-- postion the aabb in 3d space relative the node
		box_pos.z = bot_left.z
		#in coordsys parent ( box_pos += node.pos)
		#box_pos += ob.getLocation()

		#Create the string for the current box
		#the format nwn expects is 
		#aabb bottom_left.x bottom_left.x bottom_left.y top_right.z top_right.y top_right.z faceindex
		#if the box bounds a single face, its a leaf and the index corresponds to the face it bounds
		#if it bound more than one, faceindex is set to -1 to indicate its a parent box
		aabbLine = ""
		if level: #if we're not at level 0: add indent
			aabbLine += "       "
		aabbLine += level*"    " + "%f %f %f %f %f %f" % (bot_left.x, bot_left.y, bot_left.z, top_right.x, top_right.y, top_right.z)
		
		if len(facelist) == 1:
			#facelist is a single face, this is a leaf in the tree, recursion stops here
			aabbLine += " %i\n" % facelist[0].index

			#update aabb data array
			aabb_data.append(aabbLine)
			
		else:	#-- box is a parent as bounds multiple faces

			#-1 indicates that this is a bounding box with children
			aabbLine += " -1\n"
			
			aabb_data.append(aabbLine)
			
			bb_size = top_right - bot_left
			#-- Axis 1=x 2=y 3=z
			#-- Identify the longest axis for the bounding box
			axis = 1
			if (bb_size.y > bb_size.x): axis = 2
			if (bb_size.z > bb_size.y): axis = 3

			#-- Check exception case, where all points are coplanar with the axis-aligned split plane
			change_axis = True
			for face in facelist:
				p1 = face.cent
				if axis == 1:
					change_axis = change_axis and (p1.x == midpoint_average.x)
				elif axis == 2:
					change_axis = change_axis and (p1.y == midpoint_average.y)
				elif axis == 3:
					change_axis = change_axis and (p1.z == midpoint_average.z)
			
			if change_axis:
				axis += 1
				if axis > 3:
					axis = 1
			
			leftside = True
			good_split = False
			leftlist = []
			rightlist = []
			
			#-- work out the split for the tree: left and right branches
			axiscnt = 1
			while (not good_split):
				leftlist = []
				rightlist = []
				
				#-- split out the faces in facelist to the left and right tree
				#-- branches. The split is based on split axis value
				for face in facelist:
					p1 = face.cent

					if axis == 1:
						leftside = (p1.x < midpoint_average.x)
					elif axis == 2:
						leftside = (p1.y < midpoint_average.y)
					elif axis == 3:
						leftside = (p1.z < midpoint_average.z)

					if leftside:
						leftlist.append(face)
					else:
						rightlist.append(face)
				
				
				#-- This code tries to make a split that is not down one branch only.
				#-- This is probably causing more problems than it is worth.
				if leftlist and rightlist:
				#if there are faces in both lists; consider it a good split
					good_split = True

				else:
					#try another axis
					axiscnt += 1
					axis += 1
					if axis > 3: axis = 1

					if (axiscnt > 3):
						raise RuntimeError, "Unable to get a good aabb split, even after trying all axis"
						
						aabb_data.append("#ERROR: aabb split problem.")
						
						for f in facelist:
							aabb_data.append("#  face: "+ str(f))
							
						
						aabb_data.append("#ERROR-END")
						
						return
				

			#-- Recursive calls
			self.build_aabb_tree_node(ob, leftlist, level+1, aabb_data)
			self.build_aabb_tree_node(ob, rightlist, level+1, aabb_data)
			


	
	
	def export_aurabase(self, aurabase, export_animations = False):
		"""
		Constructs a nwn model based on the aurabase passed and its children
		"""
		
		#start by setting the model in the 'rest' animation
		AuroraLink.set_active_animation("rest", aurabase)
		
		#assign the base which is currently being exported
		self.current_base = aurabase
		
		#Creates a nwn_model and assignes the values from the aurabase properties
		model = borealis_mdl_interface.Model()
		
		model.name = aurabase.name
		self.current_model = model
		self.models.update({aurabase.name : model}) ##adds this model to the dictionary for exporting

		super = AuroraLink.get_aurora_value("setsupermodel", aurabase)
		if super:
			model.supermodel = super
		else: 
			model.supermodel = 'null'

		classification = AuroraLink.get_aurora_value("classification", aurabase)
		if classification:
			model.classification = classification
		else: 
			model.classification = 'character'

		setanimationscale = AuroraLink.get_aurora_value("setanimationscale", aurabase)
		if setanimationscale:
			model.setanimationscale = setanimationscale
		else: 
			model.setanimationscale = '1'
		
		geometry = Geometry() #Create a Geometry object to hold the geometry data
		model.geometry = geometry		#attach geometry to Model
		
		geometry.geometry_nodes = []  
		geometry.name = model.name
		
		#add the aurabase object to the geometry nodes
		auranode = borealis_mdl_interface.Node()
		auranode.name = aurabase.name
		auranode.properties['parent'] = 'null'
		auranode.type = 'dummy'
		geometry.geometry_nodes.append(auranode)
		
		#contruct a list with all the child objects
		children = AuroraLink.get_all_children(aurabase)
		
	 
		#Only export nodes which has the NWN_MODEL property set to 1 (True)
		export_nodes = []
		for ob in children:
			if AuroraLink.is_aurora_object(ob):
				export_nodes.append(ob)
		
		#This loop does the actual per node construction
		for ob in export_nodes:
			node_type = 'dummy'

			node_type = AuroraLink.get_aurora_value("node_type", ob)
			
			node = borealis_mdl_interface.Node(type=node_type)

			node = self.export_node(ob)
			
			##Done with node type-specific parsing, setting up general values
			
			if ob.parent:
				node.properties['parent'] = ob.parent.name
			else:
				node.properties['parent'] = 'null'
			node.name = ob.name
			
			#calculate the position for the node relative to the parent
			if ob.parent:
				child_loc = ob.getLocation()
				parent_loc = ob.parent.getLocation()
				node.properties['position'] = [child_loc[0]-parent_loc[0], child_loc[1]-parent_loc[1], child_loc[2]-parent_loc[2]]
			else:
				node.properties['position'] = list(ob.getLocation())
				
			#use blenders quaternion object to get axis/angle values
			#be careful of where radians is expected (Blenders API is non-
			#deterministic in this case)
			quaternion = ob.getEuler().toQuat()
			node.properties['orientation'] = [a for a in quaternion.axis] + [quaternion.angle]
				
			geometry.geometry_nodes.append(node)
			## Done with geometry exporting
			
		if export_animations:
			self.export_animations(aurabase)



	def export_animations(self, aurabase):
	
		render = self.scene.getRenderingContext()
		fps = render.fps
		
		if 'animations' in aurabase.properties['aurora_properties']:
			animation_dictionary = aurabase.properties['aurora_properties']['animations'].convert_to_pyobject()

			for animation, anim_data in animation_dictionary.items():
				#skip the rest animation
				if animation == 'rest':
					continue
					
				nwn_anim = Animation()
				nwn_anim.name = animation
				nwn_anim.transtime = anim_data['transtime']
				nwn_anim.animroot = anim_data['animroot']
				nwn_anim.events = anim_data['events'].items()
				nwn_anim.model_name = self.current_model.name
				
				length = 0
				#print "Animation data node  length:", len(anim_data['node_ipos'].keys())
				for node, ipo in anim_data['node_ipos'].iteritems():
					ipo = Ipo.Get(ipo)
					ob = Object.Get(node)
						#check total length of ipo, if it's greater than current self.length, update it
					
					for curve in ipo:
						#Assuming last entry in list is last bezTriple in time. Might be a bad assumption, but it seems to work well enough
						last_bez = curve.bezierPoints[-1]
						if last_bez.pt[0] > length * fps:
							length = last_bez.pt[0] / fps
					
					

					
					anim_node = AnimNode()
				
					node_type = AuroraLink.get_aurora_value("node_type", ob)
					
					if node_type == 'trimesh' or node_type == 'danglymesh' or node_type == 'skin':
						#in the animations the meshnodes seem to state trimesh, even if the
						#corresponding geometry node is skin or danglymesh
						anim_node.node_type = node_type
					
					
					anim_node.name = ob.name
					
					if ob.parent:
						anim_node.properties['parent'] = ob.parent.name
						anim_node.parent = ob.parent.name
					else:
						anim_node.parent = 'null'
						anim_node.properties['parent'] = 'null'
						
					#dictionary of dictionaries, {time : {rotx : value, roty : value, rotz : value}}
					rot_dict = {}
					loc_dict = {}
					for curve in ipo:
						for item in ['LocX', 'LocY', 'LocZ']:
							if curve.name == item:
								for point in curve.bezierPoints:
									if point.pt[0] in loc_dict:
										#if dict key already exist we append the point to that key (time)
										loc_dict[point.pt[0]][item] = point.pt[1]
									else:
										#otherwise it's added as a new key
										loc_dict[point.pt[0]] = {item : point.pt[1]}

						#Rotations are in tenths of degrees in the ipos
						for item in ['RotX', 'RotY', 'RotZ']:
							if curve.name == item:
								for point in curve.bezierPoints:
									if point.pt[0] in rot_dict:
										#if dict key already exist we append the point to that key (time)
										rot_dict[point.pt[0]][item] = point.pt[1]*10
									else:
										#otherwise it's added as a new key
										rot_dict[point.pt[0]] = {item : point.pt[1]*10}	 
						
					#we have to add checks to see that every keyframe has
					#all keyes. If you tweak curve points manually in the ipo editor
					#they easily get misaligned
					#we simply add the missing values
					for (time, keys) in rot_dict.items():
						if len(keys) != 3:
							#keyframe is missing some keys
							if not keys.has_key('RotX'):
								ipc = ipo[Ipo.OB_ROTX]
								keys['RotX'] = ipc[time]
							if not keys.has_key('RotY'):
								ipc = ipo[Ipo.OB_ROTY]
								keys['RotY'] = ipc[time]
							if not keys.has_key('RotZ'):
								ipc = ipo[Ipo.OB_ROTZ]
								keys['RotZ'] = ipc[time]
								
					for (time, keys) in loc_dict.items():
						if len(keys) != 3:
							#keyframe is missing some keys
							if not keys.has_key('LocX'):
								ipc = ipo[Ipo.OB_LOCX]
								keys['LocX'] = ipc[time]
							if not keys.has_key('LocY'):
								ipc = ipo[Ipo.OB_LOCY]
								keys['LocY'] = ipc[time]
							if not keys.has_key('LocZ'):
								ipc = ipo[Ipo.OB_LOCZ]
								keys['LocZ'] = ipc[time]				
					
					
					#create positionkeys and orientationkeys from the dicts
					if rot_dict:
						orientationkeys = []
						for (key,rotations) in rot_dict.items():
							euler = Mathutils.Euler(rotations['RotX'], rotations['RotY'], rotations['RotZ'])
							quaternion = euler.toQuat()
							orientation = [key/fps] + [axis for axis in quaternion.axis] + [radians(quaternion.angle)]
							orientationkeys.append(orientation)
						orientationkeys.sort()
						anim_node.properties['orientationkey'] = orientationkeys
						
					if loc_dict:
						positionkeys = []
						for (key, locations) in loc_dict.items():
							positionkeys.append([key/fps, locations['LocX'], locations['LocY'], locations['LocZ']])
						positionkeys.sort()
						anim_node.properties['positionkey'] = positionkeys
					nwn_anim.nodes.append(anim_node)
				
				nwn_anim.length = length
				self.current_model.animations.append(nwn_anim)	
	
=======
'''
Created on 11 aug 2010

@author: erik
'''

import os
import bpy
from bpy.props import CollectionProperty, StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper


class BorealisExport(bpy.types.Operator, ExportHelper):
    '''Export a single object as a stanford PLY with normals, colours and texture coordinates.'''
    bl_idname = "export_mesh.nwn_mdl"
    bl_label = "Export NWN Mdl"


    filepath = bpy.props.StringProperty(name="File Path",
                          description="File path used for exporting "
                                      "the active object to STL file",
                          maxlen=1024,
                          default="")
    filename_ext = ".mdl"
    filter_glob = StringProperty(default="*.mdl", options={'HIDDEN'})

    use_root_name = BoolProperty(name="Use Root Object Name", description="Use the name of the root object as the model name and filename like Neverwinter Nights expects, if false the filename will be used as the model name in the model file", default=True)
    export_animations = BoolProperty(name="Export Animations", description="Toggle whether animations should be exported or not", default=True) 
    
    
    @classmethod
    def poll(cls, context):
        ## Check to see that the root object exists
        
        return context.scene.nwn_props.root_object_name != None

    def execute(self, context):
        filepath = self.filepath
        filepath = bpy.path.ensure_ext(filepath, self.filename_ext)
        
        return export_nwn_mdl(context, **self.as_keywords(ignore=("check_existing", "filter_glob")))

from . import borealis_mdl
        

def export_nwn_mdl(context, **kwargs):
    scene_props = context.scene.nwn_props
    root_object = context.scene.objects[scene_props.root_object_name]
    
    if kwargs['use_root_name']:
        model_name = root_object.name
    else:
        filepath = kwargs['filepath']
        base_name = os.path.basename(kwargs['filepath'])
        model_name, ext = os.path.splitext(base_name)
        
    #poll should catch this
    if not root_object:
        return {'CANCELLED'}
    
    mdl = borealis_mdl.Model(model_name)
    mdl.classification = scene_props.classification
    mdl.supermodel = scene_props.supermodel
    mdl.setanimationscale =  scene_props.animationscale
    
    #this will act as an accumulator, containing the objects which has been exported
    exported_objects = []
    export_geometry(mdl, root_object, exported_objects)
    
    if kwargs['export_animations']:
        export_animations(context.scene, mdl, root_object, exported_objects)
    
#    if os.path.exists(kwargs['filepath']):
#        print("Path exists")
#    else:
    file = open(kwargs['filepath'], 'w')
    file.write(str(mdl))
    file.close()
    
    return {'FINISHED'}

def export_geometry(mdl, obj, exported_objects):
    node = mdl.new_geometry_node("dummy", obj.name)
    node['parent'] = "NULL"
    exported_objects.append(obj)
    for child in obj.children:
        export_node(mdl, child, obj.name, exported_objects)
    
        
def export_node(mdl, obj, parent, exported_objects):
    
    if obj.type in ['MESH', 'LIGHT']:
        node_type = obj.data.nwn_node_type
    else:
        node_type = obj.nwn_props.nwn_node_type
        
    node = mdl.new_geometry_node(node_type, obj.name)
    node['parent'] = parent
    
    from . import borealis_basic_types
    
    w, x, y, z = obj.rotation_axis_angle
    orientation = [x, y, z, w] 
    node['orientation'] = orientation
    
    node['position'] = obj.location
    
    for prop in borealis_basic_types.GeometryNodeProperties.get_node_properties(node_type):
        #only export the properties which are set in the properties group
        if prop.name in obj.nwn_props.node_properties and not prop.has_blender_eq:
            node[prop.name] = eval("obj.nwn_props.node_properties." + prop.name)

    if node_type in ["trimesh", "skin", "danglymesh"]:
        export_mesh(obj, node)

    exported_objects.append(obj)
    for child in obj.children:
        export_node(mdl, child, obj.name, exported_objects)

def export_mesh(obj, node):
    mesh = obj.data
    uv_faces = None
    image = None
        
    if mesh.uv_textures:
        uv_faces = mesh.uv_textures.active.data
        image = uv_faces[0].image
    
    #somehow we have to accomodate for the difference in how blender and nwn
    #handles the uv-coords. In nwn every uv vertice corresponds to a geometry vertice
    #in blender, every face has it's own uv-vertices
    
    vertices = [vert.co[:] for vert in mesh.vertices]
    node['verts'] = vertices
    
    smooth_group = 1
    faces = []
    uv_verts = []
    uv_verts_dict = {}
    
    uv_verts
    for i, face in enumerate(mesh.faces):
        v1, v2, v3 = face.vertices[:]
        
        if uv_faces:
            uv_co1, uv_co2, uv_co3 = uv_faces[i].uv1, uv_faces[i].uv2, uv_faces[i].uv3
            
            if uv_co1[0] not in uv_verts_dict:
                uv_verts_dict[uv_co1[0]] = {}
            if uv_co1[1] not in uv_verts_dict[uv_co1[0]]:
                uv1 = len(uv_verts)
                uv_verts.append(uv_co1[:])
                uv_verts_dict[uv_co1[0]][uv_co1[1]] = uv1
            else:
                uv1 = uv_verts_dict[uv_co1[0]][uv_co1[1]]
            
            
            if uv_co2[0] not in uv_verts_dict:
                uv_verts_dict[uv_co2[0]] = {}
            if uv_co2[1] not in uv_verts_dict[uv_co2[0]]:
                uv2 = len(uv_verts)
                uv_verts.append(uv_co2[:])
                uv_verts_dict[uv_co2[0]][uv_co2[1]] = uv2
            else:
                uv2 = uv_verts_dict[uv_co2[0]][uv_co2[1]]
            
            if uv_co3[0] not in uv_verts_dict:
                uv_verts_dict[uv_co3[0]] = {}
            if uv_co3[1] not in uv_verts_dict[uv_co3[0]]:
                uv3 = len(uv_verts)
                uv_verts.append(uv_co3[:])
                uv_verts_dict[uv_co3[0]][uv_co3[1]] = uv3
            else:
                uv3 = uv_verts_dict[uv_co3[0]][uv_co3[1]]
        else:
            uv1, uv2, uv3 = 0,0,0
        face_line = [v1, v2, v3, smooth_group, uv1, uv2, uv3, 1] #don't know what the last value is 
        
        faces.append(face_line)
    
    #add the third value to the tverts
    tverts = [[uv1, uv2, 0] for uv1, uv2 in uv_verts]
    node['tverts'] = tverts
    node['faces'] = faces
    
    if image:
        #use the filename for the texture as primary name
        #fall back on the name of the image 
        import os.path
        if os.path.exists(image.filepath):
            image_filename = os.path.basename(image.filepath)
            node['bitmap'], ext = os.path.splitext(image_filename)
        else:
            node['bitmap'] = image.name
    else:
        node['bitmap'] = "NULL"
        
    if node.type == "danglymesh":
        vertex_group_name = obj.nwn_props.danglymesh_vertexgroup
        if vertex_group_name:
            vertex_group = obj.vertex_groups[vertex_group_name]
            constraints = []
            for i in range(len(mesh.vertices)):
                constraint = vertex_group.weight(i) * 255
                constraint = 255 - int(constraint)
                constraints.append([constraint])
            node['constraints'] = constraints
    
    elif node.type == "skin":
        bones = []
        hooks = [mod for mod in obj.modifiers if mod.type == 'HOOK']
        
        
        bones_list = [{} for vert in mesh.vertices]
        
        for hook in hooks:
            if not (hook.vertex_group and hook.object):
                break
            
            vertex_group = obj.vertex_groups[hook.vertex_group]
            
            for i, bones in enumerate(bones_list):
                #there doesn't seem to be any way of checking whether a vertex i in a group
                # hence this try-clause 
                try:
                    if vertex_group.weight(i) > 0:
                        bones[hook.object.name] = vertex_group.weight(i)
                except RuntimeError:
                    pass  
        
        weights = []
        for bones in bones_list:
            total_weight = 0
            for weight in bones.values():
                total_weight += weight
            norm_co = 1/total_weight
            line = []
            for bone, weight in bones.items():
                line.append(bone)
                line.append("%.9g" % (weight*norm_co))
            weights.append(line)
        
        node["weights"] = weights
        

def export_animations(scene, mdl,root_object, exported_objects):
    animations = scene.nwn_props.animation_props.animations
    
    if not animations:
        return
    
    animation_data = build_animation_data(exported_objects, animations)
    
    for animation in animations:
        export_animation(animation_data[animation.name], scene, animation, mdl, root_object)

def export_animation(animation_data, scene, animation, mdl, root_object):
    fps = scene.render.fps
    nwn_anim = mdl.new_animation(animation.name)
    nwn_anim.animroot = root_object.name 
    
    start_frame = animation.start_frame
    end_frame = animation.end_frame
    
    nwn_anim.length = (end_frame - start_frame) / fps
    nwn_anim.transtime = animation.transtime
    
    for event in animation.events:
        nwn_anim.events.append((event.time, event.type))
    root_node = nwn_anim.new_node("dummy", root_object.name)
    root_node.parent = 'NULL'
    
    
    for child in root_object.children:
        export_animation_node(fps, animation_data, animation, nwn_anim, mdl, child, root_object.name)
        
def export_animation_node(fps, animation_data, animation, nwn_anim, mdl, obj, parent):
    if obj.type in ['MESH', 'LIGHT']:
        node_type = obj.data.nwn_node_type
    else:
        node_type = obj.nwn_props.nwn_node_type
    
    node = nwn_anim.new_node("dummy", obj.name)
    node['parent'] = parent
    start_frame = animation.start_frame
    if obj.name in animation_data['nodes']:
        if "location" in animation_data['nodes'][obj.name]:
            locations = sorted(animation_data['nodes'][obj.name]["location"].items())
            positionkeys = [[(time - start_frame) / fps, pos['x'], pos['y'], pos['z']] for time, pos in locations]
            node['positionkey'] = positionkeys
           
        if "rotation_axis_angle" in animation_data['nodes'][obj.name]:
            rotations = sorted(animation_data['nodes'][obj.name]["rotation_axis_angle"].items())
            orientationkey = [[(time - start_frame) / fps, ori['x'], ori['y'], ori['z'], ori['w']] for time, ori in rotations]
            node['orientationkey'] = orientationkey
            
    for child in obj.children:
        export_animation_node(fps, animation_data, animation, nwn_anim, mdl, child, obj.name)
    
def build_animation_data(objects, animations):
    """
    We create a complete dictionary of all objects and their animation data for simplified
    access later on
    """
    #We build a tree with all the animation n
    
    animation_list = [{"name" : animation.name, 
                       "start_frame" : animation.start_frame,
                       "end_frame" : animation.end_frame,
                       "nodes" : {}} for animation in animations]
    
    animation_list.sort(key=lambda x: x["start_frame"])
    
    #we build a mighty dictionary where the keyframe points are gathered depending on 
    #time, and not seperate channels for every object
    times = {}
    
    for object in objects:
        if not object.animation_data:
            continue
        for fcurve in object.animation_data.action.fcurves:
            attribute_name = "foo"
            if fcurve.data_path == "location":
                if fcurve.array_index == 0:
                    attribute_name = "x"
                elif fcurve.array_index == 1:
                    attribute_name = "y"
                elif fcurve.array_index == 2:
                    attribute_name = "z"    
            elif fcurve.data_path == "rotation_axis_angle":
                if fcurve.array_index == 0:
                    attribute_name = "w"
                elif fcurve.array_index == 1:
                    attribute_name = "x"
                elif fcurve.array_index == 2:
                    attribute_name = "y"   
                elif fcurve.array_index == 3:
                    attribute_name = "z"
            
            for point in fcurve.keyframe_points:
                if point.co[0] not in times:
                    times[point.co[0]] = {}
                if object.name not in times[point.co[0]]:
                    times[point.co[0]][object.name] = {}
                if fcurve.data_path not in times[point.co[0]][object.name]:
                    times[point.co[0]][object.name][fcurve.data_path] = {}
                times[point.co[0]][object.name][fcurve.data_path][attribute_name] = point.co[1]
    
    times_list = sorted(times.items())
    current_time = times_list.pop(0)
    for animation in animation_list:
        while(current_time[0] <= animation['end_frame']):    
            #if we find a time which has already 'passed', it isn't part of any animation
            #and is therefore discarded        
            if current_time[0] >= animation['start_frame']:
                for node, data_paths in current_time[1].items():
                    if node not in animation['nodes']:
                        animation['nodes'][node] = {} 
                    for path, attributes in data_paths.items():
                        if path not in animation['nodes'][node]:
                            animation['nodes'][node][path] = {}
                        animation['nodes'][node][path][current_time[0]] = attributes
            
            if not times_list:
                break;
            current_time = times_list.pop(0)        
                
        
    animation_dict = dict(zip([animation['name'] for animation in animation_list],
                               animation_list))
    
    return animation_dict 
>>>>>>> 781f1c2a147e6bd3346e959433dec04030dbc26f
