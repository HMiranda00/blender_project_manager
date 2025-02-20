import bpy
from bpy.types import Operator
from bpy.props import StringProperty

class PROJECTMANAGER_OT_dummy_operator(Operator):
    bl_idname = "project.dummy_operator"
    bl_label = ""
    
    bg_type: StringProperty(default="NONE")
    
    def execute(self, context):
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        layout.emboss = 'NONE'
    
    def invoke(self, context, event):
        return {'FINISHED'}

def register():
    bpy.utils.register_class(PROJECTMANAGER_OT_dummy_operator)

def unregister():
    bpy.utils.unregister_class(PROJECTMANAGER_OT_dummy_operator)