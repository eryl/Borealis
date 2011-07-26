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
    def __init__(self, name):
        
        self.name = name
        try:
            from . import borealis_mdl_definitions
        except ValueError:
            import borealis_mdl_definitions
        props = borealis_mdl_definitions.GeometryNodeProperties.get_properties(self.type)
        self.properties = {}
        
        import copy
        
        for prop in props:
            self.properties[prop.name] = copy.copy(prop)
        
    def from_file(self, model_data):
        while model_data:
            current_line = model_data.pop(0)
        
            if "endnode" in current_line:
                break
            
            if not current_line: #skip empty lines
                continue
            
            if current_line[0] == "setfillumcolor":
                current_line[0] = "selfillumcolor"
            
            if current_line[0] in self.properties:
                self.properties[current_line[0]].read_value(current_line, model_data)
    
    def get_prop_value(self, property):
        if property not in self.properties:
            return None
        print("get_prop_value: %s, value: %s" % (property, self.properties[property].value))
        return self.properties[property].value
    
    def output_node(self):
        yield "node %s %s" % (self.type, self.name)
        for property in self.properties.values():
            if property.value_written:
                yield str(property)
        yield "endnode"
        
    def __str__(self):
        return "\n".join([line for line in self.output_node()])
            
class NodeDummy(Node):
    type = "dummy"

class NodeTrimesh(Node):
    type = "trimesh"

class NodeDanglymesh(Node):
    type = "danglymesh"

class NodeSkin(Node):
    type = "skin"

class NodeEmitter(Node):
    type = "emitter"

class NodeLight(Node):
    type = "light"


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
                node_type = current_line[1]
                node_name = current_line[2]
                node = None
                
                if node_type == "dummy":
                    node = AnimationNodeDummy(node_name)
                    
                elif node_type == "trimesh":
                    node = AnimationNodeTrimesh(node_name)
                    
                elif node_type == "danglymesh":
                    node = AnimationNodeDanglymesh(node_name)
                    
                elif node_type == "skin":
                    node = AnimationNodeSkin(node_name)
                    
                elif node_type == "light":
                    node = AnimationNodeLight(node_name)
                elif node_type == "emitter":
                    node = AnimationNodeEmitter(node_name)
                
                node.from_file(model_data)
                self.nodes.append(node)
                

    def __str__(self):
        out_string = "newanim %s %s\n" % (self.name, self.mdl_name)
        for node in self.nodes:
            out_string += str(node)
        out_string += "doneanim %s %s\n" % (self.name, self.mdl_name)
        return out_string

class AnimationNode(Node):
    def __init__(self, name):
        
        self.name = name
        
        try:
            from . import borealis_mdl_definitions
        except ValueError:
            import borealis_mdl_definitions
        props = borealis_mdl_definitions.AnimationNodeProperties.get_properties(self.type)
        self.properties = {}
        
        import copy
        
        for prop in props:
            self.properties[prop.name] = copy.copy(prop)
   
class AnimationNodeDummy(AnimationNode):
    type = "dummy"

class AnimationNodeTrimesh(AnimationNode):
    type = "trimesh"
    
class AnimationNodeDanglymesh(AnimationNode):
    type = "danglymesh"

class AnimationNodeSkin(AnimationNode):
    type = "skin"

class AnimationNodeEmitter(AnimationNode):
    type = "emitter"

class AnimationNodeLight(AnimationNode):
    type = "light"
    
if __name__ == "__main__":
    mdl = Model()
    mdl.from_file("c_allip.mdl")
    #mdl = Model("c_drggreen.mdl.txt")
    
    print(mdl)
    