# Report de Alinhamento com Blender 5.0.1

Data do report: 2026-03-03

## Status Atual (apos implementacao)

Este report foi atualizado apos implementacao das correcoes P0/P1, testes puros e smoke tests com `bpy`.

## Correcoes Implementadas

### P0 concluido

1. Duplicidade de operador removida:
   - `project.toggle_asset_browser` agora tem implementacao canonica em `operators/asset_browser_setup.py`.
   - `operators/asset_browser_view.py` foi desativado como modulo legado (sem registro de operador).
2. Consolidacao de utilitarios duplicados:
   - `get_project_info` centralizado em `utils/core.py`.
   - `get_wip_path` centralizado em `utils/version_control.py` com wrapper de compatibilidade em `operators/version_control.py`.
3. Registro/desregistro endurecido:
   - `register()/unregister()` do asset browser tornados idempotentes e simetricos.

### P1 concluido

1. Baseline Blender atualizado no add-on metadata:
   - `bl_info["blender"] = (4, 4, 0)`.
2. Handlers persistentes:
   - `on_file_change` e `on_undo_redo` marcados com `@persistent`.
3. Logging padronizado:
   - substituicao de `print` em modulos criticos tocados.
4. Robustez de contexto:
   - ajustes em fluxos sensiveis com troca de arquivo (`open_mainfile`), com restauracao de contexto em operadores relevantes.

## Melhorias de Testabilidade e Qualidade

1. Regras puras de pipeline adicionadas:
   - `utils/pipeline_rules.py` (naming/path/version).
2. Testes unitarios puros (sem Blender runtime):
   - `tests/test_pipeline_rules.py`.
3. Script de execucao de testes:
   - `scripts/run_unit_tests.ps1` com fallback para Python local (ignora stub WindowsApps).
4. Smoke runner com `bpy` headless:
   - `scripts/blender_smoke_runner.py`.
5. Checklist e processo de release:
   - `docs/BLENDER_VALIDATION_CHECKLIST.md`
   - `docs/RELEASE_PROCESS.md`

## Validacao Executada

### Unit tests (pure python)

- Resultado: PASS
- Total: 6 testes
- Evidencia: execucao via `scripts/run_unit_tests.ps1`

### Smoke tests com `bpy` (headless)

Executado em:

- Blender 5.0.1 (build hash `a3db93c5b259`)
- Blender 4.4.3 (linha LTS, build hash `802179c51ccc`)

Resultado:

- PASS em ambas versoes para suite automatizada:
  - ciclo de registro/desregistro do add-on
  - criacao de projeto (root flexivel)
  - criacao de shot + arquivos iniciais
  - novo WIP + publish
  - abertura/rebuild de assembly
  - criacao de asset (mark only)

Evidencias:

- `validation_reports/blender_5_0_1_smoke.md`
- `validation_reports/blender_4_4_3_smoke.md`

## Compatibilidade Atual

### Verde (validado)

- API basica de operadores/paineis/preferencias compatível com Blender 4.4.3 e 5.0.1.
- Fluxos principais smoke testados em ambas versoes.
- Setup/cleanup de Asset Browser estabilizado para cenarios de load/undo/redo.

### Amarelo (proximos incrementos recomendados)

1. Cobertura de smoke ainda nao inclui todos os cenarios interativos de UI.
2. `DuplicateShotOperator` continua sendo o fluxo de maior risco (complexidade alta com relink em lote).
3. Ainda nao ha CI executando Blender headless automaticamente em pipeline remoto.

## Estado de Instalacao do Add-on no Blender 5

Checagem objetiva feita no Blender 5.0.1 (perfil padrao):

- `FOUND_MODULE=False`
- `CHECK_DEFAULT=False`
- `CHECK_LOADED=False`

Interpretacao:

- O add-on **nao esta instalado no perfil padrao do seu Blender 5** neste momento.
- Nos smoke tests ele foi carregado via `BLENDER_USER_SCRIPTS` apontando para um diretório temporario.

## Fontes oficiais usadas

- Blender 5.0 Python API Release Notes:
  - https://developer.blender.org/docs/release_notes/5.0/python_api/
- Blender 5.0 Assets Release Notes:
  - https://developer.blender.org/docs/release_notes/5.0/assets/
- Blender 5.0 Add-ons Release Notes:
  - https://developer.blender.org/docs/release_notes/5.0/add_ons/
- Blender Python API (handlers/persistent):
  - https://docs.blender.org/api/current/bpy.app.handlers.html
- Blender Extensions Platform:
  - https://docs.blender.org/manual/en/dev/advanced/extensions/getting_started.html
- Indicacao de corretivas 5.0.1 (referencia publica):
  - https://steamdb.info/patchnotes/22368528/
