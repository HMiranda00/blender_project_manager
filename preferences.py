import bpy
import os
import json
from bpy.types import AddonPreferences, PropertyGroup, Operator
from bpy.props import StringProperty, CollectionProperty, EnumProperty, IntProperty, BoolProperty

class RecentProject(PropertyGroup):
    path: StringProperty(name="Project Path")
    name: StringProperty(name="Project Name")
    is_fixed_root: BoolProperty(name="Is Fixed Root")

class RoleMapping(PropertyGroup):
    """Classe para armazenar as configurações de cada cargo"""
    role_name: StringProperty(
        name="Nome do Cargo",
        description="Nome do cargo (ex: ANIMATION, LOOKDEV)",
    )
    description: StringProperty(
        name="Descrição",
        description="Breve descrição do que este cargo faz",
        default="Descrição do cargo"
    )
    link_type: EnumProperty(
        name="Tipo de Referência",
        description="Define se a collection será linkada ou anexada",
        items=[
            ('LINK', "Link", "Collection será linkada (referência)"),
            ('APPEND', "Append", "Collection será anexada (cópia)")
        ],
        default='LINK'
    )
    icon: EnumProperty(
        name="Ícone",
        description="Ícone para representar este cargo",
        items=[
            ('OUTLINER_OB_ARMATURE', "Animação", "Responsável pela animação dos personagens e objetos", 'OUTLINER_OB_ARMATURE', 0),
            ('MATERIAL', "Materiais", "Desenvolvimento de materiais e texturas", 'MATERIAL', 1),
            ('OUTLINER_OB_MESH', "Modelos", "Modelagem de objetos e personagens", 'OUTLINER_OB_MESH', 2),
            ('WORLD', "Ambiente", "Configuração do ambiente e iluminação global", 'WORLD', 3),
            ('CAMERA_DATA', "Câmera", "Configuração e animação de câmeras", 'CAMERA_DATA', 4),
            ('LIGHT', "Luzes", "Iluminação da cena", 'LIGHT', 5),
            ('PARTICLE_DATA', "Efeitos", "Efeitos especiais e partículas", 'PARTICLE_DATA', 6),
            ('RENDER_RESULT', "Composição", "Composição final e pós-produção", 'RENDER_RESULT', 7),
            ('TOOL_SETTINGS', "Técnico", "Configurações técnicas e otimizações", 'TOOL_SETTINGS', 8),
            ('MODIFIER', "Rigging", "Desenvolvimento de rigs e controles", 'MODIFIER', 9),
            ('UV', "UV/Textura", "Unwrap UV e texturização", 'UV', 10),
            ('VIEW3D', "Layout", "Layout de cena e blocking", 'VIEW3D', 11),
        ],
        default='TOOL_SETTINGS'
    )
    collection_color: EnumProperty(
        name="Cor da Collection",
        description="Cor para identificar visualmente a collection no outliner",
        items=[
            ('NONE', "Nenhuma", "Sem cor", 'OUTLINER_COLLECTION', 0),
            ('COLOR_01', "Vermelho", "Cor vermelha", 'COLLECTION_COLOR_01', 1),
            ('COLOR_02', "Laranja", "Cor laranja", 'COLLECTION_COLOR_02', 2),
            ('COLOR_03', "Amarelo", "Cor amarela", 'COLLECTION_COLOR_03', 3),
            ('COLOR_04', "Verde", "Cor verde", 'COLLECTION_COLOR_04', 4),
            ('COLOR_05', "Azul", "Cor azul", 'COLLECTION_COLOR_05', 5),
            ('COLOR_06', "Roxo", "Cor roxa", 'COLLECTION_COLOR_06', 6),
            ('COLOR_07', "Rosa", "Cor rosa", 'COLLECTION_COLOR_07', 7),
            ('COLOR_08', "Marrom", "Cor marrom", 'COLLECTION_COLOR_08', 8),
        ],
        default='NONE'
    )
    hide_viewport_default: BoolProperty(
        name="Oculto por Padrão",
        description="Define se a collection deve começar oculta no viewport",
        default=False
    )
    exclude_from_view_layer: BoolProperty(
        name="Excluir da View Layer",
        description="Define se a collection deve ser excluída da view layer por padrão",
        default=False
    )
    show_status: BoolProperty(
        name="Mostrar Status",
        description="Mostra o status deste cargo no painel principal",
        default=True
    )
    owns_world: BoolProperty(
        name="Controla World",
        description="Define se este cargo é responsável pelo World da cena",
        default=False
    )
    skip_assembly: BoolProperty(
        name="Ignorar Assembly",
        description="Se marcado, este cargo não será incluído no arquivo de assembly do shot",
        default=False
    )
    publish_path_preset: EnumProperty(
        name="Pasta de Publicação",
        description="Selecione o caminho de publicação para este cargo",
        items=[
            ('SHOTS', "SHOTS", "Publicação em shots"),
            ('CHARACTERS', "CHARACTERS", "Publicação em personagens"),
            ('PROPS', "PROPS", "Publicação em props"),
            ('CUSTOM', "Custom", "Definir caminho personalizado"),
        ],
        default='SHOTS'
    )
    custom_publish_path: StringProperty(
        name="Caminho Personalizado",
        description="Caminho personalizado para a pasta de publicação deste cargo (use placeholders como {root}, {projectCode}, {shot}, {role}, {assetName})",
        default=""
    )
    expanded: BoolProperty(
        name="Expandido",
        default=False,
        description="Expande ou colapsa as configurações deste cargo"
    )

class PROJECTMANAGER_OT_add_role_mapping(Operator):
    """Adiciona um novo cargo às configurações"""
    bl_idname = "project.add_role_mapping"
    bl_label = "Adicionar Cargo"
    
    def execute(self, context):
        prefs = context.preferences.addons['gerenciador_projetos'].preferences
        new_role = prefs.role_mappings.add()
        new_role.role_name = "NOVO_CARGO"
        new_role.description = "Descrição do novo cargo"
        new_role.icon = 'TOOL_SETTINGS'
        return {'FINISHED'}

class PROJECTMANAGER_OT_remove_role_mapping(Operator):
    """Remove um cargo das configurações"""
    bl_idname = "project.remove_role_mapping"
    bl_label = "Remover Cargo"
    
    index: IntProperty()
    
    def execute(self, context):
        prefs = context.preferences.addons['gerenciador_projetos'].preferences
        prefs.role_mappings.remove(self.index)
        return {'FINISHED'}

class PROJECTMANAGER_OT_export_config(Operator):
    """Exporta as configurações para um arquivo JSON"""
    bl_idname = "project.export_config"
    bl_label = "Exportar Configurações"
    
    filepath: StringProperty(
        subtype='FILE_PATH',
        default="project_config.json"
    )
    
    filter_glob: StringProperty(
        default='*.json',
        options={'HIDDEN'}
    )
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        prefs = context.preferences.addons['gerenciador_projetos'].preferences
        
        config = {
            'use_fixed_root': prefs.use_fixed_root,
            'fixed_root_path': prefs.fixed_root_path,
            'roles': []
        }
        
        for role_mapping in prefs.role_mappings:
            role_config = {
                'role_name': role_mapping.role_name,
                'description': role_mapping.description,
                'icon': role_mapping.icon,
                'collection_color': role_mapping.collection_color,
                'hide_viewport_default': role_mapping.hide_viewport_default,
                'exclude_from_view_layer': role_mapping.exclude_from_view_layer,
                'show_status': role_mapping.show_status,
                'owns_world': role_mapping.owns_world,
                'skip_assembly': role_mapping.skip_assembly,
                'publish_path_preset': role_mapping.publish_path_preset,
                'custom_publish_path': role_mapping.custom_publish_path,
                'link_type': role_mapping.link_type,
            }
            config['roles'].append(role_config)
        
        filepath = self.filepath
        if not filepath.lower().endswith('.json'):
            filepath += '.json'
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            self.report({'INFO'}, f"Configurações exportadas para: {filepath}")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Erro ao exportar configurações: {str(e)}")
            return {'CANCELLED'}

class PROJECTMANAGER_OT_import_config(Operator):
    """Importa as configurações de um arquivo JSON"""
    bl_idname = "project.import_config"
    bl_label = "Importar Configurações"
    
    filepath: StringProperty(
        subtype='FILE_PATH'
    )
    
    filter_glob: StringProperty(
        default='*.json',
        options={'HIDDEN'}
    )
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        if not os.path.exists(self.filepath):
            self.report({'ERROR'}, "Arquivo não encontrado")
            return {'CANCELLED'}
            
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            prefs = context.preferences.addons['gerenciador_projetos'].preferences
            
            prefs.use_fixed_root = config.get('use_fixed_root', True)
            prefs.fixed_root_path = config.get('fixed_root_path', '')
            
            prefs.role_mappings.clear()
            
            for role_config in config.get('roles', []):
                role_mapping = prefs.role_mappings.add()
                role_mapping.role_name = role_config.get('role_name', '')
                role_mapping.description = role_config.get('description', '')
                role_mapping.icon = role_config.get('icon', 'TOOL_SETTINGS')
                role_mapping.collection_color = role_config.get('collection_color', 'NONE')
                role_mapping.hide_viewport_default = role_config.get('hide_viewport_default', False)
                role_mapping.exclude_from_view_layer = role_config.get('exclude_from_view_layer', False)
                role_mapping.show_status = role_config.get('show_status', True)
                role_mapping.owns_world = role_config.get('owns_world', False)
                role_mapping.skip_assembly = role_config.get('skip_assembly', False)
                role_mapping.publish_path_preset = role_config.get('publish_path_preset', 'SHOTS')
                role_mapping.custom_publish_path = role_config.get('custom_publish_path', '')
                role_mapping.link_type = role_config.get('link_type', 'LINK')
            
            self.report({'INFO'}, "Configurações importadas com sucesso!")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Erro ao importar configurações: {str(e)}")
            return {'CANCELLED'}

class ProjectPreferences(AddonPreferences):
    bl_idname = 'gerenciador_projetos'

    use_fixed_root: BoolProperty(
        name="Usar Raiz Fixa",
        description="Se marcado, usará uma pasta raiz fixa para todos os projetos",
        default=True
    )

    fixed_root_path: StringProperty(
        name="Pasta Raiz Fixa",
        subtype='DIR_PATH',
        default="",
        description="Caminho para a pasta raiz fixa"
    )

    role_mappings: CollectionProperty(
        type=RoleMapping,
        name="Configurações dos Cargos",
        description="Define os cargos e suas configurações",
    )

    recent_projects: CollectionProperty(
        type=RecentProject,
        name="Recent Projects",
        description="Lista de projetos recentes"
    )

    show_all_recent: BoolProperty(
        name="Mostrar Todos os Projetos",
        default=False,
        description="Mostrar todos os projetos recentes ou apenas os 3 mais recentes"
    )
    
    recent_search: StringProperty(
        name="Buscar Projetos",
        default="",
        description="Filtrar projetos recentes"
    )

    def draw(self, context):
        layout = self.layout
        
        # Documentação/Ajuda
        help_box = layout.box()
        help_box.label(text="Documentação", icon='HELP')
        help_box.label(text="Como o addon funciona:", icon='INFO')
        col = help_box.column()
        col.label(text="1. Cada cargo define uma collection principal com o mesmo nome")
        col.label(text="2. As collections são criadas com as configurações definidas abaixo")
        col.label(text="3. Ao criar um novo shot, a collection do cargo é criada automaticamente")
        col.label(text="4. Ao linkar um cargo, sua collection é linkada e um override é criado")
        
        # Configuração da Raiz do Projeto
        box = layout.box()
        box.label(text="Configuração da Raiz do Projeto", icon='FILE_FOLDER')
        box.prop(self, "use_fixed_root")
        if self.use_fixed_root:
            box.prop(self, "fixed_root_path")
        
        # Botões de Importação/Exportação
        box = layout.box()
        box.label(text="Gerenciamento de Configurações", icon='SETTINGS')
        row = box.row()
        row.operator("project.export_config", icon='EXPORT')
        row.operator("project.import_config", icon='IMPORT')
        
        # Configurações dos cargos
        box = layout.box()
        box.label(text="Configurações dos Cargos", icon='COMMUNITY')
        
        # Botão para adicionar novo cargo
        row = box.row()
        row.operator("project.add_role_mapping", icon='ADD')
        
        # Lista de cargos existentes
        for i, role_mapping in enumerate(self.role_mappings):
            role_box = box.box()
            
            # Cabeçalho com nome e botão remover
            header = role_box.row()
            header.prop(role_mapping, "expanded", icon='TRIA_DOWN' if role_mapping.expanded else 'TRIA_RIGHT', icon_only=True, emboss=False)
            header.prop(role_mapping, "role_name", text="")
            remove = header.operator("project.remove_role_mapping", icon='X', text="")
            remove.index = i
            
            if role_mapping.expanded:
                # Configurações básicas
                col = role_box.column()
                col.prop(role_mapping, "description")
                
                # Configurações de publicação
                col.prop(role_mapping, "publish_path_preset")
                if role_mapping.publish_path_preset == 'CUSTOM':
                    col.prop(role_mapping, "custom_publish_path")
                
                # Ícone com preview
                icon_row = col.row()
                icon_row.prop(role_mapping, "icon")
                icon_row.label(icon=role_mapping.icon)
                
                # Configurações da collection
                col_settings = role_box.box()
                col_settings.label(text="Configurações da Collection:", icon='OUTLINER')
                col_settings.prop(role_mapping, "collection_color")
                col_settings.prop(role_mapping, "hide_viewport_default")
                col_settings.prop(role_mapping, "exclude_from_view_layer")

                # Configurações do Link
                link_settings = role_box.box()
                link_settings.label(text="Configurações de Link:", icon='LINKED')
                link_settings.prop(role_mapping, "link_type")

                # Configurações especiais
                special_settings = role_box.box()
                special_settings.label(text="Configurações Especiais:", icon='SETTINGS')
                row = special_settings.row()
                row.prop(role_mapping, "owns_world", icon='WORLD')
                row.prop(role_mapping, "show_status", icon='INFO')
                row = special_settings.row()
                row.prop(role_mapping, "skip_assembly", icon='FILE_BLEND')

# Lista de classes para registro
classes = (
    RecentProject,
    RoleMapping,
    PROJECTMANAGER_OT_add_role_mapping,
    PROJECTMANAGER_OT_remove_role_mapping,
    PROJECTMANAGER_OT_export_config,
    PROJECTMANAGER_OT_import_config,
    ProjectPreferences,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)