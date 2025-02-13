"""
Internationalization module for the Project Manager addon.
This module contains all translatable strings and translation utilities.
"""

import bpy
import os
from typing import Dict, Tuple, Any

# Translation dictionary format:
# (msgctxt, msgid): msgstr
# msgctxt is usually "*" for general strings
# msgid is the English string
# msgstr is the translated string

# English (default/fallback)
en_US: Dict[Tuple[str, str], str] = {
    # General
    ("*", "Project Manager"): "Project Manager",
    ("*", "Project"): "Project",
    ("*", "Project:"): "Project:",
    ("*", "Shot"): "Shot",
    ("*", "Shot:"): "Shot:",
    ("*", "Role"): "Role",
    ("*", "Scene"): "Scene",
    ("*", "Scene:"): "Scene:",
    
    # Actions
    ("*", "New"): "New",
    ("*", "Open"): "Open",
    ("*", "Create"): "Create",
    ("*", "Link"): "Link",
    ("*", "Publish"): "Publish",
    ("*", "New Version"): "New Version",
    ("*", "Open Publish"): "Open Publish",
    ("*", "New Shot"): "New Shot",
    ("*", "Open Shot"): "Open Shot",
    ("*", "New Scene"): "New Scene",
    ("*", "Open Scene"): "Open Scene",
    
    # Project Types
    ("*", "Team"): "Team",
    ("*", "Solo"): "Solo",
    
    # Asset Management
    ("*", "Asset Browser"): "Asset Browser",
    ("*", "Create Asset"): "Create Asset",
    
    # Version Control
    ("*", "Versions"): "Versions",
    ("*", "Versions:"): "Versions:",
    ("*", "Last publish"): "Last publish",
    ("*", "WIP"): "WIP",
    
    # Settings
    ("*", "Settings"): "Settings",
    ("*", "Preferences"): "Preferences",
    ("*", "Use Versioning"): "Use Versioning",
    
    # Messages
    ("*", "Project created successfully"): "Project created successfully",
    ("*", "Error creating project"): "Error creating project",
    ("*", "Shot created successfully"): "Shot created successfully",
    ("*", "Error creating shot"): "Error creating shot",
    ("*", "Addon is not active"): "Addon is not active",
    ("*", "Settings not initialized"): "Settings not initialized",
    ("*", "Error loading interface"): "Error loading interface",
    
    # Roles
    ("*", "Animation"): "Animation",
    ("*", "Layout"): "Layout",
    ("*", "Lightning"): "Lightning",
    ("*", "Assembly"): "Assembly",
    ("*", "Roles"): "Roles",
    ("*", "Roles:"): "Roles:",
    ("*", "Link Role"): "Link Role",
    ("*", "Open Role"): "Open Role",
    
    # Recent Projects
    ("*", "Recent Projects"): "Recent Projects",
    ("*", "Recent Projects:"): "Recent Projects:",
    ("*", "Clear Recent"): "Clear Recent",
    ("*", "Search Projects"): "Search Projects",
    
    # New additions
    ("*", "Create Shot"): "Create Shot",
    ("*", "Create a new shot or scene"): "Create a new shot or scene",
    ("*", "Mode"): "Mode",
    ("*", "Create a new numbered shot"): "Create a new numbered shot",
    ("*", "Single Scene"): "Single Scene",
    ("*", "Create a single scene without numbering"): "Create a single scene without numbering",
    ("*", "Shot Number"): "Shot Number",
    ("*", "Scene Name"): "Scene Name",
    ("*", "Your Role"): "Your Role",
    ("*", "Select your role for this shot"): "Select your role for this shot",
    ("*", "Role Settings"): "Role Settings",
    ("*", "No project selected."): "No project selected.",
    ("*", "Role '{}' not configured in preferences."): "Role '{}' not configured in preferences.",
    ("*", "Shot already exists: {}"): "Shot already exists: {}",
    ("*", "Error creating WIP version"): "Error creating WIP version",
    ("*", "Shot created and WIP file saved at: {}"): "Shot created and WIP file saved at: {}",
    ("*", "Error creating shot: {}"): "Error creating shot: {}",
    ("*", "Configure the following preferences first: {}"): "Configure the following preferences first: {}",
    ("*", "Please select or create a project first."): "Please select or create a project first.",
    ("*", "Add Default Role"): "Add Default Role",
    ("*", "New role description"): "New role description",
    ("*", "Remove Default Role"): "Remove Default Role",
    ("*", "Move Default Role"): "Move Default Role",
    ("*", "Direction"): "Direction",
    ("*", "Direction to move the role"): "Direction to move the role",
    ("*", "Up"): "Up",
    ("*", "Down"): "Down",
    # Assembly Management
    ("*", "Assembly:"): "Assembly:",
    ("*", "Update Assembly"): "Update Assembly",
    ("*", "Check Status"): "Check Status",
    ("*", "Open Assembly"): "Open Assembly",
    ("*", "Rebuild Assembly"): "Rebuild Assembly",
    ("*", "Prepare Render"): "Prepare Render",
    ("*", "Prepare for Render"): "Prepare for Render",
    ("*", "Clean Missing Files"): "Clean Missing Files",
    ("*", "Purge Unused Data"): "Purge Unused Data",
    ("*", "Make Local"): "Make Local",
    ("*", "Pack Resources"): "Pack Resources",
    ("*", "Check Missing Files"): "Check Missing Files",
}

# Brazilian Portuguese
pt_BR: Dict[Tuple[str, str], str] = {
    # General
    ("*", "Project Manager"): "Gerenciador de Projetos",
    ("*", "Project"): "Projeto",
    ("*", "Project:"): "Projeto:",
    ("*", "Shot"): "Shot",
    ("*", "Shot:"): "Shot:",
    ("*", "Role"): "Cargo",
    ("*", "Scene"): "Cena",
    ("*", "Scene:"): "Cena:",
    
    # Actions
    ("*", "New"): "Novo",
    ("*", "Open"): "Abrir",
    ("*", "Create"): "Criar",
    ("*", "Link"): "Linkar",
    ("*", "Publish"): "Publicar",
    ("*", "New Version"): "Nova Versão",
    ("*", "Open Publish"): "Abrir Publish",
    ("*", "New Shot"): "Novo Shot",
    ("*", "Open Shot"): "Abrir Shot",
    ("*", "New Scene"): "Nova Cena",
    ("*", "Open Scene"): "Abrir Cena",
    
    # Project Types
    ("*", "Team"): "Equipe",
    ("*", "Solo"): "Solo",
    
    # Asset Management
    ("*", "Asset Browser"): "Navegador de Assets",
    ("*", "Create Asset"): "Criar Asset",
    
    # Version Control
    ("*", "Versions"): "Versões",
    ("*", "Versions:"): "Versões:",
    ("*", "Last publish"): "Última publicação",
    ("*", "WIP"): "WIP",
    
    # Settings
    ("*", "Settings"): "Configurações",
    ("*", "Preferences"): "Preferências",
    ("*", "Use Versioning"): "Usar Versionamento",
    
    # Messages
    ("*", "Project created successfully"): "Projeto criado com sucesso",
    ("*", "Error creating project"): "Erro ao criar projeto",
    ("*", "Shot created successfully"): "Shot criado com sucesso",
    ("*", "Error creating shot"): "Erro ao criar shot",
    ("*", "Addon is not active"): "O addon não está ativo",
    ("*", "Settings not initialized"): "Configurações não inicializadas",
    ("*", "Error loading interface"): "Erro ao carregar interface",
    
    # Roles
    ("*", "Animation"): "Animação",
    ("*", "Layout"): "Layout",
    ("*", "Lightning"): "Iluminação",
    ("*", "Assembly"): "Assembly",
    ("*", "Roles"): "Cargos",
    ("*", "Roles:"): "Cargos:",
    ("*", "Link Role"): "Vincular Cargo",
    ("*", "Open Role"): "Abrir Cargo",
    
    # Recent Projects
    ("*", "Recent Projects"): "Projetos Recentes",
    ("*", "Recent Projects:"): "Projetos Recentes:",
    ("*", "Clear Recent"): "Limpar Recentes",
    ("*", "Search Projects"): "Buscar Projetos",
    
    # New additions
    ("*", "Create Shot"): "Criar Shot",
    ("*", "Create a new shot or scene"): "Criar um novo shot ou cena",
    ("*", "Mode"): "Modo",
    ("*", "Create a new numbered shot"): "Criar um novo shot numerado",
    ("*", "Single Scene"): "Cena Única",
    ("*", "Create a single scene without numbering"): "Criar uma cena única sem numeração",
    ("*", "Shot Number"): "Número do Shot",
    ("*", "Scene Name"): "Nome da Cena",
    ("*", "Your Role"): "Seu Cargo",
    ("*", "Select your role for this shot"): "Selecione seu cargo para este shot",
    ("*", "Role Settings"): "Configurações de Cargo",
    ("*", "No project selected."): "Nenhum projeto selecionado.",
    ("*", "Role '{}' not configured in preferences."): "Cargo '{}' não configurado nas preferências.",
    ("*", "Shot already exists: {}"): "Shot já existe: {}",
    ("*", "Error creating WIP version"): "Erro ao criar versão WIP",
    ("*", "Shot created and WIP file saved at: {}"): "Shot criado e arquivo WIP salvo em: {}",
    ("*", "Error creating shot: {}"): "Erro ao criar shot: {}",
    ("*", "Configure the following preferences first: {}"): "Configure as seguintes preferências primeiro: {}",
    ("*", "Please select or create a project first."): "Por favor, selecione ou crie um projeto primeiro.",
    ("*", "Add Default Role"): "Adicionar Cargo Padrão",
    ("*", "New role description"): "Descrição do novo cargo",
    ("*", "Remove Default Role"): "Remover Cargo Padrão",
    ("*", "Move Default Role"): "Mover Cargo Padrão",
    ("*", "Direction"): "Direção",
    ("*", "Direction to move the role"): "Direção para mover o cargo",
    ("*", "Up"): "Para Cima",
    ("*", "Down"): "Para Baixo",
    # Assembly Management
    ("*", "Assembly:"): "Assembly:",
    ("*", "Update Assembly"): "Atualizar Assembly",
    ("*", "Check Status"): "Verificar Status",
    ("*", "Open Assembly"): "Abrir Assembly",
    ("*", "Rebuild Assembly"): "Reconstruir Assembly",
    ("*", "Prepare Render"): "Preparar Render",
    ("*", "Prepare for Render"): "Preparar para Render",
    ("*", "Clean Missing Files"): "Limpar Arquivos Faltantes",
    ("*", "Purge Unused Data"): "Limpar Dados Não Utilizados",
    ("*", "Make Local"): "Tornar Local",
    ("*", "Pack Resources"): "Empacotar Recursos",
    ("*", "Check Missing Files"): "Verificar Arquivos Faltantes",
}

# Dictionary mapping language codes to their translation dictionaries
translations = {
    'en_US': en_US,
    'pt_BR': pt_BR,
}

def get_prefs():
    """Get addon preferences"""
    return bpy.context.preferences.addons[__package__.split('.')[0]].preferences

def get_language():
    """Get current language from preferences or system default"""
    prefs = get_prefs()
    if hasattr(prefs, 'language'):
        return prefs.language
    return bpy.app.translations.locale

def translate(text: str, context: str = "*") -> str:
    """
    Translate text using current language.
    Args:
        text: Text to translate
        context: Translation context (default: "*")
    Returns:
        Translated text
    """
    try:
        # Get current language
        lang = get_language()
        
        # Get translation dictionary for current language
        lang_dict = translations.get(lang, en_US)
        
        # Try to get translation
        key = (context, text)
        if key in lang_dict:
            return lang_dict[key]
            
        # Fallback to English
        if lang != 'en_US' and key in en_US:
            return en_US[key]
            
        # If no translation found, return original text
        return text
        
    except Exception as e:
        print(f"Error translating text: {str(e)}")
        return text

def register():
    """Register translations with Blender"""
    try:
        # Register translations for each language
        for lang_code, lang_dict in translations.items():
            bpy.app.translations.register(__package__, {lang_code: lang_dict})
        print(f"Registered translations: {', '.join(translations.keys())}")
    except Exception as e:
        print(f"Error registering translations: {str(e)}")

def unregister():
    """Unregister translations from Blender"""
    try:
        bpy.app.translations.unregister(__package__)
        print("Unregistered translations")
    except Exception as e:
        print(f"Error unregistering translations: {str(e)}") 