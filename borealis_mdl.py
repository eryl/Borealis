#!/usr/bin/python
'''
Created on 10 aug 2010

@author: erik
'''
TAB_WIDTH = 2

def compare(file1, file2):
    import os
    print("Comparing file: %s with %s" % (os.path.basename(file1), os.path.basename(file2)))
    mdl1 = Model()
    mdl2 = Model()
    
    mdl1.from_file(file1, True)
    mdl2.from_file(file2, True)
    
    #compare the geometry nodes
    for node1 in mdl1.geometry.nodes:
        for node2 in mdl2.geometry.nodes:
            if node1.name == node2.name:
                if node1.type != node2.type:
                    print("Differing node types; node %s\tmdl1: %s\tmdl2: %s" % 
                           (node1.name, node1.type, node2,type ))
                for name, prop in node1.properties.items():
                    if node2[name] != node1[name]:
                        print("Property %s differs\tmdl1: %s\tmdl2: %s" %
                              (name, str(node2[name]), str(node1[name])))
                break   
        
        
class Model(object):
    '''
    classdocs
    '''
    def __init__(self, name = ""):
        '''
        Constructor
        '''
        self.name = name
        self.supermodel = ""
        self.classification = ""
        self.setanimationscale = 1
   
        self.geometry = Geometry(self.name)
        self.animations = []
    
    def new_geometry_node(self, type, name):
       return self.geometry.new_node(type, name)
        
    
    def new_animation(self, name):
        animation = Animation(name, self.name)
        self.animations.append(animation)
        return animation
    
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
                        self.geometry.name = geom_name
                        self.geometry.from_file(model_data)
                    
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
        
        out_string += "\n".join([str(animation) for animation in self.animations])
        
        out_string += "\ndonemodel %s\n" % self.name
    
        return out_string

### Geometry classes ### 

class Geometry:
   
    
    def __init__(self, name):
        self.name = name
        self.nodes = []
        self.node_classes = {"dummy": NodeDummy, "trimesh" : NodeTrimesh,
                        "danglymesh" : NodeDanglymesh, "skin" : NodeSkin, 
                        "emitter" : NodeEmitter, "light" : NodeLight}
    
    def from_file(self, model_data):
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
    
    def new_node(self, type, name):
        node_class = self.node_classes[type]
        node = node_class(name)
        self.nodes.append(node)
        return node
    
    def output_geometry(self):
        yield "beginmodelgeom %s" % self.name
        for node in self.nodes:
            yield str(node)
        yield "doneanim %s " % self.name

    def __str__(self):
        return "\n".join([line for line in self.output_geometry()])

    
    
class Node:
    def __init__(self, name):
        
        self.name = name
        try:
            from . import borealis_basic_types
        except ValueError:
            import borealis_basic_types
        props = borealis_basic_types.GeometryNodeProperties.get_node_properties(self.type)
        self.properties = {}
        
        import copy
        
        for prop in props:
            self.properties[prop.name] = copy.copy(prop)
    
    def __getitem__(self, key):
        if key in self.properties:
            return self.properties[key].value
        else:
            raise KeyError
    
    def __setitem__(self, key, value):
        if key in self.properties:
            prop = self.properties[key]
            prop.update_value(value)
        else:
            raise KeyError
    
    def __iter__(self):
        return self.properties.__iter__()
    
    def keys(self):
        return self.properties.keys()
    
    def items(self):
        return self.properties.items()

    
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
        #print("get_prop_value: %s, value: %s" % (property, self.properties[property].value))
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
        self.length = 0
        self.transtime = 0
        self.animroot = ""
        self.nodes = []
        self.events = []
        self.node_classes = {"dummy": AnimationNodeDummy, "trimesh" : AnimationNodeTrimesh,
                        "danglymesh" : AnimationNodeDanglymesh, "skin" : AnimationNodeSkin, 
                        "emitter" : AnimationNodeEmitter, "light" : AnimationNodeLight}
    
    def new_node(self, type, name):
        node_class = self.node_classes[type]
        animation_node = node_class(name)
        self.nodes.append(animation_node)
        return animation_node

    def from_file(self, model_data):
        while model_data:
            current_line = model_data.pop(0)
            
            if "doneanim" in current_line:
                break
            
            if not current_line: #skip empty lines
                current_line = model_data.pop(0)
                continue
            
            if current_line[0] == "length":
                self.length = float(current_line[1])
            
            elif current_line[0] == "transtime":
                self.transtime = float(current_line[1])
                
            elif current_line[0] == "animroot":
                self.animroot = current_line[1]
                
            elif current_line[0] == "event":
                self.events.append((float(current_line[1]), current_line[2]))
                print(self.events[-1])
            
            elif current_line[0] == "node":
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
                
    def output_animation(self):
        yield "newanim %s %s" % (self.name, self.mdl_name)
        yield " "*TAB_WIDTH + "length %s" % str(self.length)
        yield " "*TAB_WIDTH + "transtime %s" % str(self.transtime)
        yield " "*TAB_WIDTH + "animroot %s" % self.animroot
        for time, event in self.events:
            yield " "*TAB_WIDTH + "event %.9g %s" % (time, event)
        for node in self.nodes:
            yield str(node)
        yield "doneanim %s %s" % (self.name, self.mdl_name)

    def __str__(self):
        return "\n".join([line for line in self.output_animation()])

class AnimationNode(Node):
    def __init__(self, name):
        
        self.name = name
        
        try:
            from . import borealis_basic_types
        except ValueError:
            import borealis_basic_types
        props = borealis_basic_types.AnimationNodeProperties.get_node_properties(self.type)
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
    #mdl = Model()
    #mdl.from_file("c_allip.mdl")
    #mdl = Model("c_drggreen.mdl.txt")
    
    #print(mdl)
    import sys
    argv = sys.argv
    #compare(*argv[1:3])
    compare("c_allip.mdl", "untitled.mdl")
    