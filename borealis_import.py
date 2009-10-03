#!BPY
# -*- coding: latin-1 -*-
""" Registration info for Blender menus
Name:	'Bioware NWN, ASCII (.mdl)...'
Blender: 248
Group:   'Import'
Tip:	 'Import a Neverwinter Nights model'
"""

__author__ = 'Erik Ylipää'
__version__ = '0.1'
#__url__ = ["No url"]
__email__ = ["Erik Ylipää, erik.ylipaa:gmail*com"]
__bpydoc__ = """\

This is an import script for Bioware Neverwinter Nights ASCII models.

 Shortcuts:<br>
   Esc or Q: quit.<br>

 Supported:<br>
   Importing of most geometry nodes works well. Animations arn't implemented fully yet.

 Known issues:<br>
   Animations arn't supported yet
"""

import Blender
from Blender import Window, Scene, Object, Image, Mathutils, Ipo, Modifier, Armature, Constraint
from Blender.Mathutils import Vector, Quaternion, Euler
from aurora_link import *
try:
	from borealis_mdl_interface import *
except ImportError:
	from borealis.borealis_mdl_interface import *

try:
	from math import degrees, radians
except ImportError:
	def degrees(radian):
		return radian*57.2957795
	def radians(degrees):
		return degrees/57.2957795



class AuroraImporter():
	armature = None
	model = None
	aurabase = None
	scene = None
	filename = None
	nodes = []
	armature_object = None
	timeline_padding = 25
	
	def __init__(self, filename):
		self.filename = filename
		
		self.model = Model(filename)
		
		self.scene = Scene.GetCurrent()
		

		
		self.create_nodes()
		self.import_animations()
		Window.RedrawAll()

	
	def create_nodes(self):
		#first create all the geometry nodes and parent them
		for node in self.model.geometry.geometry_nodes:
			
			ob = None		
			
			##Node specific operations start
			
			if node.name == self.model.name:
				#Node is the aurabase node
				ob = Object.New('Empty', node.name)
				ob.drawSize = 0.01
				node.type = 'aurabase'
				self.aurabase = ob
				
				AuroraLink.make_aurora_node("aurabase", ob)
				AuroraLink.set_aurora_value('setsupermodel', self.model.supermodel, ob)
				AuroraLink.set_aurora_value('classification', self.model.classification, ob)
				AuroraLink.set_aurora_value('setanimationscale', self.model.setanimationscale, ob)

				
			elif node.type == "dummy":
				ob = Object.New('Empty', node.name)
				ob.drawSize = 0.01
	
			elif node.type == "emitter":
				ob = self.import_emitter(node)
	
			elif node.type == 'light':
				ob = self.import_light(node)
	
			elif node.type == "trimesh" or node.type == "danglymesh" or node.type == "skin" or node.type == "aabb":
				ob = self.import_mesh(node)
				
			else:
				print "Unknown node type: " + node.type
				continue
			
			##Node specific operations complete
			
			
			## Add a node_type property
			AuroraLink.set_aurora_value("node_type", node.type, ob)
			
			self.scene.objects.link(ob)
			self.nodes.append(ob)
			
			# parent the objects, perhaps this would be better to put in a seperate for loop
			parent = None
			
			if node.parent.lower() != "null":
					parent = Blender.Object.Get(node.parent)
					if parent:
						parent.makeParent([ob])
					else:
						print "Parent not found for node:", node.name
			
			#Assign the location
			if node.position:
				position = [float(p) for p in node.position.split()] #the position is a space delimited string, split it to get the positions as elements in a list
				p_loc = [0.0,0.0,0.0]
				if parent:
					p_loc = parent.getLocation('worldspace')
				location = [p_loc[i]+pos for i, pos in enumerate(position)]
				ob.setLocation(location[0], location[1], location[2])
			
		#go thourgh the list again, this time apply rotation
		#Not done above since rotation is dependent on all objects being correctly parented
		for node in self.model.geometry.geometry_nodes:
			try:
				ob = Blender.Object.Get(node.name)
			except ValueError:
				continue
			
			if node.orientation:
				
				
				#Rotation in .mdl file is in axis/angle format: [x, y, y, angle]
				#We use a blenders quaternion to do the conversions
				axis = [float(a) for a in node.orientation.split()[:3]]
				angle = float(node.orientation.split()[3])
				quaternion = Mathutils.Quaternion(axis, angle)
				euler = quaternion.toEuler()
				euler = [a for a in quaternion.toEuler()]
				ob.RotX = euler[0]
				ob.RotY = euler[1]
				ob.RotZ = euler[2]
				
				
			ob.setLocation(ob.getLocation()) # Without this, it doesn't seem to update its children
			ob.makeDisplayList()
 
			
	def import_light(self, node):
		"""
		Takes a nwn node-object as argument and creates a blender lamp based on the data
		"""
		lamp = Blender.Lamp.New('Lamp', node.name)
		lamp.R, lamp.G, lamp.B = [float(c) for c in node.color.split()]
		lamp.dist = float(node.radius)
		
		ob = Object.New('Lamp', node.name)
		ob.link(lamp)

		# light specific properties
		for (property, value) in node.properties.items():
			if property not in NodeProperties.blender_handled:
				if value:
					AuroraLink.set_aurora_value("light/" + property.lower(), value, ob)
		return ob
		
	def import_emitter(self, node):
		scene = Scene.GetCurrent()
		render_context = scene.getRenderingContext()
		
		fps = render_context.fps
		
		#create a triangle to act as the emitter face
		mesh = Blender.Mesh.New(node.name)
		face = [[0.01,0,0],
				[-0.01,0,0],
				[0,0,0.01]]
		mesh.verts.extend(face)
		mesh.faces.extend([v.index for v in mesh.verts])
		
		ob = Object.New('Mesh', node.name)
		ob.link(mesh)
#		ob.newParticleSystem()
#		emitter = ob.getParticleSystems()[0]
#		
		mat = Blender.Material.New(node.name)
		mat_ipo = Blender.Ipo.New('Material', node.name)
		mat.setIpo(mat_ipo)
		
		mesh.materials += [mat]
		
		image = None
		texture = node.texture
		if texture != 'null':
			#construct the image filename
			imagefname = texture + ".tga"
			#create a full path to the file based on where the model file was loaded from
			image_url = Blender.sys.join(Blender.sys.dirname(self.filename), imagefname)
			
			try:
				#first see if the image is already loaded into blender
				image=Image.Get(texture)
			except NameError:
				try:
					#try loading the image
					image=Image.Load(image_url)
					image.setName(texture)
				except IOError:
					image = Image.New(texture, 512, 512, 32)
					print "Emitter texture %s not found, creating empty image" % (image_url)
				
		
		if image:
			tex = Blender.Texture.New("texture")
			tex.setType('Image')
			tex.setImage(image)
			mat.setTexture(0,tex)
#	
#		if node.colorstart:
#			mat.rgbCol = [float(f) for f in node.colorstart]
#			red = green = blue = None
#			try:
#				red = mat_ipo.addCurve('R')
#			except ValueError:
#				red = mat_ipo[Blender.Ipo.MA_R]
#			if red:
#				red.append((0, float(node.colorstart[0])))
#			try:
#				green = mat_ipo.addCurve('G')
#			except ValueError:
#				green = mat_ipo[Blender.Ipo.MA_G]
#			if green:
#				green.append((0, float(node.colorstart[1])))
#			try:
#				blue = mat_ipo.addCurve('B')
#			except ValueError:
#				blue = mat_ipo[Blender.Ipo.MA_B]
#			if blue:
#				blue.append((0, float(node.colorstart[2])))
#		
#		if node.colorend:
#			time = fps*float(node.lifeexp)
#			red = green = blue = None
#			try:
#				red = mat_ipo.addCurve('R')
#			except ValueError:
#				red = mat_ipo[Blender.Ipo.MA_R]
#			if red:
#				red.append((time, float(node.colorend[0])))
#			try:
#				green = mat_ipo.addCurve('G')
#			except ValueError:
#				green = mat_ipo[Blender.Ipo.MA_G]
#			if green:
#				green.append((time, float(node.colorend[1])))
#			try:
#				blue = mat_ipo.addCurve('B')
#			except ValueError:
#				blue = mat_ipo[Blender.Ipo.MA_B]
#			if blue:
#				blue.append((time, float(node.colorend[2])))
#	
#		if node.alphastart:
#			alpha = None
#			try:
#				alpha = mat_ipo.addCurve('Alpha')
#			except ValueError:
#				red = mat_ipo[Blender.Ipo.MA_ALPHA]
#			if red:
#				red.append((0, float(node.alphastart)))
#				
#		if node.alphaend:
#			time = fps*float(node.lifeexp)
#			alpha = None
#			try:
#				red = mat_ipo[Blender.Ipo.MA_ALPHA]
#			except ValueError:
#				alpha = mat_ipo.addCurve('Alpha')
#			if red:
#				red.append((time, float(node.alphaend)))		 
#			
#			
#		if node.alphastart:
#			mat.alpha = float(node.alphastart)
#		
#		if node.lifeexp and emitter:
#			
#			# Blender can't handle lifeexpectancy shorter than one frame, if it is we
#			# force it to exactly one frame long
#			if float(node.lifeexp)*fps < 1.0:
#				emitter.lifetime = 1.0
#			else:
#				emitter.lifetime = float(node.lifeexp)*fps
	
		
		## Add all the emitter specific properties
		for (property, value) in node.properties.items():
			if property not in NodeProperties.blender_handled:
				if value:
					AuroraLink.set_aurora_value("emitter/" + property.lower(), value, ob)
					
		return ob
	
	def load_bitmap(self, imagename):
		image = None
		bitmap = imagename
		if bitmap != 'null':
			#construct the image filename
			imagefname = bitmap + ".tga"
			#create a full path to the file based on where the model file was loaded from
			image_url = Blender.sys.join(Blender.sys.dirname(self.filename), imagefname)
			
			try:
				#first see if the image is already loaded into blender
				image=Image.Get(bitmap)
			except NameError:
				try:
					#try loading the image
					image=Image.Load(image_url)
					image.setName(bitmap)
				except IOError:
					image = Image.New(bitmap, 512, 512, 32)
					print "Image %s not found, creating empty image" % (image_url)
		
		return image
		
	def import_mesh(self, node):
		mesh = Blender.Mesh.New(node.name)
		image = None
		
		if node.bitmap:
			bitmap_name = node.bitmap.lower()
			image = self.load_bitmap(bitmap_name)

		if image:
			mesh.addUVLayer(bitmap_name)

		

		#construct the vertices for the mesh
		verts = []
		if node.properties['verts']:
			for vert in node.properties['verts']:
				verts.append([float(vert[0]), float(vert[1]), float(vert[2])])
		
		tverts = []
		if node.tverts:
			for tvert in node.tverts:
				tverts.append([float(tvert[0]), float(tvert[1]), float(tvert[2])])
		
		faces = []
		uvfaces = []
		material_id = []
		
		#the faces lines in .mdl files are in the format:
		#[v1] [v2] [v3] [smooth_group] [t1] [t2] [t3] [matid]
		if node.faces:
			for node_face in node.faces:
				faces.append([int(node_face[0]), int(node_face[1]), int(node_face[2])])
				if int(node_face[7]) not in material_id:
					#construct a list of all face groups
					material_id.append(int(node_face[7]))
				#creates a list with actual uv vertenode_face coordinates
				if tverts:
					#does a quick lookup from the tverts list for every tN value
					uvfaces.append([tverts[int(node_face[4])],tverts[int(node_face[5])],tverts[int(node_face[6])]])

		print node.name, material_id
	
						
		mesh.verts.extend(verts)
		mesh.faces.extend(faces,ignoreDups=True)
		
		#adding uv-coordinates to the faces
		#this probably isn't the best way of doing this, as it's asssuming the faces are in the right order
		if uvfaces:
			for i in range(len(mesh.faces)):
				#Face.uv expects a tuple of vectors
				uv = (Mathutils.Vector(uvfaces[i][0]),Mathutils.Vector(uvfaces[i][1]),Mathutils.Vector(uvfaces[i][2]))
				mesh.faces[i].image = image
				mesh.faces[i].uv = uv
		
		##Add material
		mat = Blender.Material.New(node.name)
		
		#parse the settings that can be applied to a blender material
		if node.diffuse:
			mat.rgbCol = [float(s) for s in node.diffuse.split()]
		if node.specular:
			mat.specCol = [float(s) for s in node.specular.split()]
		if node.alpha:
			mat.alpha = float(node.alpha)
			mat.setMode(mat.getMode()|Blender.Material.Modes['ZTRANSP'])
		
	
		#Should enable texture face on material if it has uv-layers
		if mesh.getUVLayerNames():
			mat.setMode(mat.getMode()|Blender.Material.Modes['TEXFACE'])
			texture = Blender.Texture.New(image.name + "_tex")
			texture.setType("Image")
			texture.setImage(image)
			mat.setTexture(0, texture, Blender.Texture.TexCo['UV'])
		mesh.materials += [mat]
		
		ob = Blender.Object.New('Mesh', node.name)
		ob.link(mesh)
		
		# mesh specific properties
		for (property, value) in node.properties.items():
			if property not in NodeProperties.blender_handled:
				if value:
					AuroraLink.set_aurora_value("mesh/" + property.lower(), value, ob)
					
					
		if node.type == 'danglymesh':
			##Take care of dangly mesh specifics
			#Create vertex group to use for the dangly constraints
			mesh.addVertGroup('dangly_constraints')
	 
			## this goes through the vertices and adds them one by one to the group 'dangly_constraints'
			## with weights from the models constraint values
			if node.constraints:
				for v in mesh.verts:
					constraint = 255 - int(node.constraints[v.index][0]) #a weight of 1 is completely solid when using softbody
					weight = float(constraint)/255.0
					mesh.assignVertsToGroup('dangly_constraints', [v.index], weight, Blender.Mesh.AssignModes.ADD)
	
		
		if node.type == 'skin':
			#walks through every line in the weigtsh matrix and split them into
			#two different matrices
			#should probably add some sanity checks here, right now we assume the list is
			#[bonename, weight, bonename, weight, ...]
			bones = [a[::2] for a in node.weights]
			weights = [a[1::2] for a in node.weights]
			
			#create a one-dimensional list from the 2D bones list
			vgroups = []
			for a in bones:
				for b in a:
					vgroups.append(b)
					
			#removes all duplicates in the vgroups list
			if vgroups:
				vgroups.sort()
				last = vgroups[-1]
				for i in range(len(vgroups) -2, -1, -1):
					if last == vgroups[i]:
						del vgroups[i]
					else:
						last = vgroups[i]
						
			#creates vertex groups from the list of unique bones, vgroups
			for group in vgroups:
				mesh.addVertGroup(group)
			
			## Iterate through all the verts in the mesh, and creates a touple-list with 
			## (bone,weight) as items
			if node.weights:
				for i, vert in enumerate(mesh.verts):
					weight_list = zip(bones[vert.index],weights[vert.index])
					for bone,weight in weight_list:
						mesh.assignVertsToGroup(bone,[vert.index], float(weight), Blender.Mesh.AssignModes.ADD)
	
		
		return ob

			
	def import_animations(self):
		#every animations data is expressed in a dict with the following format
		#animation_name : {nodes : { node_name : ipo_name }, 'transtime' : transtime, animroot : animroot, events : event_list}
		
		animations_dictionary = {}   #a dictionary containing all the animations for a specific aurabase
		frame_start = frame_end = 1
		render = self.scene.getRenderingContext()
		fps = render.fps

		
		#first create the neutral restposition
		#build the animation data
		rest_dict = {'events' : {}, 
					 'transtime' : 0, 
					 'animroot' : "null", 
					 'node_ipos' : {}
					 }
		
		#go through every node and add a keyframe for the current position and rotation
		for node in self.model.geometry.geometry_nodes:
			ob = Object.Get(node.name)
			#create a new ipo for this animation and turn on the fake user flag
			ipo = Ipo.New('Object', "rest" + '_' + node.name)
			ipo.fakeUser = True
			ob.setIpo(ipo)
			ob.insertIpoKey(Object.IpoKeyTypes.LOCROT)
			#add the node and ipo to the node_ipos dictionary
			rest_dict['node_ipos'].update({node.name : ipo.name})
			
		animations_dictionary.update({"rest" : rest_dict})	

		## done adding rest animation
		
		#parse all the animation nodes from the mdl file and create dictionaries based on their data
		for animation in self.model.animations:
			#build the animation data
			animation_dict = {'events' : dict(animation.events), 
							  'transtime' : animation.transtime, 
							  'animroot' : animation.animroot, 
							  'node_ipos' : {}
							  }

			for node in animation.nodes:
				
				
				ob = Object.Get(node.name)
				
				#create a new ipo for this animation and turn on the fake user flag
				ipo = Ipo.New('Object', animation.name + '_' + node.name)
				ipo.fakeUser = True
				ob.setIpo(ipo)
				
				#add the node and ipo to the node_ipos dictionary
				animation_dict['node_ipos'].update({node.name : ipo.name})
				
				if node.positionkey:
					loc_x = ipo.addCurve("LocX")
					loc_y = ipo.addCurve("LocY")
					loc_z = ipo.addCurve("LocZ")
					for key in node.positionkey:
						time = float(key[0]) * fps
						x = key[1]
						y = key[2]
						z = key[3]
						loc_x.append((time,x))
						loc_y.append((time,y))
						loc_z.append((time,z))
					loc_x.recalc()
					loc_y.recalc()
					loc_z.recalc()
			
				if node.orientationkey:
					rot_x = ipo.addCurve("RotX")
					rot_y = ipo.addCurve("RotY")
					rot_z = ipo.addCurve("RotZ")
					for key in node.orientationkey:
						time = float(key[0]) * fps
						axis = [float(f) for f in key[1:4]]
						angle = degrees(float(key[4]))
						quaternion = Mathutils.Quaternion(axis, angle)
						euler = quaternion.toEuler()
											
						#blender stores rotaions in 10ths of degrees
						rot_x.append((time,euler[0]/10.0))
						rot_y.append((time,euler[1]/10.0))
						rot_z.append((time,euler[2]/10.0))
						
					rot_x.recalc()
					rot_y.recalc()
					rot_z.recalc()

						
			animations_dictionary.update({animation.name : animation_dict})
		#print animations_dictionary
		self.aurabase.properties['aurora_properties']['animations'] = animations_dictionary
		AuroraLink.set_active_animation("rest", self.aurabase)
			

		
def filechooser_callback(filename):
	importer = AuroraImporter(filename)
				 
Window.FileSelector (filechooser_callback, "Open NWN Model", "/home/erik/Projekt/Neverwinter Nights/Models/*.mdl")
#filechooser_callback('/home/erik/src/Models/c_drggreen.mdl.txt')
