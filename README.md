# PythonFolderLinkerAddon
Blender Add-on to manage linked Python folders to be used with the BGE

This is a Blender Add-on.

It helps to organize what Python folders a .blend-file is linking in to be included in the Python search path.

## Requirements
The Python folders are supposed to contain a file called LinkedPythonFolder.blend in the Python folder you want to inlcude to your Python search path. The file LinkedPythonFolder.blend should contain a group called "LinkedPythonFolder" (configurable).

## Usage
* Install this add-on
* Choose a folder to search for Python folders [Search Path:]. 
* Setup the group name that is used within the LinkedPythonFolder.blend files.
* Press [Refresh] to update the list of available Python folders. 
* Select/Unselect the Python folders to include/exclude them from Python search path (within the BGE)

## Limits
* removing a link to a python folder does not immediatly remove the link. You will need to save and reload the blend file to get rid of it. This is a limitation of the current Blender API.

## How it works
### Refresh
* it searches through all subfolders of [Search Path:] to find files called LinkedPythonFolder.blend. 
* for each found blend file an entry in the library list is done. The name of the entry is the top folder where the file was found (one level below the search path). This allows to place the python folders into deeper structures such as src/main/python/.

### Select
* When selecting a library entry, the group [Group name:] will be linked in from the according blend file. An instance of that group will be aded to the current scene at layers [Layers:]. The instance will be named <group name>.<library name> for easier identification.
* As long a s this instance exist within the game (not necessarily the scene) the folder it resides in will be included in the Python search path (BGE feature).

### Unselect
* When unselecting a library entry, the instance object will be deleted, the group will be removed.
* Currently it is not possible to completely remove the reference to the blend file via Blender API. Therefore a save/load of the file is required for final unlink.
