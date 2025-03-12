#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para instalar diretamente a extensão Blender Project Manager
no diretório de extensões do Blender 4.3
"""

import os
import shutil
import subprocess
import sys
import time
import re

# Caminho de destino (padrão para Windows)
TARGET_DIR = r"C:\Users\HenriqueMiranda\AppData\Roaming\Blender Foundation\Blender\4.3\extensions\user_default\blender_project_manager"

# Caminho para o executável do Blender (Windows padrão)
BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe"

# Obtém o diretório atual (raiz do addon)
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Arquivos e diretórios para excluir da cópia
EXCLUDE_PATTERNS = [
    ".git",
    ".gitignore",
    "README.md",
    "build_tools",
    "__pycache__",
    "*.pyc",
    ".vscode",
    ".idea",
    ".DS_Store",
    "Thumbs.db",
    "*.blend1",
    "*.blend2",
    "*.blend3",
    "temp",
    "cache",
    "logs",
    "*.zip",
    "dist",
    "other scripts",
]

# Lista de arquivos e diretórios obrigatórios
REQUIRED_FILES = [
    "manifest.toml",
    "__init__.py",
    "operators",
    "panels",
    "preferences",
    "utils",
    "integration",
    "handlers.py",
    "README.md",
]

def should_exclude(file_path):
    """Verifica se um arquivo deve ser excluído da cópia"""
    # Converte para caminho relativo se for absoluto
    if os.path.isabs(file_path):
        rel_path = os.path.relpath(file_path, SCRIPT_DIR)
    else:
        rel_path = file_path
    
    # Normaliza o caminho para comparação
    norm_path = os.path.normpath(rel_path)
    
    # Verifica cada padrão de exclusão
    for pattern in EXCLUDE_PATTERNS:
        # Caso seja um padrão glob com asterisco
        if '*' in pattern:
            if re.match(pattern.replace('*', '.*'), norm_path):
                return True
        # Verifica diretório ou arquivo exato
        elif norm_path == pattern or norm_path.startswith(pattern + os.path.sep):
            return True
        # Verifica se é um arquivo com a extensão a ser excluída
        elif pattern.startswith('*.') and norm_path.endswith(pattern[1:]):
            return True
    
    # Arquivo não deve ser excluído
    return False

def install_directly():
    """
    Instala a extensão diretamente no diretório de extensões do Blender
    
    1. Fecha o Blender se estiver aberto
    2. Limpa o diretório da extensão
    3. Copia os novos arquivos
    4. Abre o Blender ao concluir
    """
    print(f"Diretório atual: {os.getcwd()}")
    print(f"SCRIPT_DIR: {SCRIPT_DIR}")
    os.chdir(SCRIPT_DIR)
    print(f"Mudou para diretório: {os.getcwd()}")
    
    print(f"Instalando extensão diretamente em: {TARGET_DIR}")
    
    # 1. Tentar fechar o Blender (Windows)
    print("Tentando fechar o Blender (se estiver aberto)...")
    try:
        if os.name == 'nt':
            subprocess.run(["taskkill", "/f", "/im", "blender.exe"], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            print("Blender fechado com sucesso (ou não estava aberto).")
    except Exception as e:
        print(f"Aviso: Não foi possível fechar o Blender automaticamente: {e}")
        print("Continuando mesmo assim...")
    
    # 2. Limpar o diretório da extensão se existir
    if os.path.exists(TARGET_DIR):
        print(f"Limpando diretório existente: {TARGET_DIR}")
        try:
            for item in os.listdir(TARGET_DIR):
                item_path = os.path.join(TARGET_DIR, item)
                if os.path.isfile(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
        except Exception as e:
            print(f"ERRO ao limpar diretório: {e}")
            return
    else:
        print(f"Criando diretório: {TARGET_DIR}")
        os.makedirs(TARGET_DIR, exist_ok=True)
    
    # 3. Verificar arquivos obrigatórios
    print("Verificando arquivos obrigatórios...")
    missing_files = []
    for req_file in REQUIRED_FILES:
        req_path = os.path.join(SCRIPT_DIR, req_file)
        if not os.path.exists(req_path):
            missing_files.append(req_file)
            print(f"AVISO: Arquivo ou diretório obrigatório não encontrado: {req_file}")
    
    if missing_files:
        print(f"AVISO: {len(missing_files)} arquivos obrigatórios não encontrados.")
        resposta = input("Deseja continuar mesmo assim? (s/n): ")
        if resposta.lower() != 's':
            print("Instalação cancelada.")
            return
    
    # 4. Copiar os novos arquivos
    print("Copiando novos arquivos...")
    files_copied = 0
    
    # Criar arquivo handlers/__init__.py se não existir
    handlers_dir = os.path.join(TARGET_DIR, "handlers")
    os.makedirs(handlers_dir, exist_ok=True)
    handlers_init = os.path.join(handlers_dir, "__init__.py")
    if not os.path.exists(os.path.join(SCRIPT_DIR, "handlers", "__init__.py")):
        with open(handlers_init, 'w') as f:
            f.write('"""\nHandlers module for Blender Project Manager.\n"""\n\ndef register():\n    pass\n\ndef unregister():\n    pass\n')
        print(f"Criado: handlers/__init__.py")
        files_copied += 1
    
    # Copiar todos os arquivos e diretórios, exceto os excluídos
    for root, dirs, files in os.walk(SCRIPT_DIR):
        # Ignora os diretórios na lista de exclusão
        dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
        
        # Processa cada arquivo
        for file in files:
            file_path = os.path.join(root, file)
            
            # Verifica se deve excluir este arquivo
            if should_exclude(file_path):
                continue
            
            # Calcula o caminho relativo e de destino
            rel_path = os.path.relpath(file_path, SCRIPT_DIR)
            target_path = os.path.join(TARGET_DIR, rel_path)
            
            # Cria a estrutura de diretórios necessária
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
            # Copia o arquivo
            try:
                shutil.copy2(file_path, target_path)
                print(f"Copiado: {rel_path}")
                files_copied += 1
            except Exception as e:
                print(f"ERRO ao copiar {rel_path}: {e}")
    
    # 5. Verificar se o manifest.toml foi copiado, caso contrário, criar um
    manifest_path = os.path.join(TARGET_DIR, "manifest.toml")
    if not os.path.exists(manifest_path):
        print("Criando manifest.toml...")
        with open(manifest_path, 'w') as f:
            f.write('# manifest.toml for Blender Project Manager\n\n')
            f.write('display_name = "Blender Project Manager"\n')
            f.write('description = "Project management for complex Blender projects"\n')
            f.write('publisher = "Henrique Miranda"\n')
            f.write('version = "1.6.2"\n')
            f.write('blender_version_min = "3.0.0"\n')
            f.write('license = "GPL-3.0-or-later"\n')
            f.write('tags = ["Pipeline", "Project Management", "Organization"]\n')
            f.write('language = "python"\n')
            f.write('category = "Pipeline"\n\n')
            f.write('[repository]\n')
            f.write('url = "https://github.com/HMiranda00/blender_project_manager"\n\n')
            f.write('[documentation]\n')
            f.write('url = "https://docs.henriquemiranda.com.br/blender-project-manager/"\n\n')
            f.write('[tracker]\n')
            f.write('url = "https://github.com/HMiranda00/blender_project_manager/issues"\n')
        print("Criado: manifest.toml")
        files_copied += 1
    
    print(f"\nInstalação direta concluída! {files_copied} arquivos copiados para {TARGET_DIR}")
    
    # 6. Abrir o Blender automaticamente
    print("\nAbrindo o Blender...")
    try:
        if os.path.exists(BLENDER_EXE):
            subprocess.Popen([BLENDER_EXE])
            print(f"Blender iniciado com sucesso: {BLENDER_EXE}")
        else:
            try:
                subprocess.Popen(["blender"])
                print("Blender iniciado via comando 'blender'")
            except:
                print("AVISO: Não foi possível encontrar o executável do Blender.")
                print("Por favor, abra o Blender manualmente.")
    except Exception as e:
        print(f"ERRO ao abrir o Blender: {e}")
        print("Por favor, abra o Blender manualmente.")

if __name__ == "__main__":
    print("\nInstalando extensão diretamente no Blender 4.3...")
    install_directly() 