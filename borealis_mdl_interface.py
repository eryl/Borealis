#!/usr/bin/python
#sorts nodes relative to their parents

def sort_nodes(node_list):
	tmp_list = node_list[:]
	sorted_list = []

	while tmp_list:
		for node in tmp_list:
			if node.parent.lower() == 'null':
				sorted_list.insert(0, node)
				tmp_list.remove(node)
			else:
				for n in sorted_list:
					if n.name == node.parent:
						index = sorted_list.index(n)
						sorted_list.insert(index+1, node)
						tmp_list.remove(node)
	
	  
	return sorted_list
			
line_count = 0

class NodeProperties:
	"""
	This class deals with knowing which properties are valid, what kind of value they hold,
	converting values from the mdl file to python values, and formatting the values
	"""
	
	common_properties = {'parent' : None
						 #,'children' : []
						 ,'position' : []  #The position in 3d space of this node.
						 ,'orientation' : [] #the node is rotated around the axis given in x,y,z, and orientation ammount in radians
						 ,'wirecolor' : []}  #This probably defines the color for the object's wireframe.}
	
	mesh_properties = {'ambient' : []
					   ,'diffuse' : []
					   ,'specular' : []
					   ,'shininess' : []
					   ,'shadow' : None
					   ,'bitmap' : None
					   ,'verts' : []
					   ,'faces' : []
					   ,'tverts' : []
					   ,'alpha' : None
					   ,'scale' : None
					   ,'selfillumcolor' : []
					   ,'setfillumcolor' : []
					   ,'rotatetexture' : None
					   ,'tilefade' : None
					   ,'transparencyhint' : None
					   ,'beaming' : None
					   ,'inheritcolor' : None
					   ,'center' : []
					   ,'render' : None
					   ,'colors' : []
					
						#Dangly properties
						,'displacement' : None
						,'period' : None
						,'tightness' : None
						,'constraints' : None
					
						#Skin properties
						,'weights' : []}
	

	
	emitter_properties = {'colorstart' : []
					   ,'colorend' : []
					   ,'alphastart' : None 
					   ,'alphaend' : None
					   ,'sizestart' : None
					   ,'sizeend' : None
					   ,'sizestart_y' : None
					   ,'sizeend_y' : None 
					   ,'framestart' : None 
					   ,'frameend' : None 
					   ,'birthrate' : None 
					   ,'spawntype' : None
					   ,'lifeexp' : None
					   ,'mass' : None 
					   ,'spread' : None 
					   ,'particlerot' : None 
					   ,'velocity' : None 
					   ,'randvel' : None 
					   ,'fps' : None
					   ,'random' : None
					   ,'inherit' : None
					   ,'inherit_local' : None
					   ,'inherit_part' : None
					   ,'inheritvel' : None
					   ,'xsize' :  None
					   ,'ysize' :  None
					   ,'bounce' :  None
					   ,'bounce_co' : None
					   ,'loop' : None
					   ,'update' :  None
					   ,'render' :  None #[Normal | linked | Motion_blur]  - Unknown. Probably controls how the particles are drawn in some way.
					   ,'blend' :  None  # [Normal | lighten]  - Unknown.
					   ,'update_sel' :  None
					   ,'render_sel' :  None
					   ,'blend_sel' :  None
					   ,'deadspace' :  None
					   ,'opacity' :  None
					   ,'blurlength' :  None 
					   ,'lightningdelay' :  None 
					   ,'lightningradius' :  None 
					   ,'lightningscale' :  None
					   ,'blastradius' :  None
					   ,'blastlength' : None
					   ,'twosidedtex' : None 
					   ,'p2p' : None 
					   ,'p2p_sel' : None 
					   ,'p2p_type' : None 
					   ,'p2p_bezier2' : None 
					   ,'p2p_bezier3' : None
					   ,'combinetime' : None 
					   ,'drag' : None 
					   ,'grav' : None 
					   ,'threshold' : None
					   ,'texture' : None
					   ,'xgrid' : None 
					   ,'ygrid' : None 
					   ,'affectedbywind' : None 
					   ,'m_istinted' : None 
					   ,'renderorder' : None 
					   ,'splat' : None }
	
	light_properties = {'color' : None		#The color of the light source.
						,'multiplier' : None #Unknown
						,'radius' : None		#Probably the range of the light.
						,'ambientonly' : None		#This controls if the light is only an ambient lightsource or if it is directional as well.
						,'isdynamic' : None	   #Unknown.
						,'affectdynamic' : None		#Unknown.
						,'lightpriority' : None		#Unknown. I'm not sure what this does,' but a reasonable guess would be it controls when the lightsource casts a shadow. We know that in NWN only the strongest lightsource in an area casts shadows,' this may be the value that determines that. Or it could be a flag of some kind.
						,'shadow' : None		#Probably determines if this light is capable of casting shadows.
						,'lensflares' : None			#Possibly causes the light source to produce a lens flare effect,' sounds cool anyway.
						,'flareradius' : None
						,'fadinglight' : None}		#Unknown. Might activate some kind of distance fall off for the light. Or it could do just about anything.				   
	
	animnode_properties = {'positionkey' : None  #The position in 3d space of this node.
						   ,'orientationkey' : None #the node is rotated around the axis given in x,y,z, and orientation ammount in radians
						   }
	
	animemit_properties = {'sizestartkey' : None
						   ,'sizeendkey' : None
						   ,'birthratekey' : None
						   ,'masskey' : None
						   ,'bouncekey' : None
						   ,'bounce_cokey' : None}


						   
	#has multiple values on a line
	vector_properties = ['position', 'orientation', 'mesh/wirecolor', 'mesh/ambient', 'mesh/diffuse', 'mesh/color',
						 'mesh/specular','mesh/selfillumcolor', 'center', 'emitter/colorstart', 'emitter/colorend']

	#has multiple values on multiple lines
	matrix_properties = ['mesh/verts' ,'mesh/faces', 'mesh/tverts', 'mesh/colors', 'mesh/weights', 'mesh/constraints', 'positionkey',
						 'orientationkey', 'sizestartkey', 'sizeendkey', 'birthratekey', 'masskey'
						 ,'bouncekey','bounce_cokey']
	
	#used by the blender helper tools   
	integer_properties = ['mesh/shininess', 'mesh/faces', 'mesh/tilefade', 'mesh/beaming', 'mesh/colors',
						  'constraints',"emitter/renderorder", "emitter/xsize", "emitter/ysize","emitter/birthrate",
						  "emitter/xgrid", "emitter/ygrid", "emitter/fps" ,"emitter/p2p_sel", "emitter/framestart",
						  "emitter/frameend", "emitter/p2p_bezier2", "emitter/p2p_bezier3","emitter/spawntype"]
						  
	float_properties = ['mesh/verts', 'orientation', 'position', 'mesh/tverts', 'mesh/alpha',
						'mesh/scale', 'center', 'mesh/displacement', 'mesh/period', 'mesh/tightness',
						"emitter/alphastart", "emitter/alphaend", "emitter/sizestart", "emitter/sizeend","emitter/lifeexp",
						"emitter/spread", "emitter/velocity", "emitter/randvel", "emitter/drag", "emitter/grav", "emitter/blurlength",
						"emitter/sizestart_y", "emitter/sizeend_y", "emitter/blastradius", "emitter/blastlength",
						"emitter/mass", "emitter/bounce_co", "emitter/lightningdelay", "emitter/lightningradius",
						"emitter/lightningscale","emitter/deadspace", "emitter/combinetime","emitter/particlerot",
						"emitter/threshold"]
						
	string_properties = ['parent', 'mesh/bitmap', "emitter/texture","emitter/update", "emitter/render",
						"emitter/blend"]
	
	color_properties = ['mesh/ambient', 'mesh/diffuse', 'mesh/specular', 'mesh/selfillumcolor',
						'mesh/setfillumcolor', 'mesh/color', "emitter/colorstart", "emitter/colorend"]
						
	bool_properties = ['mesh/shadow', 'mesh/rotatetexture', 'mesh/transparencyhint', 
					   'mesh/inheritcolor', 'mesh/render', "emitter/p2p", "emitter/affectedbywind",
					   "emitter/m_istinted","emitter/inherit_part", "emitter/inheritvel", "emitter/loop","emitter/twosidedtex", 
						"emitter/inherit","emitter/inherit_local", "emitter/bounce", "emitter/splat","emitter/random"]
						
	special_properties = ['weights']


	#properties which can be handled by blender data
	blender_handled = ['parent', 'position','orientation', 'bitmap','verts'
					   ,'faces','tverts','alpha','constraints','weights'
					   ,'diffuse','specular']


	def __getitem__(self, item):
		return self.properties[item]

	@staticmethod
	def get_properties(type):
		"""
		Constructs a dictionary with valid properties for the supplied node type.
		"""
		return_props = NodeProperties.common_properties.copy()
		
		if type.lower() == 'trimesh' or type.lower() == 'skin' or type.lower() == 'danglymesh':
			return_props.update(NodeProperties.mesh_properties.copy())
		elif type.lower() == 'emitter':
			return_props.update(NodeProperties.emitter_properties.copy())
		elif type.lower() == 'light':
			return_props.update(NodeProperties.emitter_properties.copy())
		elif type.lower() == 'animdummy':
			return_props.update(NodeProperties.animnode_properties.copy())
		elif type.lower() == 'animemitter':
			return_props.update(NodeProperties.emitter_properties.copy())
			return_props.update(NodeProperties.animnode_properties.copy())
			return_props.update(NodeProperties.animemit_properties.copy())
			
		elif type.lower() == 'animtrimesh':
			return_props.update(NodeProperties.animnode_properties.copy())
			return_props.update(NodeProperties.mesh_properties.copy())
			
			
		return return_props

		

	@staticmethod
	def extract(node_type, datastream):
		"""
		Extracts values from the datastream according to the kind of property
		"""
		property = datastream[0][0] #extract the first word on the line
		

		#construct the property name this class is expecting, common properties doesnt have prefixes
		if property in NodeProperties.common_properties:
			complex_property = property
		elif property in NodeProperties.mesh_properties and (node_type in ['trimesh', "skin", "danglymesh"]):
			complex_property = "mesh/" + property
		elif property in NodeProperties.emitter_properties and node_type == "emitter":
			complex_property = "emitter/" + property
		elif property in NodeProperties.light_properties and node_type == 'light':
			complex_property = "light/" + property
		else:
			complex_property = property

		global line_count
		
		#if the property is a matrix (eg verts and faces) parse it here
		if complex_property in NodeProperties.matrix_properties:
			
			matrix = []
			if len(datastream[0]) == 1: #this matrix uses the endlist token instead of a number as a delimiter
				del datastream[0]
				line = datastream[0]
				line_count += 1
				
				while line[0] != 'endlist':
					matrix.append(line)
					del datastream[0]
					line = datastream[0]
					line_count += 1
					
			else:
				rows = int(datastream[0][1]) #how many rows does the matrix have? The value following the property
				
				#Since pyton counts from 0, add 1 to the rows delimiter
				for row in datastream[1:rows+1]:
					matrix.append(row)
					
				del datastream[0:rows] #leave one row for the read_node_data to delete, I'll have to figure out a better way to handle it
				line_count += rows
			return matrix	
		
		else:
			#extract values after the first token on the first line of the datastream and returns it as a list
			value = datastream[0][1:]
			return value
		
	@staticmethod
	def format(node_type, property, value):
		"""
		Returns a string formatted like nwn expects them in a .mdl ascii 
		"""

		if not value:
			return None

		
		#construct the property name this class is expecting, common properties doesnt have prefixes
		if property in NodeProperties.common_properties:
			complex_property = property
		elif property in NodeProperties.mesh_properties and (node_type in ['trimesh', "skin", "danglymesh"]):
			complex_property = "mesh/" + property
		elif property in NodeProperties.emitter_properties and node_type == "emitter":
			complex_property = "emitter/" + property
		elif property in NodeProperties.light_properties and node_type == 'light':
			complex_property = "light/" + property
		else:
			complex_property = property

		#print complex_property, value
		if complex_property in NodeProperties.matrix_properties: #complex_property contains a matrix of values
			list_str = " " + str(len(value))
			
			#if the matrix contains only float properties, format them to 9 digits
			if complex_property in NodeProperties.float_properties:
				for row in value:
					list_str += "\n	" + (" ".join("%.9g" % float(s) for s in row))
			
			#otherwise treat them as they are
			else:
				for row in value:
					list_str += "\n	" + " ".join(str(item) for item in row)
			return list_str
		
		elif complex_property in NodeProperties.vector_properties: #complex_property is a vector of values
			list_str = " ".join(str(item) for item in value)
			return list_str
		
		else:
			#return "".join([str(v) for v in value])
			return str(value)
	@staticmethod
	def blendformat(node_type, property, value):
		"""
		Returns value in a format that blender expects
		"""
		
		#first determine what kind of value we're dealing with
		if not value:
			return None


				#construct the property name this class is expecting, common properties doesnt have prefixes
		if property in NodeProperties.common_properties:
			complex_property = property
		elif property in NodeProperties.mesh_properties and (node_type in ['trimesh', "skin", "danglymesh"]):
			complex_property = "mesh/" + property
		elif property in NodeProperties.emitter_properties and node_type == "emitter":
			complex_property = "emitter/" + property
		elif property in NodeProperties.light_properties and node_type == 'light':
			complex_property = "light/" + property
		else:
			complex_property = property
		
		if complex_property in NodeProperties.string_properties:
			return "".join(value)
		elif complex_property in NodeProperties.vector_properties:
			return value
		elif complex_property in NodeProperties.matrix_properties:
			return value
		else:
			return "".join(value)
		
		
class Geometry:
	name = "null"
	geometry_nodes = []
	
	def __init__(self,datastream = None, name = "null"):
		self.name = name
		self.geometry_nodes = []
		
		## If datastream isn't passed, an empty geometry is created
		if not datastream:
			return
		global line_count
		line = datastream[0]
		while line[0] != "endmodelgeom":
			
			del datastream[0]
			line_count += 1
			try:
				first_token = line[0]	#reads first token from the line
				if first_token == 'node':
					self.geometry_nodes.append(Node(datastream, line[1], line[2]))
  
				else:
					pass
				
			except IndexError:   #there should be a simpler way to skip newlines?
				continue
			
			line = datastream[0]

	def __str__(self):
		#sort_nodes(self.geometry_nodes)
		return ("beginmodelgeom " + self.name +
				"\n%s" % ("\n".join(str(s) for s in self.geometry_nodes)) +
				"\nendmodelgeom " + self.name
				)

	def get_node(self,name):
		for node in self.geometry_nodes:
			if node.name == name:
				return node
		
		return None
		
class Model:
	name = ""

#This sets the parent model(s) from which this model inherits behavior. If there are no parent models the second parameter should be NULL. A child model inherits animations and geometry from it's parent and may override these properties with their own. 
#This should probably be a list of model names, can a model inherit from multiple parents?
	supermodel = "NULL"

#This defines the type of the model. Valid types we have seen are: Character, Tile, effects and Item. All of the creature models have been characters. The Tile and Item models (found in gidy_intlight.mdl and gidy_sun.mdl) are used for the environment in the viewer, but it's easy to imagine their possible uses in the actual game. The spells that have been released are classified as tiles. The effects class appears in fx_ref.mdl which is reffered to by the spells, but is not a parent of them.

	classification = "character"
	
#From the name I would guess this is a global control on the length of animations for this model. All of the character models use this setting, the tile and item (which aren't animated) do not.
	setanimationscale = None

	geometry = None
	animations = []
	
	aurabase_node = None

	def __init__(self, filename = None):
		self.animations = []
				
		if not filename:
			return
		
		mdl_file = open(filename, 'r')
		datastream = mdl_file.readlines()
		mdl_file.close()

		
		#make the whole file lowecase
		for i in range(len(datastream)):
			datastream[i] = datastream[i].lower()
			
		datastream = [line.rstrip().split() for line in datastream]
		#we traverse the file line by line, deleting lines as they are read. This method is used instead of a for-loop to allow the datastream to be passed to other functions
		line = datastream[0]
		global line_count
		while line[0] != "donemodel" and datastream:

			del datastream[0]
			
			line_count += 1
			try:
				first_token = line[0]	#reads first token from the line
				if first_token == 'newmodel':
					self.name = line[1]
		
				elif first_token == 'setsupermodel':
					self.supermodel = line[2]
		
				elif first_token == 'classification':
					self.classification = line[1]
					
				elif first_token == 'setanimationscale':
					self.setanimationscale = line[1]
		
				elif first_token == 'beginmodelgeom':
					geom_name = line[1]
					self.geometry = Geometry(datastream, geom_name)
				
				elif first_token == 'newanim':

					anim_name = line[1]
					model_name = line[2]
					self.animations.append(Animation(datastream, anim_name, model_name))
		
			except IndexError:   #should be a better way to skip newlines?
				continue

			try:
				#removes empty lines, kind of crude but works well
				while not datastream[0]:
					del datastream[0]
			except IndexError:
				continue
			
			line = datastream[0]
			
			#print "Are the animationnodes the same?:", self.animations[0].nodes is self.animations[1].nodes	


	def __str__(self):
		tmp_str = "newmodel " + self.name
		tmp_str += ("\nsetsupermodel " + self.name + " " + self.supermodel
					+ "\nclassification " + self.classification
					)
		if self.setanimationscale:
			tmp_str += "\nsetanimationscale " + str(self.setanimationscale)
		
		tmp_str += "\n" + str(self.geometry)
		tmp_str += "\n%s" % ("\n".join(str(s) for s in self.animations))
		
		tmp_str += "\ndonemodel " + self.name
		return tmp_str
	
	def getAnimation(self, name):
		for i in self.animations:
			if i.name == name:
				return i
			
		return None
	
	def get_geometry_node(self, name):
		return geometry.get_node(name)


class Node:

	name = "NULL"
	type = "dummy"

	properties = {}

			
	def __init__(self, datastream = None, type = 'dummy', name = 'null'):
		self.properties = NodeProperties.get_properties(type) #will return a dictionary containing valid values
		
		self.type = type
		self.name = name
		
		#not parsing a file, return with an empty node
		if not datastream:
			return
		
		self.read_node_data(datastream)
	 
	def __str__(self):
		tmp_str = "node " + self.type + " " + self.name
		for key in self.properties.keys():
			if self.properties[key]:
				tmp_str += "\n  " + key + " " + str(NodeProperties.format(self.type, key, self.properties[key]))
				#tmp_str += "\n  " + key + " " + str(self.properties[key])
		tmp_str += "\nendnode"		
		return tmp_str
	
	def __getattr__(self, attribute):
		if attribute in self.properties:
			return NodeProperties.blendformat(self.type, attribute, self.properties[attribute])
		
		else:
			raise AttributeError, attribute
		
	def read_node_data(self, datastream):
		"""
		Reads the node properties and adds them to the nodes properties
		"""
		
		line = datastream[0]
		global line_count
		while line[0] != "endnode":
			try:
				first_token = line[0]	#reads first token from the line
				
				#Checks if the property can be handled by this node, extract the values with the help of NodeProperties.extract
				if first_token in self.properties:
					#hack to take care of the selfillum/setfillum misspelling in the original bioware models
					if first_token == "setfillum":
						first_token == "selfillum"
						
					self.properties[first_token] = NodeProperties.extract(self.type, datastream)

					
					
				else:
					pass
					if first_token[0] != '#':
						print "Unknown keyword %s on line %i. I think i'm in a %s node" % (first_token, line_count, self.type)
			except IndexError:   #should be a better way to skip newlines?
				continue
			
			del datastream[0] 
			
			line_count += 1
			line = datastream[0]	



class AnimNode(Node):	
	
	def __init__(self, datastream = None, type = 'dummy', name = ''):
		self.properties = NodeProperties.get_properties("anim" + type) #will return a dictionary containing valid values

		self.type = type
		self.name = name
		
		#not parsing a file, return with an empty node
		if not datastream:
			return
		
		self.read_node_data(datastream)

	def __str__(self):
		tmp_str = "node " + self.type + " " + self.name
		for key in self.properties.keys():
			if self.properties[key]:
				tmp_str += "\n  " + key + " " + str(NodeProperties.format(self.type, key, self.properties[key]))

		tmp_str += "\nendnode"		
		return tmp_str
		

class Animation:
	name = None
	model_name = None
	nodes = None
	events = None #list of touples in (time, event_name) 
	length = None #[float]  - This is probably the ammount of time the animation will take to complete. This may be affected by the model property setanimationscale.
	
	transtime = None #[float] - This seems to have to do with the blending between animations. More testing needed.

	animroot = "NULL" #[node_name] - I'm really not sure about this one. It seems to refer to a node in the animation tree, possibly creating a reference to the root of the tree. However in the case of the bugbear the animroot is set to rootdummy which actually has a parent. This happens in a_ba as well. In deer it actually points to the root of the tree. This may be just a wierd artifact of the exporter though, in the cases where it does not point to the root of the tree, that root contains no information. Probably this tells NWN where the entry point of the animation tree is. 
	
	def __init__(self,datastream = None, name = '', model_name = ''):
		self.nodes = []
		self.events = []
		
		self.name = name
		self.model_name = model_name
		
		if not datastream:
			return
		
		line = datastream[0]

		while line[0] != 'doneanim':
			
			del datastream[0]
			global line_count
			line_count += 1
			
			try:
				first_token = line[0]	#reads first token from the line
				
				if first_token == 'length':
					self.length = line[1]
				elif first_token == 'transtime':
					self.transtime = line[1]
				elif first_token == 'animroot':
					self.animroot = line[1]
				elif first_token == 'event':
					time = line[1]
					event = line[2]
					self.events.append((time,event))
				
				elif first_token == 'node':
					self.nodes.append(AnimNode(datastream, line[1], line[2]))
   
					
					#if line[1] == 'dummy':
						#self.nodes.append(AnimDummyNode(datastream, line[1], line[2]))

					#elif line[1] == 'trimesh':
						#self.nodes.append(AnimTrimeshNode(datastream, line[1], line[2]))
					#elif line[1] == 'emitter':
						#self.nodes.append(AnimEmitterNode(datastream, line[1], line[2]))
					#elif line[1] == 'light':
						#self.nodes.append(AnimDummyNode(datastream, line[1], line[2]))
				
					#else:
						#print "Unknown node type:", line[1]
					

					
				else:
					pass
				
			except IndexError:   #there should be a simpler way to skip newlines?
				continue
			
			line = datastream[0]


	def __str__(self):
		#self.nodes = sort_nodes(self.nodes)
		event_string = ""
		for time, event in self.events:
			event_string += "\n  event %s %s" % (str(time), str(event))
		
		return ("newanim " + self.name + " " + self.model_name +
				"\n  length " + str(self.length) +
				"\n  transtime " + str(self.transtime) +
				"\n  animroot " + str(self.animroot) +
				event_string +
				#"\n%s" % ("\n".join(str(s) for s in self.events)) +
				"\n%s" % ("\n".join(str(s) for s in sort_nodes(self.nodes))) +
				"\ndoneanim " + self.name + " " + self.model_name
				)

		
def main():
	import sys
	filename = sys.argv[1]

	model = Model(filename)

	print str(model)
	return 0

if __name__ == '__main__': main() #if this script is called by itself, do a test-run
