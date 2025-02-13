import bpy
from . import context

# Export context functions
get_context = context.get_context
save_context = context.save_context
load_context = context.load_context
clear_context = context.clear_context
validate_context = context.validate_context

def register():
    """Register core module"""
    try:
        # Register scene properties for backward compatibility
        if not hasattr(bpy.types.Scene, "current_project"):
            bpy.types.Scene.current_project = bpy.props.StringProperty(
                name="Current Project",
                description="Current project path"
            )
        if not hasattr(bpy.types.Scene, "current_shot"):
            bpy.types.Scene.current_shot = bpy.props.StringProperty(
                name="Current Shot",
                description="Current shot name"
            )
        if not hasattr(bpy.types.Scene, "current_role"):
            bpy.types.Scene.current_role = bpy.props.StringProperty(
                name="Current Role",
                description="Current role name"
            )
        if not hasattr(bpy.types.Scene, "last_publish_time"):
            bpy.types.Scene.last_publish_time = bpy.props.StringProperty(
                name="Last Publish Time",
                description="Last publish time for current role"
            )
        if not hasattr(bpy.types.Scene, "version_status"):
            bpy.types.Scene.version_status = bpy.props.StringProperty(
                name="Version Status",
                description="Status of current version"
            )
        
        print("Core module registered successfully")
    except Exception as e:
        print(f"Error registering core module: {str(e)}")
        raise

def unregister():
    """Unregister core module"""
    try:
        # Remove scene properties
        if hasattr(bpy.types.Scene, "current_project"):
            del bpy.types.Scene.current_project
        if hasattr(bpy.types.Scene, "current_shot"):
            del bpy.types.Scene.current_shot
        if hasattr(bpy.types.Scene, "current_role"):
            del bpy.types.Scene.current_role
        if hasattr(bpy.types.Scene, "last_publish_time"):
            del bpy.types.Scene.last_publish_time
        if hasattr(bpy.types.Scene, "version_status"):
            del bpy.types.Scene.version_status
            
        print("Core module unregistered successfully")
    except Exception as e:
        print(f"Error unregistering core module: {str(e)}")
        raise 