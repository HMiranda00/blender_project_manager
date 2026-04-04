# Arquitetura do Blender Project Manager

## 1) Visao geral

O add-on e estruturado em tres camadas:

- `panels/`: UI principal no N-Panel (`VIEW3D_PT_project_management`).
- `operators/`: casos de uso (criar projeto, shot, WIP, publish, assembly, assets).
- `utils/`: funcoes compartilhadas (paths, estrutura de projeto, versionamento e cache).

Ponto de entrada:

- `__init__.py`: registra `preferences`, `operators`, `panels` e propriedades da `Scene`.

## 2) Modelo de dados

### Estado em `bpy.types.Scene`

- `current_project`: caminho absoluto do projeto.
- `current_shot`: shot ativo.
- `current_role`: role/departamento ativo.
- `previous_file`: arquivo anterior (fluxo de assembly).
- `show_asset_manager`, `show_role_status`: flags de UI.

### Configuracao em `AddonPreferences`

Arquivo: `preferences.py`.

- Root:
  - `use_fixed_root`
  - `fixed_root_path`
- Roles (`role_mappings`):
  - nome, descricao, icone, cor, visibilidade, `link_type`, `skip_assembly`, `owns_world`
  - politica de publish (`publish_path_preset` ou `custom_publish_path`)
- Projetos recentes (`recent_projects`).

## 3) Fluxos principais

### Criacao e carga de projeto

1. `project.create_project` cria pasta base + workspace (`3D` ou `03 - 3D`).
2. `utils.create_project_structure()` cria `SHOTS`, `ASSETS 3D/PROPS|CHR|ENV`.
3. `project.setup_asset_browser` cria biblioteca de assets e catalogs.
4. `utils.get_project_info()` centraliza a resolucao de `workspace_path`:
   - aceita raiz de projeto ou a pasta de workspace como entrada;
   - em `fixed root`, prefere `03 - 3D`, mas reaproveita `3D` quando estiver lidando com projeto legado ou selecao manual;
   - nunca retorna `workspace_path` indefinido, mesmo que o nome da pasta nao siga o padrao `NNN - Nome`.

### Fluxo Shot/Role

1. `project.create_shot` cria estrutura do shot/role (`WIP` e `PUBLISH`).
2. Abre arquivo limpo (`wm.read_homefile(use_empty=True)`), cria collection principal.
3. Cria primeiro WIP e copia para publish.
4. Cria/atualiza arquivo de assembly do shot.

### Versionamento

- `project.new_wip_version`: incrementa `v###`.
- `project.publish_version`: copia ultimo WIP para publish.
- `project.open_version_list` e `project.open_latest_wip`: navegacao entre versoes.

### Assembly

- `project.open_assembly`: abre/cria assembly do shot.
- `project.rebuild_assembly`: relinka colecoes publicadas das roles.
- `project.prepare_assembly_render`: gera copia local pronta para render.

### Assets

- `project.create_asset`: cria/marca asset (novo arquivo, save as ou mark only).
- `project.reload_links`: recarrega bibliotecas linkadas.
- `project.toggle_asset_browser`: abre/fecha area do asset browser.

## 4) Dependencias e acoplamentos

- Forte acoplamento UI <-> filesystem <-> operador Blender.
- Muitos operadores fazem `wm.open_mainfile`, o que troca contexto global.
- Convencoes de nome sao centrais:
  - WIP: `{prefix}_{shot}_{role}_v###.blend`
  - Publish: `{prefix}_{shot}_{role}.blend`
  - Assembly: `{prefix}_{shot}_ASSEMBLY.blend`

## 5) Divida tecnica atual (prioritaria)

1. `bl_idname` duplicado para `project.toggle_asset_browser`:
   - `operators/asset_browser_setup.py`
   - `operators/asset_browser_view.py`
2. Funcoes duplicadas:
   - `get_project_info` em `utils/core.py` e `utils/__init__.py`
   - `get_wip_path` em `utils/version_control.py` e `operators/version_control.py`
3. Baseline de compatibilidade declarada desatualizada:
   - `bl_info["blender"] = (2, 80, 0)` em `__init__.py`.
4. Handlers sem `@persistent` em `operators/asset_browser_setup.py` (podem ser limpos ao carregar arquivo).
5. Ausencia de separacao clara entre "dominio pipeline" e "adapter Blender API".

## 6) Arquitetura alvo recomendada

### Curto prazo

- Consolidar funcoes duplicadas em `utils/core.py` e `utils/version_control.py`.
- Ter apenas um operador `project.toggle_asset_browser`.
- Introduzir `services/` para regras de negocio sem `bpy.ops` quando possivel.
- Validar selecao manual de projeto na carga (`project.load_project`) para distinguir raiz de projeto vs workspace e normalizar `scene.current_project`.

### Medio prazo

- Criar camadas:
  - `domain/` (modelo pipeline: projeto, shot, role, versao)
  - `infrastructure/` (filesystem, naming, config)
  - `adapters/blender/` (operadores e integracao com `bpy`)

Isso prepara o projeto para evoluir para outros DCCs (After Effects, por exemplo).
