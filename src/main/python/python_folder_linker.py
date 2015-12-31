import bpy
import os

class LibraryDescriptor():
    def __init__(self, name, path):
        self.name = name
        self.path = path

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