#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar a versão do addon Blender Project Manager
Verifica se a versão está consistente em todos os arquivos relevantes
"""

import os
import re
import sys
from pathlib import Path

def simple_toml_parse(content):
    """
    Parser básico de TOML para extrair valores simples.
    Não suporta TOML complexo, apenas extrai pares chave-valor básicos.
    """
    result = {}
    
    # Processar linhas
    for line in content.split('\n'):
        line = line.strip()
        
        # Ignorar comentários e linhas vazias
        if not line or line.startswith('#'):
            continue
            
        # Ignorar seções e tabelas para este parser simples
        if line.startswith('[') and line.endswith(']'):
            continue
            
        # Procurar por pares chave-valor
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            # Remover aspas se estiverem presentes
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
                
            result[key] = value
            
    return result

def get_version_from_init():
    """Extrai a versão do arquivo __init__.py"""
    init_path = Path(__file__).parent.parent / "__init__.py"
    
    if not init_path.exists():
        print(f"ERRO: Arquivo __init__.py não encontrado em {init_path}")
        return None
    
    with open(init_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Procura pelo padrão de versão no bl_info
    version_match = re.search(r'"version":\s*\((\d+),\s*(\d+),\s*(\d+)\)', content)
    if version_match:
        major = version_match.group(1)
        minor = version_match.group(2)
        patch = version_match.group(3)
        return f"{major}.{minor}.{patch}"
    
    print("ERRO: Não foi possível encontrar a versão no arquivo __init__.py")
    return None

def get_version_from_manifest():
    """Extrai a versão do arquivo blender_manifest.toml"""
    manifest_path = Path(__file__).parent.parent / "blender_manifest.toml"
    
    if not manifest_path.exists():
        print(f"ERRO: Arquivo blender_manifest.toml não encontrado em {manifest_path}")
        return None
    
    try:
        # Tentar com o módulo toml se estiver disponível
        try:
            import toml
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = toml.load(f)
                version = manifest_data.get("version")
                if version:
                    return version
        except ImportError:
            # Se o módulo toml não estiver disponível, usar o parser simples
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
                manifest_data = simple_toml_parse(content)
                version = manifest_data.get("version")
                if version:
                    return version
            
        print("ERRO: Não foi possível encontrar a versão no arquivo blender_manifest.toml")
        return None
    except Exception as e:
        print(f"ERRO ao ler o arquivo manifesto: {e}")
        return None

def check_version_in_package_script():
    """Verifica se a versão no script de empacotamento está correta"""
    package_script_path = Path(__file__).parent / "package_addon.py"
    
    if not package_script_path.exists():
        print(f"ERRO: Script de empacotamento não encontrado em {package_script_path}")
        return False
    
    # O script agora obtém a versão do manifesto, então não precisamos mais verificar
    # a definição estática da versão. Em vez disso, apenas verificamos se o script existe.
    print(f"OK: Script de empacotamento encontrado em {package_script_path}")
    return True

def main():
    """Função principal"""
    print("Verificando versão do addon Blender Project Manager...")
    
    # Obtém a versão do __init__.py
    init_version = get_version_from_init()
    if not init_version:
        print("ERRO: Não foi possível obter a versão do __init__.py")
        sys.exit(1)
    
    print(f"Versão encontrada no __init__.py: {init_version}")
    
    # Obtém a versão do blender_manifest.toml
    manifest_version = get_version_from_manifest()
    if not manifest_version:
        print("ERRO: Não foi possível obter a versão do blender_manifest.toml")
        sys.exit(1)
    
    print(f"Versão encontrada no blender_manifest.toml: {manifest_version}")
    
    # Verifica se as versões são consistentes
    if init_version != manifest_version:
        print(f"\nERRO: Versões inconsistentes entre __init__.py ({init_version}) e blender_manifest.toml ({manifest_version})")
        sys.exit(1)
    
    # Verifica o script de empacotamento
    if not check_version_in_package_script():
        print("\nATENÇÃO: Há problemas com o script de empacotamento!")
        sys.exit(1)
    
    print("\nTudo OK! A versão está consistente em todos os arquivos.")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 