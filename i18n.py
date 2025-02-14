import bpy
import os
import json
from bpy.app.translations import pgettext_iface as iface_
from bpy.app.translations import register, unregister

# Translation context for the addon
TRANSLATION_CONTEXT = "Project Manager"

# Available languages
LANGUAGES = {
    'en_US': 'English',
    'pt_BR': 'PortuguÃªs (Brasil)'
}

# Translation dictionary
# Format: (msgctxt, msgid) : str
translations_dict = {
    # Interface strings
    ("*", "Project Manager"): {
        'en_US': 'Project Manager',
        'pt_BR': 'Gerenciador de Projetos'
    },
    ("*", "Project management and organization addon"): {
        'en_US': 'Project management and organization addon',
        'pt_BR': 'Addon para gerenciamento e organizaÃ§Ã£o de projetos'
    },
    
    # Panel titles and labels
    ("*", "Project Management"): {
        'en_US': 'Project Management',
        'pt_BR': 'Gerenciamento de Projetos'
    },
    ("*", "Role Management"): {
        'en_US': 'Role Management',
        'pt_BR': 'Gerenciamento de Cargos'
    },
    ("*", "Shot Management"): {
        'en_US': 'Shot Management',
        'pt_BR': 'Gerenciamento de Shots'
    },
    ("*", "Version Control"): {
        'en_US': 'Version Control',
        'pt_BR': 'Controle de VersÃ£o'
    },
    
    # Buttons and actions
    ("*", "Create Project"): {
        'en_US': 'Create Project',
        'pt_BR': 'Criar Projeto'
    },
    ("*", "Open Project"): {
        'en_US': 'Open Project',
        'pt_BR': 'Abrir Projeto'
    },
    ("*", "Create Shot"): {
        'en_US': 'Create Shot',
        'pt_BR': 'Criar Shot'
    },
    ("*", "Open Shot"): {
        'en_US': 'Open Shot',
        'pt_BR': 'Abrir Shot'
    },
    ("*", "Create Role"): {
        'en_US': 'Create Role',
        'pt_BR': 'Criar Cargo'
    },
    ("*", "Open Role"): {
        'en_US': 'Open Role',
        'pt_BR': 'Abrir Cargo'
    },
    ("*", "Link Role"): {
        'en_US': 'Link Role',
        'pt_BR': 'Vincular Cargo'
    },
    ("*", "Publish"): {
        'en_US': 'Publish',
        'pt_BR': 'Publicar'
    },
    ("*", "Open Publish"): {
        'en_US': 'Open Publish',
        'pt_BR': 'Abrir Publish'
    },
    
    # Status and info messages
    ("*", "Current Project"): {
        'en_US': 'Current Project',
        'pt_BR': 'Projeto Atual'
    },
    ("*", "Current Shot"): {
        'en_US': 'Current Shot',
        'pt_BR': 'Shot Atual'
    },
    ("*", "Current Role"): {
        'en_US': 'Current Role',
        'pt_BR': 'Cargo Atual'
    },
    ("*", "No project selected"): {
        'en_US': 'No project selected',
        'pt_BR': 'Nenhum projeto selecionado'
    },
    ("*", "No shot selected"): {
        'en_US': 'No shot selected',
        'pt_BR': 'Nenhum shot selecionado'
    },
    ("*", "No role selected"): {
        'en_US': 'No role selected',
        'pt_BR': 'Nenhum cargo selecionado'
    },
    
    # Settings and preferences
    ("*", "Team Mode"): {
        'en_US': 'Team Mode',
        'pt_BR': 'Modo Equipe'
    },
    ("*", "Solo Mode"): {
        'en_US': 'Solo Mode',
        'pt_BR': 'Modo Solo'
    },
    ("*", "Language"): {
        'en_US': 'Language',
        'pt_BR': 'Idioma'
    },
    ("*", "Default Role"): {
        'en_US': 'Default Role',
        'pt_BR': 'Cargo PadrÃ£o'
    },
    ("*", "Project Settings"): {
        'en_US': 'Project Settings',
        'pt_BR': 'ConfiguraÃ§Ãµes do Projeto'
    },
    
    # Error messages
    ("*", "Error"): {
        'en_US': 'Error',
        'pt_BR': 'Erro'
    },
    ("*", "Project not found"): {
        'en_US': 'Project not found',
        'pt_BR': 'Projeto nÃ£o encontrado'
    },
    ("*", "Shot not found"): {
        'en_US': 'Shot not found',
        'pt_BR': 'Shot nÃ£o encontrado'
    },
    ("*", "Role not found"): {
        'en_US': 'Role not found',
        'pt_BR': 'Cargo nÃ£o encontrado'
    },
    ("*", "Invalid project path"): {
        'en_US': 'Invalid project path',
        'pt_BR': 'Caminho do projeto invÃ¡lido'
    },
    ("*", "Invalid shot name"): {
        'en_US': 'Invalid shot name',
        'pt_BR': 'Nome do shot invÃ¡lido'
    },
    ("*", "Invalid role name"): {
        'en_US': 'Invalid role name',
        'pt_BR': 'Nome do cargo invÃ¡lido'
    },
    
    # Additional translations for preferences
    ("*", "Documentation"): {
        'en_US': 'Documentation',
        'pt_BR': 'DocumentaÃ§Ã£o'
    },
    ("*", "How the addon works:"): {
        'en_US': 'How the addon works:',
        'pt_BR': 'Como o addon funciona:'
    },
    ("*", "1. Each role defines a main collection with the same name"): {
        'en_US': '1. Each role defines a main collection with the same name',
        'pt_BR': '1. Cada cargo define uma collection principal com o mesmo nome'
    },
    ("*", "2. Collections are created with settings defined below"): {
        'en_US': '2. Collections are created with settings defined below',
        'pt_BR': '2. As collections sÃ£o criadas com as configuraÃ§Ãµes definidas abaixo'
    },
    ("*", "3. When creating a new shot, the role collection is created automatically"): {
        'en_US': '3. When creating a new shot, the role collection is created automatically',
        'pt_BR': '3. Ao criar um novo shot, a collection do cargo Ã© criada automaticamente'
    },
    ("*", "4. When linking a role, its collection is linked and an override is created"): {
        'en_US': '4. When linking a role, its collection is linked and an override is created',
        'pt_BR': '4. Ao linkar um cargo, sua collection Ã© linkada e um override Ã© criado'
    },
    ("*", "Project Root Configuration"): {
        'en_US': 'Project Root Configuration',
        'pt_BR': 'ConfiguraÃ§Ã£o da Raiz do Projeto'
    },
    ("*", "Settings Management"): {
        'en_US': 'Settings Management',
        'pt_BR': 'Gerenciamento de ConfiguraÃ§Ãµes'
    },
    ("*", "Role Settings"): {
        'en_US': 'Role Settings',
        'pt_BR': 'ConfiguraÃ§Ãµes dos Cargos'
    },
    ("*", "Collection Settings:"): {
        'en_US': 'Collection Settings:',
        'pt_BR': 'ConfiguraÃ§Ãµes da Collection:'
    },
    ("*", "Link Settings:"): {
        'en_US': 'Link Settings:',
        'pt_BR': 'ConfiguraÃ§Ãµes de Link:'
    },
    ("*", "Special Settings:"): {
        'en_US': 'Special Settings:',
        'pt_BR': 'ConfiguraÃ§Ãµes Especiais:'
    },
    ("*", "Interface Settings"): {
        'en_US': 'Interface Settings',
        'pt_BR': 'ConfiguraÃ§Ãµes da Interface'
    },
    ("*", "Use Fixed Root"): {
        'en_US': 'Use Fixed Root',
        'pt_BR': 'Usar Raiz Fixa'
    },
    ("*", "Fixed Root Path"): {
        'en_US': 'Fixed Root Path',
        'pt_BR': 'Pasta Raiz Fixa'
    },
    ("*", "If checked, will use a fixed root folder for all projects"): {
        'en_US': 'If checked, will use a fixed root folder for all projects',
        'pt_BR': 'Se marcado, usarÃ¡ uma pasta raiz fixa para todos os projetos'
    },
    ("*", "Path to fixed root folder"): {
        'en_US': 'Path to fixed root folder',
        'pt_BR': 'Caminho para a pasta raiz fixa'
    },
    ("*", "Recent Projects"): {
        'en_US': 'Recent Projects',
        'pt_BR': 'Projetos Recentes'
    },
    ("*", "Show All"): {
        'en_US': 'Show All',
        'pt_BR': 'Mostrar Todos'
    },
    ("*", "Search Projects"): {
        'en_US': 'Search Projects',
        'pt_BR': 'Buscar Projetos'
    },
    ("*", "Show all recent projects"): {
        'en_US': 'Show all recent projects',
        'pt_BR': 'Mostrar todos os projetos recentes'
    },
    ("*", "Filter recent projects"): {
        'en_US': 'Filter recent projects',
        'pt_BR': 'Filtrar projetos recentes'
    }
}

def get_prefs():
    """Get addon preferences"""
    return bpy.context.preferences.addons[__package__].preferences

def get_language():
    """Get current language from preferences or system default"""
    prefs = get_prefs()
    if hasattr(prefs, 'language'):
        return prefs.language
    return bpy.app.translations.locale

def translate(text):
    """Translate text using current language"""
    return iface_(text, TRANSLATION_CONTEXT)

def register_translations():
    """Register translations with Blender"""
    register(__name__, translations_dict)
    
def unregister_translations():
    """Unregister translations from Blender"""
    unregister(__name__) 
