Borealis Blender Add-on
=============

This is a Blender 2.5 Add-on for importing and exporting Neverwinter Nights models into and from Blender.
The Add-on also adds GUI Panels for setting properties not supported by Blender.


Installation
-----------

    Download the files to a single folder and place it in your Blender Add-ons folder (eg. blender/2.5x/scripts/addons/, where x is the version of blender used).
    In Blender, go to File->User Preferences->Add-Ons and locate the Add-on under Import-Export, toggle the checkbox and the add-on should be active. 


Usage
-----

    Import models by going to "File->Import->Import NWN mdl". The model has to be in ASCII format for the import to work.
    
    There are a couple of different GUI Panels for working with the NWN model. General settings for the model (the ones found in the header of the model) as well as animation settings are found in the Scene Properties.
    Node specific settings are found in a panel in Object Properties.
    
    To export a model, you must first make sure you have set the model root in the general settings. This object will be used a root node for a hierarchy of nodes to be exported. Only ancestors of the root node will be exported.
