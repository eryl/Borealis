'''
Created on 11 aug 2010

@author: erik
'''
import bpy, mathutils

class BorealisSettings(bpy.types.PropertyGroup):
    """
    Properties specific for the nwn models, gets attached to all objects.
    """
    nwn_node_type = bpy.props.EnumProperty(items = [("dummy","dummy","dummy")],
                                       name = "Node Type",
                                       description = "The NWN Node type of this object")
    
    is_nwn_object = bpy.props.BoolProperty(name = "Is Neverwinter Nights Object", 
                                   description="Toggles whether this object is an nwn object and should be included in exports", 
                                   default=False)
    
    
    @classmethod
    def register(cls):
        
        #We create a dynamic class to use for node properties 
        classname = "BorealisNodeProps"
        attribute_dict = {"bl_idname": classname, 
                          "bl_label" : "Neverwinter Nights Node properties", 
                          "properties" : []}
        
        from . import borealis_mdl_definitions
        
        #we build the attribute dictionary by using the definitions from borealis_mdl_definitions
        for prop in borealis_mdl_definitions.GeometryNodeProperties.get_properties():
            # one case for each of the different property types
            if  prop.has_blender_eq:
                continue
            
            
            ##The order of the cases are important since some properties are subtypes of other
            if isinstance(prop, borealis_mdl_definitions.ColorProperty):
                attribute_dict[prop.name] = bpy.props.FloatVectorProperty(name = prop.name, size = 3, 
                                                                          subtype='COLOR', min = 0, max = 1)
                attribute_dict["properties"].append(prop)
            
            elif isinstance(prop, borealis_mdl_definitions.StringProperty):
                attribute_dict[prop.name] = bpy.props.StringProperty(name = prop.name)
                attribute_dict["properties"].append(prop)
            
            elif isinstance(prop, borealis_mdl_definitions.FloatVectorProperty):
                attribute_dict[prop.name] = bpy.props.FloatVectorProperty(name = prop.name, size = 3)
                attribute_dict["properties"].append(prop)
            
            elif isinstance(prop, borealis_mdl_definitions.BooleanProperty):
                attribute_dict[prop.name] = bpy.props.BoolProperty(name = prop.name)
                attribute_dict["properties"].append(prop)
                
            elif isinstance(prop, borealis_mdl_definitions.EnumProperty):
                items = [(name, name, name) for name in prop.enums]
                attribute_dict[prop.name] = bpy.props.EnumProperty(name = prop.name, 
                                                                   items = items)
                attribute_dict["properties"].append(prop)
            
            elif isinstance(prop, borealis_mdl_definitions.IntProperty):
                attribute_dict[prop.name] = bpy.props.IntProperty(name = prop.name)
                attribute_dict["properties"].append(prop)
            elif isinstance(prop, borealis_mdl_definitions.FloatProperty):
                attribute_dict[prop.name] = bpy.props.FloatProperty(name = prop.name)
                attribute_dict["properties"].append(prop)

            if prop.name not in attribute_dict:
                print("Failed to add property %s of type %s" % (prop.name, prop.__class__))
                      
        #we now create a dynamic class and register it so it will be usable by this class
        node_props_class = type(classname, (bpy.types.PropertyGroup,), attribute_dict)
        bpy.utils.register_class(node_props_class)
        
        cls.node_properties = bpy.props.PointerProperty(type=node_props_class)

class AnimationEvent(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name = "Name")
    time = bpy.props.FloatProperty(name = "Time")
    events = ["cast","hit","blur_start","blur_end",
              "snd_footstep","snd_hitground","draw_arrow","draw_weapon"]
    event_type = bpy.props.EnumProperty(name = "Event Type", items = [(foo, foo, foo) for foo in events])
        
class Animation(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name = "Name")
    start_marker_name = bpy.props.StringProperty(name = "Start Marker")
    end_marker_name = bpy.props.StringProperty(name = "End Marker")
    transtime = bpy.props.FloatProperty(name = "Transition time", default = 1)
    events = bpy.props.CollectionProperty(type = AnimationEvent)
    event_index = bpy.props.IntProperty(name = "Current event")
    ### Since the animations are tightly coupled to the markers
    ### dynamic properties are used for it's attributes
    
    def get_start_frame(self):
        return self.get_start_marker().frame
    
    def set_start_frame(self, value):
        self.get_start_marker().frame = value
    
    def get_start_marker(self):
        return bpy.context.scene.timeline_markers[self.start_marker_name]
        
    def set_start_marker(self, value):
        self.start_marker_name = value.name
    
    def get_end_frame(self):
        return self.get_end_marker().frame
    
    def set_end_frame(self, value):
        self.get_end_marker().frame = value
    
    def get_end_marker(self):
        return bpy.context.scene.timeline_markers[self.end_marker_name]
        
    def set_end_marker(self, value):
        self.end_marker_name = value.name
    
    end_marker = property(get_end_marker, set_end_marker)
    start_marker = property(get_start_marker, set_start_marker)
    end_frame = property(get_end_frame, set_end_frame)
    start_frame = property(get_start_frame, set_start_frame)
    
    
class AnimationProperties(bpy.types.PropertyGroup):
    current_animation = bpy.props.IntProperty(name = "current animation")
    animations = bpy.props.CollectionProperty(type=Animation)
    animation_index = bpy.props.IntProperty(name = "Index of currently selected animation")
    
     

class BorealisBasicProperties(bpy.types.PropertyGroup):
    classification = bpy.props.EnumProperty(items = [("effects","Effects","Effects"),
                                                     ("character","Character","character"),
                                                     ("item","Item","Item"),
                                                     ("tile","Tile","tile")],
                                       name = "Classification",
                                       description = "The classification of the current model")
    supermodel = bpy.props.StringProperty(name = "Supermodel")
    animationscale = bpy.props.FloatProperty(name = "Animation Scale")
    root_object_name = bpy.props.StringProperty(name = "Root object name")
        
    @classmethod
    def register(cls):
        bpy.utils.register_class(AnimationEvent)
        bpy.utils.register_class(Animation)
        bpy.utils.register_class(AnimationProperties)
        cls.animation_props = bpy.props.PointerProperty(type = AnimationProperties)
        
class OBJECT_PT_nwn_animations(bpy.types.Panel):
    bl_idname = "OBJECT_PT_nwn_animations"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "NWN Animation tools"
    bl_context = "scene"
    
    def draw(self, context):
        layout = self.layout
        ### animation settings ###
        box = layout.box()
        
        box.label(text="Animations")
        
        anim_props = context.scene.nwn_props.animation_props
        
        row = box.row()
        col = row.column()

        col.template_list(anim_props, "animations",
                          anim_props, "animation_index",
                          rows=3)
        
        col = row.column(align=True)
        col.operator("scene.add_nwn_anim", icon='ZOOMIN', text="")
        col.operator("scene.remove_nwn_anim", icon='ZOOMOUT', text="")
        
        if anim_props.animations:
            index = anim_props.animation_index
            animation = anim_props.animations[index]

            anim_row = box.row()
            anim_row.prop(animation, "name")
            
            anim_row = box.row()
            start_marker = animation.get_start_marker()
            end_marker = animation.get_end_marker()
            anim_row.prop(start_marker, "frame", text="Start frame")
            anim_row.prop(end_marker, "frame", text="End frame")
            
            row = box.row()
            col = row.column()
    
            col.template_list(animation, "events",
                              animation, "event_index",
                              rows=3)
            
            col = row.column(align=True)
            #col.operator("scene.add_nwn_anim_event", icon='ZOOMIN', text="")
            #col.operator("scene.remove_nwn_anim", icon='ZOOMOUT', text="")
            
        
        box.row().operator("scene.nwn_anim_focus")

            
class BorealisTools(bpy.types.Panel):
    bl_idname = "OBJECT_PT_nwn_tools"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "NWN Model tools"
    bl_context = "object"
    
    @classmethod
    def register(cls):
        register()
    
    @classmethod
    def poll(cls, context):
        return (context.object is not None)
     
    def draw(self, context):
        layout = self.layout

        obj = context.object
        
        #only display nwn modeling tools if the selected object is relevant in nwn
        if obj.type.upper() not in ['LAMP','MESH','EMPTY']:
            row = layout.row()
            row.label(text="Not compatible object")
            row = layout.row()
            row.label(text="Select a lamp, mesh or empty object")
            
            return
        
        box = layout.box()
        
        box.label(text="Basic model settings")
        box.prop(context.scene.nwn_props, "classification")
        box.prop(context.scene.nwn_props, "supermodel")
        box.prop(context.scene.nwn_props, "animationscale")
        box.prop_search(context.scene.nwn_props, "root_object_name", bpy.data, "objects")
        
        ### animation settings ###
        box = layout.box()
        
        box.label(text="Animations")
        
        anim_props = context.scene.nwn_props.animation_props
        
        row = box.row()
        col = row.column()

        col.template_list(anim_props, "animations",
                          anim_props, "animation_index",
                          rows=3)
        
        col = row.column(align=True)
        col.operator("scene.add_nwn_anim", icon='ZOOMIN', text="")
        col.operator("scene.remove_nwn_anim", icon='ZOOMOUT', text="")
        
        if anim_props.animations:
            index = anim_props.animation_index
            animation = anim_props.animations[index]

            anim_row = box.row()
            anim_row.prop(animation, "name")
            
            anim_row = box.row()
            start_marker = animation.get_start_marker()
            end_marker = animation.get_end_marker()
            anim_row.prop(start_marker, "frame", text="Start frame")
            anim_row.prop(end_marker, "frame", text="End frame")
            
            
        
        row = layout.row()
        row.prop(obj.nwn_props, "is_nwn_object", text="Toggle NWN object")
        
        if obj.nwn_props.is_nwn_object:
            ### node settings ###
            box = layout.box()
            
            box.label(text="Node settings")

            node_type = "dummy"
            
            #only display the node types which makes sense for the selected blender object
            if not obj.data:
                box.prop(obj.nwn_props, "nwn_node_type")
                node_type = obj.nwn_props.nwn_node_type
            else:
                box.prop(obj.data, "nwn_node_type")
                node_type = obj.data.nwn_node_type
            
            from . import borealis_mdl_definitions
            
            #Compare all possible settings for the specific node_type with the ones 
            #loaded into blender
            col_flow = box.column_flow(columns=2)
            for prop in borealis_mdl_definitions.GeometryNodeProperties.get_node_properties(node_type):
                if prop in bpy.types.BorealisNodeProps.properties:
                    col_flow.prop(obj.nwn_props.node_properties, prop.name)


class SCENE_OT_remove_nwn_animation(bpy.types.Operator):
    bl_idname ="scene.remove_nwn_anim"
    bl_label = "Remove NWN animation"
    
    animation_name = bpy.props.StringProperty("Name of animation to remove")
    
    @classmethod
    def poll(cls, context):
        if context.scene.nwn_props.animation_props.animations:
            return True
        else:
            return False
        
    def execute(self, context):
        anim_props = context.scene.nwn_props.animation_props
        index = anim_props.animation_index
        scene = context.scene
        
        animation = anim_props.animations[index]
        m = animation.start_marker
        scene.timeline_markers.remove(m)
        m = animation.end_marker
        scene.timeline_markers.remove(m)
        anim_props.animations.remove(index)
        context.area.tag_redraw() #force the gui to redraw
        return {'FINISHED'}
    
    def invoke(self,context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)
    
class SCENE_OT_add_nwn_animation(bpy.types.Operator):
    bl_idname ="scene.add_nwn_anim"
    bl_label = "Add a new NWN animation"
    
    name = bpy.props.StringProperty("Animation name")
    length = bpy.props.IntProperty("Animation length (frames)", default=50, min=0)
    
    def execute(self, context):
        print("add animation")
        scene = context.scene
        #find the last marker to get a good place to insert the new animation
        last_frame = 0
        for marker in scene.timeline_markers:
            if marker.frame > last_frame:
                last_frame = marker.frame
        
        start_frame = last_frame + 10
        end_frame = start_frame + self.length
        
        anim_ob = scene.nwn_props.animation_props.animations.add()
        anim_ob.name = self.name
        
        marker = scene.timeline_markers.new(self.name + "_start")
        marker.frame = start_frame
        anim_ob.start_marker = marker
        
        marker = scene.timeline_markers.new(self.name + "_end")
        marker.frame = end_frame
        anim_ob.end_marker = marker
        
        context.area.tag_redraw() #force the gui to redraw
        
        return {'FINISHED'}


    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class SCENE_OT_nwn_anim_focus(bpy.types.Operator):
    bl_idname ="scene.nwn_anim_focus"
    bl_label = "Focus on animation"
    bl_description = "Adjust scene start and end frame to the selected animation"
    
    @classmethod
    def poll(cls, context):
        if context.scene.nwn_props.animation_props.animations:
            return True
        else:
            return False
    
    def execute(self, context):
        scene = context.scene

        anim_props = context.scene.nwn_props.animation_props
        index = anim_props.animation_index
        
        animation = anim_props.animations[index]
        start_frame = animation.start_frame
        scene.frame_start = start_frame
        scene.frame_end = animation.end_frame
        scene.frame_current = start_frame
        scene.frame_start = start_frame # for some reason theres a bug if frame_start is set only once
        
        return {'FINISHED'}


def register():
    bpy.utils.register_class(BorealisSettings)
    bpy.types.Object.nwn_props = bpy.props.PointerProperty(type=BorealisSettings)
    
    bpy.utils.register_class(BorealisBasicProperties)
    bpy.types.Scene.nwn_props = bpy.props.PointerProperty(type=BorealisBasicProperties)
    
    bpy.utils.register_class(SCENE_OT_add_nwn_animation)
    bpy.utils.register_class(SCENE_OT_remove_nwn_animation)
    bpy.utils.register_class(SCENE_OT_nwn_anim_focus)
    bpy.utils.register_class(OBJECT_PT_nwn_animations)
    #bpy.utils.register_class(BorealisTools)
    
    #we set different node type enum lists, to make sure only node types relevant to the 
    #selected blender object are allowed
    bpy.types.Mesh.nwn_node_type = bpy.props.EnumProperty(items = [("trimesh","trimesh","trimesh"),
                                    ("danglymesh","danglymesh","danglymesh"),
                                    ("skin","skin","skin"),
                                    ("emitter","emitter","emitter"),
                                    ("aabb","aabb","aabb")],
                                   name = "Node Type",
                                   description = "The NWN Node type of this object")
    
    bpy.types.Lamp.nwn_node_type = bpy.props.EnumProperty(items = [("light","light","light")],
                                   name = "Node Type",
                                   description = "The NWN Node type of this object")

def unregister():
    pass