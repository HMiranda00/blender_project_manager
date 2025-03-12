# Scripts de Empacotamento - Blender Project Manager

Esta pasta contém scripts para empacotar o addon Blender Project Manager como uma extensão do Blender 4.0+.

## Arquivos Disponíveis

- `package_addon.py` - Script Python principal para empacotar o addon como extensão
- `package_addon.bat` - Script batch para Windows
- `package_addon.sh` - Script shell para sistemas Unix/Linux
- `check_version.py` - Script para verificar a consistência da versão do addon

## Como Usar

### Método Recomendado (usando a CLI do Blender)

O método recomendado para criar uma extensão é usar a ferramenta de linha de comando do Blender:

1. Abra um terminal na pasta raiz do projeto
2. Execute: `blender --background --python-expr "import bpy; bpy.ops.wm.extension_build()"`

O script `package_addon.py` tentará usar este método primeiro e, se falhar, usará o método alternativo.

### Método Alternativo

#### No Windows

1. Dê um duplo clique no arquivo `package_addon.bat`
2. O script irá criar um arquivo zip na pasta `build_tools` com o nome `blender_project_manager_[versão]_[data].zip`

#### No Linux/Mac

1. Abra um terminal na pasta `build_tools`
2. Execute o comando: `chmod +x package_addon.sh`
3. Execute o script: `./package_addon.sh`
4. O script irá criar um arquivo zip na pasta `build_tools` com o nome `blender_project_manager_[versão]_[data].zip`

### Verificar Versão

Para verificar se a versão do addon está consistente em todos os arquivos:

```
python check_version.py
```

## Diferenças do Sistema de Extensões

O novo sistema de extensões do Blender 4.0+ introduz algumas mudanças importantes:

1. Usa um arquivo `blender_manifest.toml` para metadados em vez de `bl_info` no `__init__.py`
2. Requer uma estrutura de pacote específica
3. De preferência, deve ser construído usando a CLI do Blender

## O que é Incluído no Pacote

O script de empacotamento inclui todos os arquivos necessários para o funcionamento do addon, excluindo:

- Arquivos de controle de versão (`.git/`, `.gitignore`)
- Documentação (README.md)
- Scripts de empacotamento (pasta `build_tools/`)

## Instalação da Extensão

Para instalar a extensão no Blender:

1. Abra o Blender 4.0 ou superior
2. Vá para Edit > Preferences > Add-ons > Install
3. Selecione o arquivo .zip criado
4. Ative a extensão na lista 