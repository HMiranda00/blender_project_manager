"""
UI operators
"""
import bpy
from bpy.types import Operator
from bpy.props import StringProperty
from ..utils.shot_utils import update_shot_list
from .. import i18n

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

class PROJECTMANAGER_OT_update_shot_list(Operator):
    """Atualiza a lista de shots e cargos"""
    bl_idname = "project.update_shot_list"
    bl_label = i18n.translate("Update Shot List")
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        if update_shot_list(context):
            return {'FINISHED'}
        return {'CANCELLED'}

def register():
    bpy.utils.register_class(PROJECTMANAGER_OT_dummy_operator)
    bpy.utils.register_class(PROJECTMANAGER_OT_update_shot_list)

def unregister():
    bpy.utils.unregister_class(PROJECTMANAGER_OT_dummy_operator)
    bpy.utils.unregister_class(PROJECTMANAGER_OT_update_shot_list)
