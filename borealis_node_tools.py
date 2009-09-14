#!BPY
# -*- coding: utf-8 -*-

from event_handler import *
from aurora_widgets import *
from aurora_link import *
from copy import copy


class AuSelectedObLabel(TextLabel):
	def update(self):
		if AuroraLink.active_object:
			self.name = "Selected Object: " + AuroraLink.active_object.name
		else:
			self.name = "Selected Object: No Object Selected"
		self.size = (Blender.Draw.GetStringWidth(self.name, "normalfix"), 20)

widget_size = [150,20]
root_panel = TogglePanel("Node Tools", 1, 2, widget_size = widget_size, padding = (10, 10))

### Basic node controls ###r

header_panel = Panel("Basic Node Tools", 1, 1, padding = (0,5), color = (1.0, 1.0, 0.0))
root_panel.add(header_panel)


selected_info = AuSelectedObLabel("Selected object: ")
header_panel.add(selected_info)

aurora_toggle = AuToggle( "Aurora Node", "is_aurora_object")
header_panel.add(aurora_toggle)

node_type = AuMenuNamed("Node Type", "node_type", menuitems = {"Aurora Base Node": "aurabase",
																	"Dummy Node" : "dummy",
																	"Trimesh Node" : "trimesh",
																	"Dangly Mesh Node" : "danglymesh",
																	"Skin Node" : "skin",
																	"Emitter Node" : "emitter",
																	"Light Node" : "light"},
							default_item = "Dummy Node")
header_panel.add(node_type)
### End basic node controls ###

### Aurabase buttons ###
aurabase_buttons = Panel("Aurabase buttons", 1, 2, padding = (0,5))
aurabase_buttons.add(AuToggle("Export", "aurabase/export"))
### End Aurabase buttons ###

### Dummy Node Panel ###
dummy_panel = Panel("Dummy node panel", 1, 1)
### Dummy Node Panel End ###

### Common mesh buttons ###
common_mesh_buttons = Panel("Common mesh buttons", 1,1, padding = (0,5))
common_mesh_toggles = Panel("Toggle Buttons", 1,1)
common_mesh_toggles.add(AuFloat("Scale", "mesh/scale"))
common_mesh_toggles.add(AuInteger("Shininess", "mesh/shininess"))
common_mesh_toggles.add(AuToggle("Shadow", "mesh/shadow"))
common_mesh_toggles.add(AuToggle("Render", "mesh/render"))
common_mesh_toggles.add(AuToggle("Beaming", "mesh/beaming"))
common_mesh_toggles.add(AuToggle("Rotate Texture", "mesh/rotatetexture"))
common_mesh_toggles.add(AuToggle("Inherit Color", "mesh/inheritcolor"))
common_mesh_buttons.add(common_mesh_toggles)
common_mesh_buttons.add(AuMenuNamed("Tilefade", "mesh/tilefade", menuitems = {"Not a cap" : 0, "Fadable" : 1, "Neighbour" : 2 , "Base" : 3}, default_item = "Not a cap"))
common_mesh_buttons.add(AuColorPickerNamed("Ambient color:", "mesh/ambient", size = (140,40), picker_rect = (40,40)))
common_mesh_buttons.add(AuColorPickerNamed("Self Illum. color:", "mesh/selfillumcolor", size = (140,40), picker_rect = (40,40)))
### End Common mesh buttons ###

#### Trimesh Buttons ####
trimesh_buttons = Panel("Mesh Buttons", 1, 2, padding = (0,5))
trimesh_buttons.add(TextLabel("Trimesh Tools"))
trimesh_buttons.add(common_mesh_buttons)
### End Trimesh buttons ###

### Dangly Mesh Tools ###
danglymesh_panel = Panel("Dangly Mesh Buttons", 1, 2, padding = (0,5))
danglymesh_panel.add(TextLabel("Danglymesh Tools"))
danglymesh_panel.add(copy(common_mesh_buttons))
danglymesh_settings = Panel("Dangly Mesh Buttons", 1, 1)
danglymesh_settings.add(AuFloat("Period", "mesh/period"))
danglymesh_settings.add(AuFloat("Displacement", "mesh/displacement"))
danglymesh_settings.add(AuFloat("Tightness", "mesh/tightness"))
danglymesh_panel.add(danglymesh_settings)
### End Dangly Mesh Buttons ###

### Light Node Tools ###
light_panel = Panel("Light Node Buttons", 1, 2, padding = (0,0))
light_panel.add(AuColorPickerNamed("Color",'light/color'))
light_panel.add(AuToggle("Multiplier",'light/multiplier'))
light_panel.add(AuToggle("Radius",'light/radius'))
light_panel.add(AuToggle("Ambient Only",'light/ambientonly'))
light_panel.add(AuToggle("Is Dynamic",'light/isdynamic'))
light_panel.add(AuToggle("Affect Dynamic",'light/affectdynamic'))
light_panel.add(AuToggle("Light Priority",'light/lightpriority'))
light_panel.add(AuToggle("Shadow",'light/shadow'))
light_panel.add(AuToggle("Lensflares",'light/lensflares'))
light_panel.add(AuToggle("Flare Radius",'light/flareradius'))
light_panel.add(AuToggle("Fading Light",'light/fadinglight'))
### End Light Node Tools ###

### EmitterNode Panel ###
### These will have to be better organized when I have the time
emitter_panel = Panel("Emitter Panel", 1, 1, widget_size = (150, 20), padding=(0,5))


#Emitter Style
emitter_style_panel = TogglePanel("Emitter Style", 2,1, toggle = 0)
emitter_panel.add(emitter_style_panel)
emitter_style_panel.add(AuMenuNamed("Update",'emitter/update', menuitems = {"Fountain" : "fountain", "Single" : "single", "Explosion" : "explosion", "Lighting" : "lightning"}, default_item = "Fountain"))
emitter_style_panel.add(AuMenuNamed("Render",'emitter/render', menuitems = {"Normal" : "normal", "Linked" : "linked", "Motion Blur" : "motion_blur", "Billboard_to_World_Z":"Billboard_to_World_Z",  "Billboard_to_Local_Z":"Billboard_to_Local_Z", "Aligned_to_World_Z" :  "Aligned_to_World_Z", "Aligned_to_Particle_Dir" : "Aligned_to_Particle_Dir"}, default_item = "Normal")) #[Normal | linked | Motion_blur]  - Unknown. Probably controls how the particles are drawn in some way.
emitter_style_panel.add(AuMenuNamed("Blend",'emitter/blend', menuitems = {"Normal" : "normal", "Lighten" : "lighten", "Punch" : "punch"}, default_item = "Normal"))  # [Normal | lighten]  - Unknown.
emitter_style_panel.add(AuMenuNamed("Spawn Type",'emitter/spawntype', menuitems = {"Normal" : 0, "Trail" : 1}, default_item = "Normal"))  

#Emitter Parameters
emitter_params_panel = TogglePanel("Emitter Params", 2,1, toggle = 0)
emitter_panel.add(emitter_params_panel)
emitter_params_panel.add(AuInteger("X Size",'emitter/xsize'))
emitter_params_panel.add(AuInteger("Y Size",'emitter/ysize'))

emitter_params_panel.add(AuToggle("Inherit",'emitter/inherit'))
emitter_params_panel.add(AuToggle("inherit_local",'emitter/inherit_local'))
emitter_params_panel.add(AuToggle("inherit_part",'emitter/inherit_part'))
emitter_params_panel.add(AuToggle("inheritvel",'emitter/inheritvel'))

#Misc
emitter_params_panel.add(AuInteger("renderorder",'renderorder')) 
emitter_params_panel.add(AuToggle("threshold",'threshold'))

#Blur params
emitter_params_panel.add(AuToggle("combinetime",'combinetime'))
emitter_params_panel.add(AuFloat("deadspace",'emitter/deadspace'))

##Emitter Particles
emitter_particles_panel = TogglePanel("Emitter Particles", 2, 1, toggle = 0)
emitter_panel.add(emitter_particles_panel)

emitter_particles_panel.add(AuColorPickerNamed("colorstart",'emitter/colorstart', picker_rect = (20,20)))
emitter_particles_panel.add(AuColorPickerNamed("colorend",'emitter/colorend', picker_rect = (20,20)))
emitter_particles_panel.add(AuToggle("m_istinted",'m_istinted'))

emitter_particles_panel.add(AuFloat("alphastart",'emitter/alphastart')) 
emitter_particles_panel.add(AuFloat("alphaend",'emitter/alphaend'))
emitter_particles_panel.add(AuFloat("sizestart",'emitter/sizestart'))
emitter_particles_panel.add(AuFloat("sizeend",'emitter/sizeend'))
emitter_particles_panel.add(AuFloat("sizestart_y",'emitter/sizestart_y'))
emitter_particles_panel.add(AuFloat("sizeend_y",'emitter/sizeend_y')) 
emitter_particles_panel.add(AuFloat("birthrate",'emitter/birthrate')) 
emitter_particles_panel.add(AuFloat("lifeexp",'emitter/lifeexp'))
emitter_particles_panel.add(AuFloat("mass",'emitter/mass')) 
emitter_particles_panel.add(AuFloat("spread",'emitter/spread')) 
emitter_particles_panel.add(AuFloat("particlerot",'emitter/particlerot')) 
emitter_particles_panel.add(AuFloat("velocity",'emitter/velocity')) 
emitter_particles_panel.add(AuFloat("randvel",'emitter/randvel'))
emitter_particles_panel.add(AuFloat("blurlength",'emitter/blurlength')) 
emitter_particles_panel.add(AuFloat("opacity",'emitter/opacity'))
emitter_particles_panel.add(AuToggle("bounce",'emitter/bounce'))
emitter_particles_panel.add(AuToggle("bounce_co",'emitter/bounce_co'))

emitter_particles_panel.add(AuToggle("loop",'emitter/loop'))
emitter_particles_panel.add(AuToggle("splat",'splat'))
emitter_particles_panel.add(AuToggle("affectedbywind",'affectedbywind'))





#texture settings
emitter_texture_panel = TogglePanel("Emitter Texture Values", 2, 1, toggle = 0)
emitter_panel.add(emitter_texture_panel)
emitter_texture_panel.add(AuToggle("texture",'texture'))
emitter_texture_panel.add(AuToggle("twosidedtex",'emitter/twosidedtex')) 
emitter_texture_panel.add(AuToggle("xgrid",'xgrid')) 
emitter_texture_panel.add(AuToggle("ygrid",'ygrid'))
emitter_texture_panel.add(AuFloat("fps",'emitter/fps'))
emitter_texture_panel.add(AuInteger("framestart",'emitter/framestart')) 
emitter_texture_panel.add(AuInteger("frameend",'emitter/frameend')) 
emitter_texture_panel.add(AuFloat("random",'emitter/random'))
emitter_texture_panel.add(AuStringEntry("Chunk Name: ", "emitter/chunkname"))


#Emitter advanced
emitter_advanced_panel = TogglePanel("Emitter Advanced", 2, 1, toggle = 0)
emitter_panel.add(emitter_advanced_panel)
#Lightning params
emitter_advanced_panel.add(AuFloat("lightningdelay",'emitter/lightningdelay')) 
emitter_advanced_panel.add(AuFloat("lightningradius",'emitter/lightningradius')) 
emitter_advanced_panel.add(AuFloat("lightningscale",'emitter/lightningscale'))

emitter_advanced_panel.add(AuFloat("blastradius",'emitter/blastradius'))
emitter_advanced_panel.add(AuFloat("blastlength",'emitter/blastlength'))


emitter_advanced_panel.add(AuToggle("update_sel",'emitter/update_sel'))
emitter_advanced_panel.add(AuToggle("render_sel",'emitter/render_sel'))
emitter_advanced_panel.add(AuToggle("blend_sel",'emitter/blend_sel'))


#p2p settings
emitter_p2p_panel = TogglePanel("Emitter p2p settings", 2, 1, toggle = 0)
emitter_panel.add(emitter_p2p_panel)
emitter_p2p_panel.add(AuToggle("p2p",'emitter/p2p'))
emitter_p2p_panel.add(AuMenuNamed("p2p_type",'emitter/p2p_type', menuitems = {"Bezier" : "Bezier", "Gravity" : "Gravity"}, default_item = "Gravity"))
emitter_p2p_panel.add(AuToggle("p2p_sel",'emitter/p2p_sel')) 
emitter_p2p_panel.add(AuToggle("p2p_bezier2",'emitter/p2p_bezier2')) 
emitter_p2p_panel.add(AuToggle("p2p_bezier3",'p2p_bezier3'))

emitter_p2p_panel.add(AuToggle("Drag",'drag')) 
emitter_p2p_panel.add(AuToggle("Gravity",'grav'))

### Emitter Node Panel END ###


dyn_panel = AuDynamicPanel("Node Panels", 1, 1, "node_type", panel_dict = {"light" : light_panel,
																			"trimesh" : trimesh_buttons,
																			"skin" : trimesh_buttons,
																			"aurabase" : aurabase_buttons,
																			"danglymesh" : danglymesh_panel,
																			"dummy" : dummy_panel,
																			"emitter" : emitter_panel})
header_panel.add(dyn_panel)
