import bpy

def fix_addon_registration():
    """Tenta corrigir o registro do addon"""
    addon_name = "gerenciador_projetos"
    
    # Primeiro, vamos tentar desregistrar o addon completamente
    if addon_name in bpy.context.preferences.addons:
        try:
            bpy.ops.preferences.addon_disable(module=addon_name)
            print("Addon desabilitado com sucesso")
        except Exception as e:
            print(f"Erro ao desabilitar addon: {str(e)}")
    
    # Limpar propriedades que podem estar causando conflito
    properties_to_clear = [
        "project_settings",
        "current_project",
        "current_shot",
        "current_role",
        "show_asset_manager",
        "show_role_status"
    ]
    
    for prop in properties_to_clear:
        if hasattr(bpy.types.Scene, prop):
            try:
                delattr(bpy.types.Scene, prop)
                print(f"Propriedade {prop} removida com sucesso")
            except Exception as e:
                print(f"Erro ao remover propriedade {prop}: {str(e)}")
    
    # Limpar propriedades do WindowManager
    wm_props = [
        "assembly_previous_file",
        "assembly_progress"
    ]
    
    for prop in wm_props:
        if hasattr(bpy.types.WindowManager, prop):
            try:
                delattr(bpy.types.WindowManager, prop)
                print(f"Propriedade WM {prop} removida com sucesso")
            except Exception as e:
                print(f"Erro ao remover propriedade WM {prop}: {str(e)}")
    
    # Reabilitar o addon
    try:
        bpy.ops.preferences.addon_enable(module=addon_name)
        print("Addon reabilitado com sucesso")
    except Exception as e:
        print(f"Erro ao reabilitar addon: {str(e)}")
    
    return "Processo de correção concluído"

if __name__ == "__main__":
    print("\n=== INICIANDO CORREÇÃO DO REGISTRO ===")
    result = fix_addon_registration()
    print(result)
    print("=====================================\n") 