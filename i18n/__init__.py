"""
Internationalization module
"""
import bpy
import os
import json
from bpy.app.translations import pgettext_iface as iface_
from bpy.app.translations import register, unregister

# Translation dictionary
translations_dict = {}

def translate(text):
    """Translate text using the current language"""
    try:
        # Get current language
        lang = bpy.context.preferences.view.language
        
        # If not English and we have translations
        if lang != 'en_US' and translations_dict:
            # Try to get translation
            if text in translations_dict.get(lang, {}):
                return translations_dict[lang][text]
        
        # Return original text if no translation found
        return text
    except:
        return text

def load_translations():
    """Load translations from JSON files"""
    global translations_dict
    
    try:
        # Get addon path
        addon_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        i18n_path = os.path.join(addon_path, "i18n")
        
        # Load each translation file
        for filename in os.listdir(i18n_path):
            if filename.endswith(".json"):
                lang_code = filename.split(".")[0]
                file_path = os.path.join(i18n_path, filename)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        translations_dict[lang_code] = json.load(f)
                except Exception as e:
                    print(f"Error loading translation file {filename}: {str(e)}")
                    continue
        
        return True
    except Exception as e:
        print(f"Error loading translations: {str(e)}")
        return False

def register():
    """Register translation support"""
    try:
        # First unregister if already registered
        try:
            unregister()
        except:
            pass
            
        # Load translations
        if not load_translations():
            print("Warning: Failed to load translations")
            return
            
        # Register with Blender
        register(translations_dict)
        
    except Exception as e:
        print(f"Error registering translations: {str(e)}")

def unregister():
    """Unregister translation support"""
    try:
        unregister()
    except:
        pass

__all__ = [
    'register',
    'unregister',
    'translate',
    'translations',
    'en_US',
    'pt_BR'
] 
