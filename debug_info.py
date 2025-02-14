import bpy
import os

def check_addon_state():
    """Verifica o estado atual do addon e suas dependências"""
    info = []
    
    # Verificar se o addon está registrado
    if 'gerenciador_projetos' in bpy.context.preferences.addons:
        info.append("Addon está registrado")
        
        # Verificar preferências
        prefs = bpy.context.preferences.addons['gerenciador_projetos'].preferences
        info.append(f"Número de cargos configurados: {len(prefs.role_mappings)}")
        
        # Listar cargos configurados
        info.append("\nCargos configurados:")
        for role in prefs.role_mappings:
            info.append(f"- {role.role_name} (Ícone: {role.icon})")
    else:
        info.append("Addon não está registrado!")
    
    # Verificar propriedades da cena
    info.append("\nPropriedades da cena:")
    if hasattr(bpy.types.Scene, "project_settings"):
        info.append("- project_settings: OK")
    else:
        info.append("- project_settings: FALTANDO")
    
    if hasattr(bpy.types.Scene, "current_project"):
        info.append("- current_project: OK")
    else:
        info.append("- current_project: FALTANDO")
    
    if hasattr(bpy.types.Scene, "current_shot"):
        info.append("- current_shot: OK")
    else:
        info.append("- current_shot: FALTANDO")
    
    if hasattr(bpy.types.Scene, "current_role"):
        info.append("- current_role: OK")
    else:
        info.append("- current_role: FALTANDO")
    
    # Verificar operadores
    info.append("\nOperadores principais:")
    operators_to_check = [
        "project.create_project",
        "project.create_shot",
        "project.link_role",
        "project.rebuild_assembly"
    ]
    
    for op_id in operators_to_check:
        if hasattr(bpy.types, op_id.replace(".", "_OT_")):
            info.append(f"- {op_id}: OK")
        else:
            info.append(f"- {op_id}: FALTANDO")
    
    return "\n".join(info)

def check_role_mappings():
    """Verifica as configurações de cargos"""
    info = []
    
    try:
        prefs = bpy.context.preferences.addons['gerenciador_projetos'].preferences
        settings = bpy.context.scene.project_settings
        
        if settings.project_type == 'TEAM':
            # Verificar cargo Assembly
            has_assembly = False
            for role in prefs.role_mappings:
                if role.role_name.upper() == "ASSEMBLY":
                    has_assembly = True
                    info.append("\n=== CARGO ASSEMBLY ===")
                    info.append(f"Nome: {role.role_name}")
                    info.append(f"Descrição: {role.description}")
                    info.append(f"Link: {role.link_type}")
                    info.append(f"Ícone: {role.icon}")
                    break
                    
            if not has_assembly:
                info.append("\nAVISO: Cargo Assembly não encontrado!")
        
        info.append("\n=== CARGOS CONFIGURADOS ===")
        for role in prefs.role_mappings:
            if settings.project_type == 'TEAM':
                if role.role_name.upper() != "ASSEMBLY":
                    info.append(f"\nCargo: {role.role_name}")
                    info.append(f"- Nome: {role.description}")
                    info.append(f"- Link: {role.link_type}")
                    info.append(f"- Ícone: {role.icon}")
            else:
                info.append(f"\nCargo: {role.role_name}")
                info.append(f"- Nome: {role.description}")
                info.append(f"- Link: {role.link_type}")
                info.append(f"- Ícone: {role.icon}")
    except Exception as e:
        info.append(f"Erro ao verificar cargos: {str(e)}")
    
    return "\n".join(info)

def check_project_mode(context):
    """Verifica o modo do projeto e suas configurações"""
    info = []
    
    try:
        if hasattr(context.scene, "project_settings"):
            settings = context.scene.project_settings
            info.append(f"\nModo do Projeto: {settings.project_type}")
            info.append(f"Tipo de Link: {settings.asset_linking}")
            info.append(f"Versionamento: {'Ativo' if settings.use_versioning else 'Inativo'}")
            
            # Verificar configurações específicas do modo
            if settings.project_type == 'TEAM':
                info.append("\nVerificação do modo Equipe:")
                # Verificar estrutura de assembly
                project_path = context.scene.current_project
                if project_path:
                    prefs = context.preferences.addons['gerenciador_projetos'].preferences
                    _, workspace_path, _ = get_project_info(project_path, prefs.use_fixed_root)
                    assembly_path = os.path.join(workspace_path, "SHOTS", "ASSEMBLY")
                    
                    if os.path.exists(assembly_path):
                        info.append("- Pasta ASSEMBLY: OK")
                    else:
                        info.append("- Pasta ASSEMBLY: FALTANDO")
            else:
                info.append("\nVerificação do modo Solo:")
                # Verificar estrutura simplificada
                if context.scene.current_project:
                    info.append("- Projeto carregado: OK")
                    if context.scene.current_shot:
                        info.append("- Shot/Cena atual: OK")
                        # Verificar estrutura de cena
                        project_path = context.scene.current_project
                        prefs = context.preferences.addons['gerenciador_projetos'].preferences
                        _, workspace_path, _ = get_project_info(project_path, prefs.use_fixed_root)
                        scene_path = os.path.join(workspace_path, "SCENES", context.scene.current_shot)
                        if os.path.exists(scene_path):
                            info.append("- Pasta da cena: OK")
                        else:
                            info.append("- Pasta da cena: FALTANDO")
                    else:
                        info.append("- Shot/Cena atual: FALTANDO")
                else:
                    info.append("- Nenhum projeto carregado")
        else:
            info.append("\nERRO: Configurações do projeto não encontradas!")
            
    except Exception as e:
        info.append(f"\nErro ao verificar modo do projeto: {str(e)}")
    
    return "\n".join(info)

def print_debug_info():
    """Imprime informações de debug no console"""
    print("\n=== DIAGNÓSTICO DO GERENCIADOR DE PROJETOS ===")
    print(check_addon_state())
    print("\n=== MODO DO PROJETO ===")
    print(check_project_mode(bpy.context))
    print("\n=== CONFIGURAÇÕES DE CARGOS ===")
    print(check_role_mappings())
    print("============================================\n")

if __name__ == "__main__":
    print_debug_info() 