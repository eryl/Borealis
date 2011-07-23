#!/usr/bin/python3.1
'''
Created on 10 aug 2010

@author: erik
'''


class Model(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.name = ""
        self.supermodel = ""
        self.classification = ""
        self.setanimationscale = 1
   
        self.geometry = Geometry()
        self.animations = []
        
    
    def from_file(self, filename, ascii=True):
        if ascii:
            try:
                model_file = open(filename)
                
                
            except:
                pass
            
            else:
                model_data = model_file.readlines()
                model_file.close()
                
                #remove comments, keeping empty lines
                tmp_data = []
                
                for line in model_data:
                    comment_index = line.find('#')
                    if comment_index >= 0:
                        line = line[0:comment_index]
                    
                    tmp_data.append(line)
                    
                        
                model_data = tmp_data
                #done removing comments    
                
                #tokenizes and removes newlines
                model_data = [line.rstrip().split() for line in model_data]
                
                self.model_data = model_data
                
                line_count = 0
                
                while model_data:
                    current_line = model_data.pop(0)
                    line_count += 1
                    
                    if "donemodel" in current_line:
                        break
                    
                    if not current_line: #skip empty lines
                        continue

                    first_token = current_line[0].lower()
                    
                    if first_token == 'newmodel':
                        self.name = current_line[1]
        
                    elif first_token == 'setsupermodel':
                        self.supermodel = current_line[2]
            
                    elif first_token == 'classification':
                        self.classification = current_line[1]
                        
                    elif first_token == 'setanimationscale':
                        self.setanimationscale = current_line[1]
            
                    elif first_token == 'beginmodelgeom':
                        geom_name = current_line[1]
                        self.geometry.from_file(geom_name, model_data)
                    
                    elif first_token == 'newanim':
                        anim_name = current_line[1]
                        model_name = current_line[2]
                        new_anim = Animation(anim_name,model_name)
                        new_anim.from_file(model_data)
                        self.animations.append(new_anim)
                    
        else:
            print("Binary mdl-files not supported")
            
    def __str__(self):
        out_string = ""
        
        out_string += "newmodel %s\n" % self.name
        out_string += "setsupermodel %s %s\n" % (self.name, self.supermodel)
        out_string += "classification %s\n" % self.classification
        out_string += "setanimationscale %s\n" % self.setanimationscale
        
        out_string += str(self.geometry)
        
        out_string += "".join([str(animation) for animation in self.animations])
        
        out_string += "donemodel %s\n" % self.name
    
        return out_string

class Property:
    value_written = False
    
    def __init__(self, name, datatype=float, has_blender_eq=False):
        self.name = name
        self.datatype = datatype
        self.has_blender_eq = has_blender_eq
        
    def read_value(self, current_line, model_data):
        pass
    
    def __str__(self):
        return self.name
    
    
    
class ListProperty(Property):
    def __init__(self, name, datatype=float, has_blender_eq=False):
        self.value= []
        Property.__init__(self, name, datatype, has_blender_eq)
        
    def read_value(self, current_line, model_data):
        if len(current_line) < 2:
            pass
        else:
            lines = int(current_line[-1])
            while lines:
                line = model_data.pop(0)
                if not line: #skip empty lines
                    continue
                self.value.append([value for value in line])
                
                lines -= 1
        
        self.value_written = True
        
    def __str__(self):
        out_string = " "*2+"%s %i\n" % (self.name, len(self.value))
        for line in self.value:
            out_string += " "*4+ " ".join([str(value) for value in line]) + "\n"
        return out_string

class ValueProperty(Property):
    def __init__(self, name, datatype=float, has_blender_eq=False):
        self.value = []
        Property.__init__(self, name, datatype, has_blender_eq)

    def read_value(self, current_line, model_data):
        self.value = [value for value in current_line[1:]]
        self.value_written = True
        
    def __str__(self):
        out_string =" "*2+ "%s %s\n" % (self.name, " ".join([str(value) for value in self.value]))
        
        return out_string

### Geometry classes ### 

class Geometry:
    def __init__(self):
        self.name = ""
        self.nodes = []
    
    def from_file(self, name, model_data):
        self.name = name
        
        while model_data:
            current_line = model_data.pop(0)
            
            if "endmodelgeom" in current_line:
                break
            
            if not current_line: #skip empty lines
                current_line = model_data.pop(0)
                continue
            
            if current_line[0] == "node":
                node = None
                node_name = current_line[2]
                
                if current_line[1] == "dummy":
                    node = NodeDummy(node_name)
                    
                elif current_line[1] == "trimesh":
                    node = NodeTrimesh(node_name)
                    
                elif current_line[1] == "danglymesh":
                    node = NodeDanglymesh(node_name)
                    
                elif current_line[1] == "skin":
                    node = NodeSkin(node_name)
                    
                elif current_line[1] == "light":
                    node = NodeLight(node_name)
                elif current_line[1] == "emitter":
                    node = NodeEmitter(node_name)
                
                node.from_file(model_data)
                self.nodes.append(node)
            
            
            
    def __str__(self):
        out_string = "beginmodelgeom %s\n" % self.name
        for node in self.nodes:
            out_string += str(node)
        out_string += "endmodelgeom %s\n" % self.name
        return out_string
    

    
    
class Node:
    properties = []
    
    
    def __init__(self, name):
        self.name = name
        self.prop_dict = dict(zip([property.name for property in self.properties], self.properties))
        
        
    def from_file(self, model_data):
        while model_data:
            current_line = model_data.pop(0)
        
            if "endnode" in current_line:
                break
            
            if not current_line: #skip empty lines
                continue
            
            if current_line[0] == "setfillumcolor":
                current_line[0] = "selfillumcolor"
            
            if current_line[0] in self.prop_dict:
                self.prop_dict[current_line[0]].read_value(current_line, model_data)
    
    def get_prop_value(self, property):
        return self.prop_dict[property].value
    
    def __str__(self):
        out_string = "node %s %s\n" % (self.type, self.name)
        for property in self.properties:
            if property.value_written:
                out_string += str(property)
        out_string += "endnode\n"
        return out_string
            
class NodeDummy(Node):
    type = "dummy"
    def __init__(self,name):
        self.properties = [ValueProperty("parent",has_blender_eq=True),
                           ValueProperty("position",has_blender_eq=True),
                           ValueProperty("orientation",has_blender_eq=True),
                           ]
        Node.__init__(self,name)
    

class NodeTrimesh(Node):
    type = "trimesh"
    def __init__(self,name):
        self.properties = set([ValueProperty("parent",has_blender_eq=True),
                     ValueProperty("ambient"),
                     ValueProperty("diffuse"),
                     ValueProperty("specular"),
                     ValueProperty("shininess"),
                     ValueProperty("shadow"),
                     ValueProperty("bitmap"),
                     ListProperty("verts",has_blender_eq=True),
                     ListProperty("tverts",has_blender_eq=True),
                     ListProperty("faces",has_blender_eq=True),
                     ValueProperty("position",has_blender_eq=True),
                     ValueProperty("orientation",has_blender_eq=True),
                     ValueProperty("alpha"),
                     ValueProperty("scale"),
                     ValueProperty("selfillumcolor"),
                     ])
        Node.__init__(self,name)


class NodeDanglymesh(Node):
    type = "danglymesh"
    
    def __init__(self, name):
        self.properties = [ValueProperty("parent",has_blender_eq=True),
                      ValueProperty("ambient"),
                      ValueProperty("diffuse"),
                      ValueProperty("specular"),
                      ValueProperty("shininess"),
                      ValueProperty("shadow"),
                      ValueProperty("bitmap"),
                      ListProperty("verts",has_blender_eq=True),
                      ListProperty("tverts",has_blender_eq=True),
                      ListProperty("faces",has_blender_eq=True),
                      ValueProperty("displacement"),
                      ValueProperty("period"),
                      ValueProperty("tightness"),
                      ListProperty("constraints"),
                      ValueProperty("position",has_blender_eq=True),
                      ValueProperty("orientation",has_blender_eq=True),
                      ValueProperty("alpha"),
                      ValueProperty("scale"),
                      ValueProperty("selfillumcolor"),
                      ]
        Node.__init__(self,name)

    
    

class NodeSkin(Node):
    type = "skin"
    def __init__(self,name):
        self.properties = [ValueProperty("parent",has_blender_eq=True),
                      ValueProperty("ambient"),
                      ValueProperty("diffuse"),
                      ValueProperty("specular"),
                      ValueProperty("shininess"),
                      ValueProperty("shadow"),
                      ValueProperty("bitmap"),
                      ListProperty("verts",has_blender_eq=True),
                      ListProperty("tverts",has_blender_eq=True),
                      ListProperty("faces",has_blender_eq=True),
                      ListProperty("weights"),
                      ValueProperty("position",has_blender_eq=True),
                      ValueProperty("orientation",has_blender_eq=True),
                      ValueProperty("alpha"),
                      ValueProperty("scale"),
                      ValueProperty("selfillumcolor"),
                      ]
        Node.__init__(self,name)

class NodeEmitter(Node):
    type = "emitter"
    def __init__(self,name):
        self.properties = [ValueProperty("parent",has_blender_eq=True),
                           ValueProperty("position",has_blender_eq=True),
                           ValueProperty("orientation",has_blender_eq=True),
                           ]
        Node.__init__(self,name)

class NodeLight(Node):
    type = "light"
    def __init__(self,name):
        self.properties = [ValueProperty("parent",has_blender_eq=True),
                           ValueProperty("position",has_blender_eq=True),
                           ValueProperty("orientation",has_blender_eq=True),
                           ]
        Node.__init__(self,name)

### Done Geometry classes ###

### Animation classes ###

class Animation:
    def __init__(self, name, mdl_name):
        self.name = name
        self.mdl_name = mdl_name
        
        self.nodes = []

    def from_file(self, model_data):
        while model_data:
            current_line = model_data.pop(0)
            
            if "doneanim" in current_line:
                break
            
            if not current_line: #skip empty lines
                current_line = model_data.pop(0)
                continue
            
            if current_line[0] == "node":
                node_name = current_line[2]
                node = AnimationNodeDummy(node_name)
                node.from_file(model_data)
                    
                self.nodes.append(node)

    def __str__(self):
        out_string = "newanim %s %s\n" % (self.name, self.mdl_name)
        for node in self.nodes:
            out_string += str(node)
        out_string += "doneanim %s %s\n" % (self.name, self.mdl_name)
        return out_string

class AnimationNodeDummy(Node):
    type = "dummy"
    def __init__(self, name):
        self.properties = [ValueProperty("parent"),
                      ListProperty("positionkey"),
                      ListProperty("orientationkey"),
                      ]
        Node.__init__(self,name)
        
if __name__ == "__main__":
    mdl = Model()
    mdl.from_file("c_allip.mdl.txt")
    #mdl = Model("c_drggreen.mdl.txt")
    
    print(mdl)
    