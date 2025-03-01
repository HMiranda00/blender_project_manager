import bpy
from bpy.types import Panel, PropertyGroup, Scene
from bpy.props import StringProperty, BoolProperty

# Properties for file notes
class FileNoteProperties(PropertyGroup):
    note: StringProperty(
        name="Note",
        description="Add a note about the current file",
        default=""
    )

# Panel to display and edit file notes
class FILE_PT_notes(Panel):
    bl_label = "File Notes"
    bl_idname = "FILE_PT_notes"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        # Only show the panel if the file has been saved
        return bpy.data.filepath != ""
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Check if using the lock management module
        lock_info = None
        lock_status = "UNLOCKED"
        locked_by_me = False
        
        try:
            from ..utils.file_lock_manager import file_lock_manager
            if file_lock_manager:
                current_file = bpy.data.filepath
                if file_lock_manager.is_file_locked(current_file):
                    lock_info = file_lock_manager.get_lock_info(current_file)
                    lock_status = f"LOCKED by {lock_info['user']}"
                    locked_by_me = file_lock_manager.is_locked_by_me(current_file)
                    
                    # If there's a note, update the property to display
                    if locked_by_me and lock_info and 'note' in lock_info:
                        scene.file_note_props.note = lock_info['note']
        except:
            pass
            
        # Display lock status
        status_box = layout.box()
        status_row = status_box.row()
        status_row.label(text=f"Status: {lock_status}")
        
        # Display and edit note
        if locked_by_me:
            note_box = layout.box()
            note_box.label(text="Note:")
            note_box.prop(scene.file_note_props, "note", text="")
            
            # Add button to update note
            update_row = layout.row()
            update_row.operator("file.update_note", text="Update Note", icon='GREASEPENCIL')
            
            # Add button to unlock file
            unlock_row = layout.row()
            unlock_row.operator("file.unlock_file", text="Unlock File", icon='UNLOCKED')
        elif not file_lock_manager.is_file_locked(current_file):
            # If not locked, show button to lock
            lock_row = layout.row()
            lock_row.operator("file.lock_file", text="Lock File", icon='LOCKED')

# Operator to lock file
class FILE_OT_lock_file(bpy.types.Operator):
    """Lock the file for the current user"""
    bl_idname = "file.lock_file"
    bl_label = "Lock File"
    
    def execute(self, context):
        try:
            from ..utils.file_lock_manager import file_lock_manager
            if file_lock_manager:
                current_file = bpy.data.filepath
                if current_file:
                    success = file_lock_manager.lock_file(current_file)
                    if success:
                        self.report({'INFO'}, "File locked successfully.")
                    else:
                        self.report({'ERROR'}, "Could not lock the file. It may be locked by another user.")
                else:
                    self.report({'ERROR'}, "Save the file before locking it.")
        except Exception as e:
            self.report({'ERROR'}, f"Error locking file: {str(e)}")
            
        return {'FINISHED'}

# Operator to update note
class FILE_OT_update_note(bpy.types.Operator):
    """Update the note for the current file"""
    bl_idname = "file.update_note"
    bl_label = "Update Note"
    
    def execute(self, context):
        try:
            from ..utils.file_lock_manager import file_lock_manager
            if file_lock_manager:
                current_file = bpy.data.filepath
                if current_file:
                    note = context.scene.file_note_props.note
                    success = file_lock_manager.update_note(current_file, note)
                    if success:
                        self.report({'INFO'}, "Note updated successfully.")
                    else:
                        self.report({'ERROR'}, "Could not update the note. Check if the file is locked by you.")
                else:
                    self.report({'ERROR'}, "Save the file before adding a note.")
        except Exception as e:
            self.report({'ERROR'}, f"Error updating note: {str(e)}")
            
        return {'FINISHED'}

# Operator to unlock file
class FILE_OT_unlock_file(bpy.types.Operator):
    """Unlock the file"""
    bl_idname = "file.unlock_file"
    bl_label = "Unlock File"
    
    def execute(self, context):
        try:
            from ..utils.file_lock_manager import file_lock_manager
            if file_lock_manager:
                current_file = bpy.data.filepath
                if current_file:
                    success = file_lock_manager.unlock_file(current_file)
                    if success:
                        self.report({'INFO'}, "File unlocked successfully.")
                        # Clear the note when unlocking
                        context.scene.file_note_props.note = ""
                    else:
                        self.report({'ERROR'}, "Could not unlock the file. It may not be locked by you.")
                else:
                    self.report({'ERROR'}, "No file is currently open.")
        except Exception as e:
            self.report({'ERROR'}, f"Error unlocking file: {str(e)}")
            
        return {'FINISHED'}

# Lista de classes para registro
classes = (
    FileNoteProperties,
    FILE_PT_notes,
    FILE_OT_lock_file,
    FILE_OT_update_note,
    FILE_OT_unlock_file,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    # Register the property in the scene
    bpy.types.Scene.file_note_props = bpy.props.PointerProperty(type=FileNoteProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    # Remove the property from the scene
    del bpy.types.Scene.file_note_props 