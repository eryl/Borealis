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
        from . import borealis_import
        
        paths = [os.path.join(self.directory, name.name) for name in self.files]
        if not paths:
            paths.append(self.filepath)
        
        for path in paths:
            borealis_import.import_mdl(path, context)
            
        return {'FINISHED'}

def register():
    from . import properties
    from . import borealis_gui
    from . import borealis_operators
    from . import borealis_import
    from . import borealis_export
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_import)
    bpy.types.INFO_MT_file_export.append(menu_export)
 
def unregister():
    from . import properties
    from . import borealis_gui
    from . import borealis_operators
    from . import borealis_import
    from . import borealis_export
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_import)
    bpy.types.INFO_MT_file_export.remove(menu_export)
 
def menu_import(self, context):
    from . import borealis_import
    self.layout.operator(BorealisImport.bl_idname, text="Nwn Mdl(.mdl)").filepath = "*.mdl"

def menu_export(self, context):
    import os
    from . import borealis_export
    default_path = os.path.splitext(bpy.data.filepath)[0] + ".mdl"
    self.layout.operator(borealis_export.BorealisExport.bl_idname, text="Nwn Mdl(.mdl)").filepath = default_path

if __name__ == "__main__":
    register()