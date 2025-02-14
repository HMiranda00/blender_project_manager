import bpy
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty
from ..i18n.translations import translate as i18n_translate

class PROJECTMANAGER_OT_add_default_role(Operator):
    """Add a new default role"""
    bl_idname = "project.add_default_role"
    bl_label = i18n_translate("Add Default Role")
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        prefs = context.preferences.addons[__package__.split('.')[0]].preferences
        role = prefs.role_mappings.add()
        role.role_name = "NEW_ROLE"
        role.description = i18n_translate("New role description")
        role.icon = "NONE"
        role.collection_color = "NONE"
        prefs.active_role_index = len(prefs.role_mappings) - 1
        return {'FINISHED'}

class PROJECTMANAGER_OT_remove_default_role(Operator):
    """Remove the selected default role"""
    bl_idname = "project.remove_default_role"
    bl_label = i18n_translate("Remove Default Role")
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        prefs = context.preferences.addons[__package__.split('.')[0]].preferences
        return len(prefs.role_mappings) > prefs.active_role_index >= 0
    
    def execute(self, context):
        prefs = context.preferences.addons[__package__.split('.')[0]].preferences
        prefs.role_mappings.remove(prefs.active_role_index)
        prefs.active_role_index = min(max(0, prefs.active_role_index - 1), len(prefs.role_mappings) - 1)
        return {'FINISHED'}

class PROJECTMANAGER_OT_move_default_role(Operator):
    """Move the selected default role up or down in the list"""
    bl_idname = "project.move_default_role"
    bl_label = i18n_translate("Move Default Role")
    bl_options = {'REGISTER', 'UNDO'}
    
    direction: EnumProperty(
        name=i18n_translate("Direction"),
        description=i18n_translate("Direction to move the role"),
        items=[
            ('UP', i18n_translate("Up"), ""),
            ('DOWN', i18n_translate("Down"), "")
        ],
        default='UP'
    )
    
    @classmethod
    def poll(cls, context):
        prefs = context.preferences.addons[__package__.split('.')[0]].preferences
        return len(prefs.role_mappings) > prefs.active_role_index >= 0
    
    def execute(self, context):
        prefs = context.preferences.addons[__package__.split('.')[0]].preferences
        index = prefs.active_role_index
        
        if self.direction == 'UP' and index > 0:
            prefs.role_mappings.move(index, index - 1)
            prefs.active_role_index -= 1
            
        elif self.direction == 'DOWN' and index < len(prefs.role_mappings) - 1:
            prefs.role_mappings.move(index, index + 1)
            prefs.active_role_index += 1
            
        return {'FINISHED'}

# Lista de classes para registro
classes = (
    PROJECTMANAGER_OT_add_default_role,
    PROJECTMANAGER_OT_remove_default_role,
    PROJECTMANAGER_OT_move_default_role
)

def register():
    """Register operators"""
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print(f"Error registering {cls.__name__}: {str(e)}")
            raise

def unregister():
    """Unregister operators"""
    for cls in reversed(classes):
        try:
            if hasattr(bpy.types, cls.__name__):
                bpy.utils.unregister_class(cls)
        except RuntimeError as e:
            if "unregister_class(...)" not in str(e):
                print(f"Error unregistering {cls.__name__}: {str(e)}")
                raise
        except Exception as e:
            print(f"Error unregistering {cls.__name__}: {str(e)}")
            raise 
