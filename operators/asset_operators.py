import bpy
import os
import traceback
from bpy.types import Operator
from bpy.props import EnumProperty, StringProperty, BoolProperty
from ..utils import save_current_file, get_project_info
from ..utils.cache import DirectoryCache

class ASSET_OT_reload_links(Operator):
    """Reload all linked assets and libraries"""
    bl_idname = "project.reload_links"
    bl_label = "Reload Assets"
    bl_description = "Reload Asset Links: Refresh all linked assets and libraries in the current file"

    def execute(self, context):
        try:
            # Save current file first
            save_current_file()
            
            # Reload all libraries
            reloaded = 0
            for lib in bpy.data.libraries:
                try:
                    lib.reload()
                    reloaded += 1
                except Exception as e:
                    print(f"Error reloading library {lib.filepath}: {str(e)}")
            
            # Force UI update
            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    area.tag_redraw()
            
            if reloaded > 0:
                self.report({'INFO'}, f"Reloaded {reloaded} libraries")
            else:
                self.report({'INFO'}, "No libraries to reload")
                
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error reloading assets: {str(e)}")
            return {'CANCELLED'}

class ASSET_OT_create_asset(Operator):
    bl_idname = "project.create_asset"
    bl_label = "Create Asset"
    bl_description = "Mark a collection as an asset or create a new asset file"

    asset_type: EnumProperty(
        name="Asset Type",
        items=[
            ('PROPS', "Prop", "General objects and props"),
            ('CHR', "Character", "Characters and rigs"),
            ('ENV', "Environment", "Environments and scenarios")
        ],
        default='PROPS'
    )

    name: StringProperty(
        name="Asset Name",
        description="Name of the asset"
    )

    save_mode: EnumProperty(
        name="Save Mode",
        items=[
            ('NEW_FILE', "New File", "Create a new file for the asset"),
            ('SAVE_AS', "Save As", "Save the current file as an asset file"),
            ('MARK_ONLY', "Mark Only", "Only mark as asset without saving new file")
        ],
        default='NEW_FILE',
        description="Defines how the asset will be saved"
    )

    @classmethod
    def poll(cls, context):
        if not context.scene.current_project:
            return False
        
        if bpy.data.is_saved:
            return (context.view_layer.active_layer_collection is not None and
                    context.view_layer.active_layer_collection.collection is not None)
            
        return True

    def _is_shot_file(self, context):
        """Check if we're in a shot file"""
        if not bpy.data.is_saved:
            return False
            
        current_file = os.path.basename(bpy.data.filepath)
        prefs = context.preferences.addons['blender_project_manager'].preferences
        project_path = context.scene.current_project
        _, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
        return current_file.startswith(project_prefix + "_SHOT_")

    def get_asset_path(self, context):
        """Return the correct path for the asset"""
        prefs = context.preferences.addons['blender_project_manager'].preferences
        project_path = context.scene.current_project
        _, workspace_path, _ = get_project_info(project_path, prefs.use_fixed_root)
        
        asset_path = os.path.join(workspace_path, "ASSETS 3D", self.asset_type)
        os.makedirs(asset_path, exist_ok=True)
        return asset_path

    def mark_as_asset(self, collection, generate_preview=True):
        """Mark the collection as asset and set the catalog"""
        # Set catalog IDs
        catalog_ids = {
            'PROPS': "d1f81597-d27d-42fd-8386-3a3def6c9200",
            'CHR': "8bfeff41-7692-4f58-8238-a5c4d9dad2d0",
            'ENV': "b741e8a3-5da8-4f5a-8f4c-e05dd1e4766c"
        }
        
        # Ensure the collection is active
        layer_collection = bpy.context.view_layer.layer_collection.children.get(collection.name)
        if layer_collection:
            bpy.context.view_layer.active_layer_collection = layer_collection
            
        # Mark as asset - this generates the preview automatically
        if not collection.asset_data:
            collection.asset_mark()
            
            # Set catalog after marking as asset
            if self.asset_type in catalog_ids:
                collection.asset_data.catalog_id = catalog_ids[self.asset_type]

    def _get_preview_path(self, context):
        """Return the path where the asset will be saved"""
        prefs = context.preferences.addons['blender_project_manager'].preferences
        project_path = context.scene.current_project
        _, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
        
        base_path = os.path.join(workspace_path, "ASSETS 3D", self.asset_type)
        return os.path.join(base_path, f"{project_prefix}_{self.asset_type}_{self.name}.blend")

    def _create_new_file(self, context, blend_path):
        """Create a new file for the asset"""
        current_project = context.scene.current_project
        
        # Create new file
        bpy.ops.wm.read_homefile(use_empty=True)
        context.scene.current_project = current_project
        
        # Create main collection
        main_collection = bpy.data.collections.new(self.name)
        context.scene.collection.children.link(main_collection)
        self.mark_as_asset(main_collection)
        
        # Set active collection
        layer_collection = context.view_layer.layer_collection.children[self.name]
        context.view_layer.active_layer_collection = layer_collection
        
        # Save file
        os.makedirs(os.path.dirname(blend_path), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    def execute(self, context):
        try:
            # Clear cache before heavy operations
            if hasattr(DirectoryCache, 'invalidate'):
                DirectoryCache.invalidate()
            
            # Force cleanup of orphan data
            bpy.ops.outliner.orphans_purge(do_recursive=True)
            
            if not context.scene.current_project:
                self.report({'ERROR'}, "Select a project first")
                return {'CANCELLED'}

            # Store current file info
            is_shot = self._is_shot_file(context)
            current_filepath = bpy.data.filepath
            
            # Get asset path
            blend_path = self._get_preview_path(context)

            # For shot files
            if is_shot:
                # Get active collection
                active_collection = context.view_layer.active_layer_collection.collection
                if not active_collection:
                    self.report({'ERROR'}, "Select a collection to create the asset")
                    return {'CANCELLED'}

                # Store collection name
                collection_name = active_collection.name

                # Create a set to store datablocks
                datablocks = set()

                def collect_dependencies(collection, seen=None):
                    """Collect all dependencies of the collection recursively"""
                    if seen is None:
                        seen = set()
                    if collection in seen:
                        return
                    seen.add(collection)
                    
                    if collection and isinstance(collection, bpy.types.ID):
                        datablocks.add(collection)
                    for obj in collection.objects:
                        if obj and isinstance(obj, bpy.types.ID):
                            datablocks.add(obj)
                            if obj.data and isinstance(obj.data, bpy.types.ID):
                                datablocks.add(obj.data)
                            for mat_slot in obj.material_slots:
                                mat = mat_slot.material
                                if mat and isinstance(mat, bpy.types.ID):
                                    datablocks.add(mat)
                                    if mat.node_tree:
                                        datablocks.add(mat.node_tree)
                    for child in collection.children:
                        collect_dependencies(child, seen)

                # Collect dependencies
                collect_dependencies(active_collection)

                # Create a temporary scene for export
                temp_scene = bpy.data.scenes.new(name="TempScene")
                temp_scene.collection.children.link(active_collection)
                datablocks.add(temp_scene)

                # Mark as asset before saving
                self.mark_as_asset(active_collection)

                # Save the datablocks to the asset file
                os.makedirs(os.path.dirname(blend_path), exist_ok=True)
                bpy.data.libraries.write(blend_path, datablocks, fake_user=True)

                # Remove temporary scene
                bpy.data.scenes.remove(temp_scene)

                # Remove original collection from scene
                if collection_name in context.scene.collection.children:
                    old_collection = context.scene.collection.children[collection_name]
                    context.scene.collection.children.unlink(old_collection)
                
                # Clean collection from blend data
                if collection_name in bpy.data.collections:
                    bpy.data.collections.remove(bpy.data.collections[collection_name])

                # Link the asset back
                with bpy.data.libraries.load(blend_path, link=True) as (data_from, data_to):
                    data_to.collections = [collection_name]

                # Add to scene
                for coll in data_to.collections:
                    if coll is not None:
                        context.scene.collection.children.link(coll)

                self.report({'INFO'}, f"Asset created and linked to shot: {collection_name}")

            # For normal files (non-shot)
            else:
                active_collection = context.view_layer.active_layer_collection.collection
                
                if self.save_mode == 'NEW_FILE':
                    # Create new file from scratch
                    if bpy.data.is_saved:
                        bpy.ops.wm.save_mainfile()
                    self._create_new_file(context, blend_path)
                    self.report({'INFO'}, f"New asset created at: {blend_path}")
                    
                elif self.save_mode == 'SAVE_AS':
                    # Save current file as asset
                    if not active_collection:
                        self.report({'ERROR'}, "Select a collection for the asset")
                        return {'CANCELLED'}
                    
                    # Mark as asset
                    self.mark_as_asset(active_collection)
                    
                    # Save as new file
                    os.makedirs(os.path.dirname(blend_path), exist_ok=True)
                    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
                    self.report({'INFO'}, f"File saved as asset at: {blend_path}")
                    
                else:  # MARK_ONLY
                    # Just mark existing collection as asset
                    if not active_collection:
                        self.report({'ERROR'}, "Select a collection to mark as asset")
                        return {'CANCELLED'}
                    
                    # Mark as asset
                    self.mark_as_asset(active_collection)
                    
                    # Save file if already saved
                    if bpy.data.is_saved:
                        bpy.ops.wm.save_mainfile()
                        self.report({'INFO'}, f"Collection '{active_collection.name}' marked as asset")
                    else:
                        self.report({'WARNING'}, "Collection marked as asset, but file is not saved")

            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Error creating asset: {str(e)}")
            return {'CANCELLED'}

    def invoke(self, context, event):
        if not context.scene.current_project:
            self.report({'ERROR'}, "Select a project first")
            return {'CANCELLED'}
            
        # Set default save mode based on context
        if self._is_shot_file(context):
            self.save_mode = 'NEW_FILE'  # In shots, always create new file
        elif not bpy.data.is_saved:
            self.save_mode = 'SAVE_AS'   # If file not saved, suggest "Save As"
        else:
            self.save_mode = 'MARK_ONLY' # Otherwise, just mark
        
        # Fill name with selected collection
        if context.view_layer.active_layer_collection:
            active_collection = context.view_layer.active_layer_collection.collection
            if active_collection:
                self.name = active_collection.name
        
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        
        # Project Information
        box = layout.box()
        box.label(text="Project:", icon='FILE_FOLDER')
        prefs = context.preferences.addons['blender_project_manager'].preferences
        project_path = context.scene.current_project
        project_name, _, _ = get_project_info(project_path, prefs.use_fixed_root)
        box.label(text=project_name)
        
        # Asset Type and Name
        layout.prop(self, "asset_type")
        layout.prop(self, "name")
        
        # Save options (except in shots)
        if not self._is_shot_file(context):
            box = layout.box()
            box.label(text="Save Mode:", icon='FILE_TICK')
            box.prop(self, "save_mode", text="")
            
            # Show additional info based on mode
            info_box = box.box()
            if self.save_mode == 'NEW_FILE':
                info_box.label(text="• Saves current file")
                info_box.label(text="• Creates new file for asset")
            elif self.save_mode == 'SAVE_AS':
                info_box.label(text="• Saves current file as asset")
                info_box.label(text="• Keeps current content")
            else:  # MARK_ONLY
                info_box.label(text="• Only marks as asset")
                info_box.label(text="• Keeps in current file")
        else:
            # For shots, show info about behavior
            box = layout.box()
            box.label(text="Shot Mode:", icon='SEQUENCE')
            info = box.box()
            info.label(text="• Creates new file for asset")
            info.label(text="• Automatically links to shot")

def register():
    bpy.utils.register_class(ASSET_OT_reload_links)
    bpy.utils.register_class(ASSET_OT_create_asset)

def unregister():
    bpy.utils.unregister_class(ASSET_OT_create_asset)
    bpy.utils.unregister_class(ASSET_OT_reload_links)