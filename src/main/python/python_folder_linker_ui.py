#----------------------------------------------------------
# File hello.py
#----------------------------------------------------------
import bpy
import os

bl_info = {
    "name": "Python Folder Linker",
    "description": "Links/Unlinks Python Folder Blend files",
    "author": "Monster",
    "version": (1, 0),
    "blender": (2, 67, 0),
    "location": "Scene > Linked Python Libraries",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/"
                "Scripts/My_Script",
    "category": "Game Engine",
}



def updateWithEnabled(pythonFolderLink, context):
    instances = findInstances(pythonFolderLink.path)
    if pythonFolderLink.enabled:
        if not instances:
            loadGroup(pythonFolderLink.path)
            addInstances(
                pythonFolderLink.path,
                context.scene.linkedGroupName,
                pythonFolderLink.name,
                context.scene.link_instance_layer,
                context)
    else:
        for instance in instances:
            context.scene.objects.unlink(instance)
            unloadGroup(pythonFolderLink.path)
            bpy.data.objects.remove(instance)

def findLibraries(basePath, fileName):
    descriptors = []
    rootPath = os.path.abspath(bpy.path.abspath(basePath))
    for path in findFilePaths(rootPath, fileName):
        descriptors.append(LibraryDescriptor(
            findDescriptor(rootPath, path), path)
        )
    return descriptors

def findFilePaths(rootPath, fileName):
    filePaths = []
    for (dirpath, dirnames, filenames) in os.walk(rootPath, topdown=True):
        for filename in filenames:
            if filename.endswith(fileName):
                filePaths.append(os.path.join(dirpath, filename))
    return filePaths

def findDescriptor(root, path):
    base = path
    last = None
    while base != last:
        if (base == root):
            return folder
        last = base
        base, folder = os.path.split(base)

def loadGroup(path):
    if not isAlreadyLinked(path):
        with bpy.data.libraries.load(path, link=True) as (sourceData, targetData):
            targetData.groups = sourceData.groups

def unloadGroup(path):
    library = findLibrary(path)
    for group in findLinkedGroups(path):
        group.user_clear()
        bpy.data.groups.remove(group)

    for object in  library.users_id:
        object.user_clear()
        bpy.data.objects.remove(object)
    #bpy.data.libraries.remove(library)

def isAlreadyLinked(path):
    if findLinkedGroups(path):
        return True
    return False

def findInstances(path):
    return [user for group in findLinkedGroups(path)
                    for user in group.users_dupli_group]

def addInstances(path, groupName, libraryName, layers, context):
    scene = context.scene
    libraries = bpy.data.libraries
    groups = findLinkedGroups(path)
    for group in groups:
        name = group.name + '.' + libraryName
        createInstance(name, group, layers, context)

def createInstance(name, group, layers, context):
    instance = bpy.data.objects.new(name, None)
    context.scene.objects.link(instance)
    instance.dupli_type = 'GROUP'
    instance.dupli_group = group
    instance.show_name = True
    instance.layers = layers
    return instance

def findLibrary(path):
    libraries = bpy.data.libraries
    for library in libraries:
        if path == library.filepath:
            return library

def findLinkedGroups(path):
    return findGroupsInLibrary(findLibrary(path))

def findGroupsInLibrary(library):
    if library:
        return [object for object in library.users_id
            if isinstance(object, bpy.types.Group)]
    return []

def unregister():
    try:
        bpy.utils.unregister_module(__name__)
        scene = bpy.types.Scene
        del scene.pythonFolderLinks
        del scene.selected_link_index
        del scene.linkedSearchPath
        del scene.link_instance_layer
        del scene.linkedGroupName
    except AttributeError:
        pass

def register():
    bpy.utils.register_module(__name__)
    scene = bpy.types.Scene
    scene.selected_link_index = bpy.props.IntProperty()
    scene.pythonFolderLinks = bpy.props.CollectionProperty(type=PythonFolderLink)
    scene.linkedGroupName = bpy.props.StringProperty(
        default="LinkedPythonFolder",
        name="Group Name",
        description="The name of the group to be instantiated")
    scene.linkedSearchPath = bpy.props.StringProperty(
          name = "Search Path",
          default = "//../../../../",
          description = "Define the path to search the sub folders",
          subtype = 'DIR_PATH'
          )
    scene.link_instance_layer = bpy.props.BoolVectorProperty(
        subtype='LAYER', size=20, default=[False]*19 + [True],
        name="Layers", description="Layers to add the instances to")

class LibraryEntry(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "name", text="", emboss=False)
        layout.prop(item, "enabled", text="", index=index)

    def invoke(self, context, event):
        pass

class LibraryPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_idname = 'OBJECT_PT_linked_python_libraries'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_label = "Linked Python Libraries"

    def draw(self, context):
        layout = self.layout

        rows = 2
        row = layout.row()
        row.prop(context.scene, 'linkedSearchPath')

        row = layout.row()
        row.prop(context.scene, 'linkedGroupName')

        row = layout.row()
        row.template_list("LibraryEntry", "",
                          context.scene, "pythonFolderLinks",
                          context.scene, "selected_link_index",
                          rows=rows)

        row = layout.row()
        col = row.column(align=True)
        col.operator("custom.refresh")

        row = layout.row()
        col = row.column(align=True)
        col.operator("custom.enable_all")
        col = row.column(align=True)
        col.operator("custom.disable_all")

        row = layout.row()
        row.prop(context.scene,"link_instance_layer")

class Refresh(bpy.types.Operator):
    bl_idname = "custom.refresh"
    bl_label = "Refresh"
    bl_description = "Check the sub-folder for linkable Python Libraries"

    def execute(self, context):
        path = context.scene.linkedSearchPath
        pythonFolderLinks = context.scene.pythonFolderLinks
        pythonFolderLinks.clear()
        descriptors = findLibraries(path, "LinkedPythonFolder.blend")
        for descriptor in descriptors:
            pythonFolderLink = pythonFolderLinks.add()
            pythonFolderLink.name = descriptor.name
            pythonFolderLink.path = descriptor.path
            pythonFolderLink.enabled = isAlreadyLinked(pythonFolderLink.path)
        return{'FINISHED'}

class EnableAll(bpy.types.Operator):
    bl_idname = "custom.enable_all"
    bl_label = "Enable All"
    bl_description = "Enable All Items"

    def execute(self, context):
        pythonFolderLinks = context.scene.pythonFolderLinks
        for pythonFolderLink in pythonFolderLinks:
            pythonFolderLink.enabled = True

        return{'FINISHED'}

class DisableAll(bpy.types.Operator):
    bl_idname = "custom.disable_all"
    bl_label = "Disable All"
    bl_description = "Disable All Items"

    def execute(self, context):
        pythonFolderLinks = context.scene.pythonFolderLinks
        for pythonFolderLink in pythonFolderLinks:
            pythonFolderLink.enabled = False

        return{'FINISHED'}

class PythonFolderLink(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty()
    enabled = bpy.props.BoolProperty(update=updateWithEnabled)
    path = bpy.props.StringProperty()

class LibraryDescriptor():
    def __init__(self, name, path):
        self.name = name
        self.path = path

if __name__ == "__main__":
    unregister()
    register()
