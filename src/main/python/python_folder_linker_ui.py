#----------------------------------------------------------
# File hello.py
#----------------------------------------------------------
import bpy
import python_folder_linker

class LibraryEntry(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "name", text="", emboss=False)
        layout.prop(item, "enabled", text="", index=index)
    def invoke(self, context, event):
        pass   

# draw the panel
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


# print button
class Refresh(bpy.types.Operator):
    bl_idname = "custom.refresh"
    bl_label = "Refresh"
    bl_description = "Check the sub-folder for linkable Python Libraries"

    def execute(self, context):
        path = context.scene.linkedSearchPath
        pythonFolderLinks = context.scene.pythonFolderLinks
        pythonFolderLinks.clear()
        descriptors = python_folder_linker.findLibraries(path, "LinkedPythonFolder.blend")
        for descriptor in descriptors:
            pythonFolderLink = pythonFolderLinks.add()
            pythonFolderLink.name = descriptor.name
            pythonFolderLink.path = descriptor.path
            pythonFolderLink.enabled = python_folder_linker.isAlreadyLinked(pythonFolderLink.path)
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

def updateWithEnabled(pythonFolderLink, context):
    instances = python_folder_linker.findInstances(pythonFolderLink.path)
    if pythonFolderLink.enabled:
        if not instances:
            python_folder_linker.loadGroup(pythonFolderLink.path)
            python_folder_linker.addInstances(
                pythonFolderLink.path,
                context.scene.linkedGroupName,
                pythonFolderLink.name,
                context.scene.link_instance_layer,
                context)
    else:
        for instance in instances:
            context.scene.objects.unlink(instance)
            python_folder_linker.unloadGroup(pythonFolderLink.path)
            bpy.data.objects.remove(instance)



class PythonFolderLink(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty()
    enabled = bpy.props.BoolProperty(update=updateWithEnabled)
    path = bpy.props.StringProperty()

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
if __name__ == "__main__":
    unregister()
    register()
