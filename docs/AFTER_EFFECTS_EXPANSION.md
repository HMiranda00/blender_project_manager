# Expansao para After Effects (mesma integracao)

## Objetivo

Reaproveitar o conceito do Blender Project Manager para After Effects, mantendo o mesmo pipeline (projeto, shot, role, versao, publish, assembly equivalente).

## Principio tecnico

Criar um "core de pipeline" agnostico de DCC e adapters por host:

- `adapter_blender`
- `adapter_after_effects`

Assim, naming, estrutura de pastas e regras de versionamento ficam compartilhados.

## Mapeamento Blender -> After Effects

- Arquivo de trabalho:
  - Blender: `.blend`
  - AE: `.aep`
- Role file:
  - Blender: arquivo por role/shot
  - AE: projeto por role/shot (ou comps por role, dependendo do pipeline)
- Publish:
  - Blender: copia de WIP para publish
  - AE: salvar versao aprovada + render intermediario/proxy quando aplicavel
- Assembly:
  - Blender: `*_ASSEMBLY.blend`
  - AE: "Master Comp Project" que referencia entregas das roles (footage/precomps)

## Arquitetura recomendada

### Core compartilhado

- `pipeline_core/naming.py`
- `pipeline_core/paths.py`
- `pipeline_core/versioning.py`
- `pipeline_core/project_model.py`

### Adapter Blender

- Usa `bpy` para UI/ops.
- Chama `pipeline_core` para calcular paths, nomes e versoes.

### Adapter After Effects

- Extensao CEP/UXP (dependendo da versao alvo).
- Bridge para ExtendScript/JSX (operacoes em projeto/comps/render queue).
- Mesmo `pipeline_core` (idealmente em JSON schema + regras replicadas em JS/TS).

## MVP sugerido para AE

1. Abrir/criar projeto de shot com naming padrao.
2. Criar nova versao WIP (`v001`, `v002`...).
3. Publicar versao para pasta `PUBLISH`.
4. Atualizar "master project" (equivalente ao assembly) com a versao publicada.

## Riscos e decisoes importantes

1. Escolha do stack AE:
   - CEP (mais legado)
   - UXP (mais moderno)
2. Controle de links entre `.aep` e assets externos.
3. Compatibilidade de SO/caminhos relativos.
4. Sincronizacao de metadata entre Blender e AE (JSON de shot/role/version).

## Proximo passo pratico

Criar um contrato de dados unico (`pipeline_manifest.json`) com:

- `project_code`
- `shot`
- `role`
- `current_version`
- `publish_path`
- `assembly_target`

Esse contrato vira a ponte entre Blender e After Effects sem duplicar regra de negocio.
