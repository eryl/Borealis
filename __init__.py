# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>
bl_info = {
    'name': 'Neverwinter Mdl importer/exporter',
    'author': 'Erik Ylipää',
    'version': '0.1',
    'blender': (2, 5, 8),
    'location': 'File > Import-Export > Neverwinter',
    'description': 'Import and Export Bioware Neverwinter Nights Models files (.mdl)',
    'warning': '', # used for warning icon and text in addons panel
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Import-Export'}


import bpy
from bpy.props import StringProperty, CollectionProperty
from bpy_extras.io_utils import ExportHelper, ImportHelper
import os
from . import blend_props
from . import gui
from . import operators
from . import mdl_import
from . import mdl_export

class BorealisImport(bpy.types.Operator, ImportHelper):
    '''
    Import Neverwinter Nights model in ascii format
    '''
    bl_idname = "import_mesh.nwn_mdl"
    bl_label = "Import NWN Mdl"

    filename_ext = ".mdl"

    filter_glob = StringProperty(default="*.mdl", options={'HIDDEN'})

    files = CollectionProperty(name="File Path",
                          description="File path used for importing "
                                      "the MDL file",
                          type=bpy.types.OperatorFileListElement)

    directory = StringProperty(subtype='DIR_PATH')

    def execute(self, context):
        
        paths = [os.path.join(self.directory, name.name) for name in self.files]
        if not paths:
            paths.append(self.filepath)
        
        for path in paths:
            mdl_import.import_mdl(path, context)
            
        return {'FINISHED'}

def register():
    bpy.utils.register_module(__name__)
    blend_props.register()
    
    bpy.types.INFO_MT_file_import.append(menu_import)
    bpy.types.INFO_MT_file_export.append(menu_export)
 
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_import)
    bpy.types.INFO_MT_file_export.remove(menu_export)
 
def menu_import(self, context):
    self.layout.operator(BorealisImport.bl_idname, text="Nwn Mdl(.mdl)").filepath = "*.mdl"

def menu_export(self, context):
    import os
    default_path = os.path.splitext(bpy.data.filepath)[0] + ".mdl"
    self.layout.operator(mdl_export.BorealisExport.bl_idname, text="Nwn Mdl(.mdl)").filepath = default_path

if __name__ == "__main__":
    register()