import bpy
from typing import List, Callable, Any, Dict, Type

# Armazena classes e funções para registro
_classes_to_register: List[Type] = []
_register_hooks: List[Callable] = []
_unregister_hooks: List[Callable] = []
_property_groups: Dict[str, Dict[str, Any]] = {}

def register_class(cls: Type) -> Type:
    """
    Decorador para registrar uma classe.
    
    Exemplo de uso:
    @register_class
    class MyOperator(bpy.types.Operator):
        ...
    """
    _classes_to_register.append(cls)
    return cls

def register_property_group(target_type: str, prop_name: str, prop_def: Any) -> None:
    """
    Registra uma propriedade para ser adicionada a um tipo de blender
    
    Args:
        target_type: String com o nome do tipo (ex: "Scene")
        prop_name: String com o nome da propriedade
        prop_def: Definição da propriedade
    
    Exemplo:
    register_property_group("Scene", "current_project", StringProperty(name="Current Project"))
    """
    if target_type not in _property_groups:
        _property_groups[target_type] = {}
    _property_groups[target_type][prop_name] = prop_def

def register_hook(register_func: Callable = None, unregister_func: Callable = None) -> None:
    """
    Registra hooks para serem chamados durante registro/desregistro
    
    Args:
        register_func: Função a ser chamada durante o registro
        unregister_func: Função a ser chamada durante o desregistro
    """
    if register_func:
        _register_hooks.append(register_func)
    if unregister_func:
        _unregister_hooks.append(unregister_func)

def register_all() -> None:
    """Registra todas as classes e executa hooks de registro"""
    # Registrar todas as classes
    for cls in _classes_to_register:
        bpy.utils.register_class(cls)
    
    # Registrar property groups
    for target_type, props in _property_groups.items():
        target = getattr(bpy.types, target_type)
        for prop_name, prop_def in props.items():
            setattr(target, prop_name, prop_def)
    
    # Executar hooks de registro
    for hook in _register_hooks:
        hook()

def unregister_all() -> None:
    """Desregistra tudo na ordem inversa"""
    # Executar hooks de desregistro na ordem inversa
    for hook in reversed(_unregister_hooks):
        hook()
    
    # Remover property groups
    for target_type, props in _property_groups.items():
        target = getattr(bpy.types, target_type)
        for prop_name in props:
            delattr(target, prop_name)
    
    # Desregistrar classes na ordem inversa
    for cls in reversed(_classes_to_register):
        bpy.utils.unregister_class(cls) 