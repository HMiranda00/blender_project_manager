#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para empacotar o addon Blender Project Manager como uma extensão do Blender
Compatível com o novo sistema de extensões do Blender 4.0+
"""

import os
import zipfile
import shutil
import datetime
import sys
import subprocess
import json
import re
import argparse
from pathlib import Path

# Obtém o diretório atual (raiz do addon)
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configurações
ADDON_NAME = "blender_project_manager"
EXCLUDE_PATTERNS = [
    ".git",
    ".gitignore",
    "README.md",
    "build_tools",
]

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

def get_version_from_manifest():
    """Extrai a versão do arquivo blender_manifest.toml"""
    manifest_path = os.path.join(SCRIPT_DIR, "blender_manifest.toml")
    try:
        # Tentar primeiro com o módulo toml se estiver disponível
        try:
            import toml
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = toml.load(f)
                return manifest_data.get("version", "0.0.0")
        except ImportError:
            # Se o módulo toml não estiver disponível, usar o parser simples
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
                manifest_data = simple_toml_parse(content)
                return manifest_data.get("version", "0.0.0")
    except Exception as e:
        print(f"Erro ao ler o manifesto: {e}")
        # Se não conseguir ler o manifesto, tentar pegar a versão do bl_info
        return get_version_from_init()

def get_version_from_init():
    """Extrai a versão do arquivo __init__.py como fallback"""
    init_path = os.path.join(SCRIPT_DIR, "__init__.py")
    
    try:
        with open(init_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Procura pelo padrão de versão no bl_info
        version_match = re.search(r'"version":\s*\((\d+),\s*(\d+),\s*(\d+)\)', content)
        if version_match:
            major = version_match.group(1)
            minor = version_match.group(2)
            patch = version_match.group(3)
            return f"{major}.{minor}.{patch}"
    except Exception as e:
        print(f"Erro ao ler a versão do __init__.py: {e}")
    
    return "0.0.0"

VERSION = get_version_from_manifest()

def should_exclude(file_path):
    """Verifica se um arquivo deve ser excluído do pacote"""
    # Normaliza o caminho para comparação
    norm_path = os.path.normpath(file_path)
    
    # Verifica cada padrão de exclusão
    for pattern in EXCLUDE_PATTERNS:
        pattern_norm = os.path.normpath(pattern)
        
        # Verifica se o caminho começa com o padrão (diretório)
        if norm_path.startswith(pattern_norm):
            return True
            
        # Verifica se o caminho é exatamente o padrão (arquivo)
        if norm_path == pattern_norm:
            return True
    
    return False

def create_package():
    """Cria o pacote de extensão para o Blender"""
    os.chdir(SCRIPT_DIR)
    
    # Cria nome do arquivo com data
    today = datetime.datetime.now().strftime("%Y%m%d")
    extension_filename = f"{ADDON_NAME}_{VERSION}_{today}.zip"
    
    # Caminho completo para o arquivo zip
    extension_path = os.path.join(SCRIPT_DIR, "build_tools", extension_filename)
    
    print(f"Empacotando extensão {ADDON_NAME} v{VERSION}...")
    print(f"Diretório base: {SCRIPT_DIR}")
    print(f"Arquivo de saída: {extension_path}")
    
    # Lista de arquivos a serem incluídos
    files_to_include = []
    
    # Verifica se o manifesto existe
    manifest_path = os.path.join(SCRIPT_DIR, "blender_manifest.toml")
    if not os.path.exists(manifest_path):
        print(f"ERRO: O arquivo blender_manifest.toml não existe em {SCRIPT_DIR}")
        print("É necessário criar este arquivo para o novo sistema de extensões do Blender.")
        return
    
    # Percorre todos os arquivos e diretórios
    for root, dirs, files in os.walk('.'):
        # Remove diretórios excluídos da lista para evitar percorrê-los
        dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d)[2:] if root.startswith('./') or root.startswith('.\\') else os.path.join(root, d))]
        
        for file in files:
            # Normaliza o caminho do arquivo
            if root == '.':
                file_path = file
            else:
                # Remove o ./ ou .\ do início do caminho
                if root.startswith('./') or root.startswith('.\\'):
                    file_path = os.path.join(root[2:], file)
                else:
                    file_path = os.path.join(root, file)
            
            # Verifica se deve excluir
            if should_exclude(file_path):
                print(f"Excluindo: {file_path}")
                continue
            
            # Adiciona à lista de arquivos a incluir
            files_to_include.append(file_path)
    
    # Cria o arquivo zip
    os.makedirs(os.path.dirname(extension_path), exist_ok=True)
    with zipfile.ZipFile(extension_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files_to_include:
            # Adiciona ao zip com o caminho correto (não incluir pasta raiz no caminho)
            print(f"Adicionando: {file_path}")
            zipf.write(file_path, file_path)
    
    # Verifica se o arquivo foi criado
    if os.path.exists(extension_path):
        print(f"\nExtensão criada com sucesso: {extension_path}")
        print(f"Tamanho: {os.path.getsize(extension_path) / 1024:.2f} KB")
        
        print("\nNOTA: Para instalar esta extensão no Blender:")
        print("1. Abra o Blender 4.0 ou superior")
        print("2. Vá para Edit > Preferences > Add-ons > Install")
        print("3. Selecione o arquivo .zip criado")
        print("4. Ative a extensão na lista")
    else:
        print(f"\nERRO: Falha ao criar a extensão: {extension_path}")
        
    return extension_path

def install_directly(target_dir=None):
    """
    Instala a extensão diretamente no diretório de extensões do Blender
    
    1. Fecha o Blender se estiver aberto
    2. Limpa o diretório da extensão
    3. Copia os novos arquivos
    """
    os.chdir(SCRIPT_DIR)
    
    # Define o diretório padrão de extensões se não for especificado
    if not target_dir:
        # Diretório padrão para Windows
        if os.name == 'nt':
            appdata = os.getenv('APPDATA')
            target_dir = os.path.join(appdata, 'Blender Foundation', 'Blender', '4.3', 'extensions', 'user_default', ADDON_NAME)
        # Diretório padrão para Linux
        else:
            home = os.path.expanduser("~")
            target_dir = os.path.join(home, '.config', 'blender', '4.3', 'extensions', 'user_default', ADDON_NAME)
    
    # Verifica se o diretório existe
    if not os.path.exists(os.path.dirname(target_dir)):
        print(f"ERRO: O diretório de extensões não existe: {os.path.dirname(target_dir)}")
        print("Por favor, verifique o caminho e tente novamente.")
        return
    
    print(f"Instalando extensão diretamente em: {target_dir}")
    
    # 1. Tentar fechar o Blender (Windows)
    print("Tentando fechar o Blender (se estiver aberto)...")
    try:
        if os.name == 'nt':
            subprocess.run(["taskkill", "/f", "/im", "blender.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("Blender fechado com sucesso.")
        else:
            # Em Linux/Mac, apenas emite um aviso
            print("AVISO: Em sistemas Linux/Mac, o Blender deve ser fechado manualmente antes de continuar.")
            input("Pressione ENTER para continuar quando o Blender estiver fechado...")
    except Exception as e:
        print(f"Aviso: Não foi possível fechar o Blender automaticamente: {e}")
        print("Por favor, feche o Blender manualmente antes de continuar.")
        input("Pressione ENTER para continuar quando o Blender estiver fechado...")
    
    # 2. Limpar o diretório da extensão se existir
    if os.path.exists(target_dir):
        print(f"Limpando diretório existente: {target_dir}")
        try:
            for item in os.listdir(target_dir):
                item_path = os.path.join(target_dir, item)
                if os.path.isfile(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
        except Exception as e:
            print(f"ERRO ao limpar diretório: {e}")
            return
    else:
        print(f"Criando diretório: {target_dir}")
        os.makedirs(target_dir, exist_ok=True)
    
    # 3. Copiar os novos arquivos
    print("Copiando novos arquivos...")
    
    # Lista de arquivos a serem incluídos (reutilizar lógica)
    files_copied = 0
    
    for root, dirs, files in os.walk('.'):
        # Remove diretórios excluídos da lista para evitar percorrê-los
        dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d)[2:] if root.startswith('./') or root.startswith('.\\') else os.path.join(root, d))]
        
        for file in files:
            # Normaliza o caminho do arquivo
            if root == '.':
                file_path = file
                target_path = os.path.join(target_dir, file)
            else:
                # Remove o ./ ou .\ do início do caminho
                if root.startswith('./') or root.startswith('.\\'):
                    rel_path = root[2:]
                else:
                    rel_path = root
                file_path = os.path.join(rel_path, file)
                target_path = os.path.join(target_dir, file_path)
            
            # Verifica se deve excluir
            if should_exclude(file_path):
                continue
            
            # Cria a estrutura de diretórios, se necessário
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
            # Copia o arquivo
            try:
                shutil.copy2(file_path, target_path)
                print(f"Copiado: {file_path}")
                files_copied += 1
            except Exception as e:
                print(f"ERRO ao copiar {file_path}: {e}")
    
    print(f"\nInstalação direta concluída! {files_copied} arquivos copiados para {target_dir}")
    print("\nAgora você pode abrir o Blender para usar a extensão atualizada.")

def try_build_with_blender_cli():
    """Tenta construir a extensão usando a CLI do Blender (método recomendado)"""
    print("\nTentando construir a extensão usando a ferramenta de linha de comando do Blender...")
    
    try:
        # Tenta encontrar o executável do Blender
        blender_path = "blender"  # Assumindo que está no PATH
        
        # Comando para construir a extensão
        cmd = [blender_path, "--background", "--python-expr", 
               "import bpy; bpy.ops.wm.extension_build()"]
        
        print(f"Executando: {' '.join(cmd)}")
        
        # Executa o comando
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Extensão construída com sucesso usando a CLI do Blender!")
            print("\nSaída do comando:")
            print(result.stdout)
            return True
        else:
            print("Falha ao construir a extensão usando a CLI do Blender.")
            print("\nErro:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"Erro ao tentar usar a CLI do Blender: {e}")
        return False

if __name__ == "__main__":
    # Configurar argumentos de linha de comando
    parser = argparse.ArgumentParser(description='Empacota e instala a extensão Blender Project Manager')
    parser.add_argument('--install', action='store_true', help='Instala diretamente no diretório de extensões')
    parser.add_argument('--target-dir', type=str, help='Diretório de instalação específico (somente com --install)')
    parser.add_argument('--force', action='store_true', help='Força a instalação sem perguntar')
    
    args = parser.parse_args()
    
    if args.install:
        if not args.force:
            print("\nAVISO: Esta operação fechará o Blender (se estiver aberto) e substituirá a extensão existente.")
            confirm = input("Deseja continuar? (s/N): ")
            if confirm.lower() != 's':
                print("Operação cancelada pelo usuário.")
                sys.exit(0)
        
        install_directly(args.target_dir)
    else:
        # Tenta construir usando a CLI do Blender primeiro (método recomendado)
        if not try_build_with_blender_cli():
            print("\nUsando método alternativo de empacotamento...")
            create_package()
        
        # Exibe instruções para instalação direta
        print("\nPara instalar diretamente (sem criar um arquivo .zip), execute novamente com:")
        print("python build_tools/package_addon.py --install")
        print("\nPara especificar um diretório de instalação personalizado:")
        print("python build_tools/package_addon.py --install --target-dir \"C:\\caminho\\para\\extensoes\\blender_project_manager\"") 