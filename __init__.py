bl_addon_info = {
    'name': 'Neverwinter Mdl importer',
    'author': 'Erik Ylipää',
    'version': '0.1',
    'blender': (2, 5, 8),
    'location': 'File > Import-Export > Nwn mdl ',
    'description': 'Import Neverwinter Nights mdl files',
    'warning': '', # used for warning icon and text in addons panel
    'wiki_url': 'http://wiki.blender.org/index.php/Extensions:2.5/Py/' \
        'Scripts/File_I-O/Raw_Mesh_IO',
    'tracker_url': 'https://projects.blender.org/tracker/index.php?'\
        'func=detail&aid=21733&group_id=153&atid=469',
    "tracker_url": ""  ,
    "support": 'OFFICIAL',
    'category': 'Import-Export'}

# To support reload properly, try to access a package var, if it's there, reload everything
if "bpy" in locals():
    import imp
    if "export_ply" in locals():
        imp.reload(export_ply)
    if "import_ply" in locals():
        imp.reload(import_ply)

import bpy

from borealis_import import BorealisImport
from borealis_export import BorealisExport
from borealis_tools import BorealisTools

def register():
    bpy.types.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_import)
    bpy.types.INFO_MT_file_export.append(menu_export)
 
def unregister():
    bpy.types.register_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_import)
    bpy.types.INFO_MT_file_export.remove(menu_export)
 
def menu_import(self, context):
    self.layout.operator(BorealisImport.bl_idname, text="Nwn Mdl(.mdl)").filepath = "*.mdl"


def menu_export(self, context):
    import os
    default_path = os.path.splitext(bpy.data.filepath)[0] + ".mdl"
    self.layout.operator(BorealisExport.bl_idname, text="Nwn Mdl(.mdl)").filepath = default_path

if __name__ == "__main__":
    register()
    print("foo")