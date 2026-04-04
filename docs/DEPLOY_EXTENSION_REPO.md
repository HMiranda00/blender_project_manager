# Deploy para o repo de publicacao da extension

Este projeto pode gerar os artefatos da Blender Extension localmente em `extension_repo/`, mas o fluxo principal de producao agora e via GitHub Actions.

O passo que faltava era sincronizar esses artefatos para o repositório externo que o Blender consome como fonte remota. O fluxo suportado agora e:

1. Trabalhar em branch e validar via CI
2. Fazer merge para `master` apenas do que vai para producao
3. O workflow `Release Extension` baixa Blender, valida o manifest, builda a extension e publica no `h_blender_addons`
4. Opcionalmente, usar `scripts/release_new_version.ps1` e `scripts/deploy_extension_repo.ps1` como fallback manual

## Pre-requisitos

- O repo de publicacao precisa estar clonado localmente.
- Esse repo precisa estar acessivel por Git.
- O checkout de destino pode ser:
  - a raiz do repo de publicacao;
  - ou uma subpasta, usando `-TargetSubdir`, se esse repo agrega varias extensoes.

## Repo real de publicacao

URL atual informada para publicacao automatica da extension:

- `https://github.com/HMiranda00/h_blender_addons.git`

## Automacao via GitHub Actions

Workflow de release:

- [release-extension.yml](/Users/henrique/github/blender_project_manager/.github/workflows/release-extension.yml)

Workflow de CI para branch e PR:

- [ci.yml](/Users/henrique/github/blender_project_manager/.github/workflows/ci.yml)

Trigger:

- `push` na branch `master`
- `workflow_dispatch` para disparo manual

Secret necessario no repo `blender_project_manager`:

- `H_BLENDER_ADDONS_TOKEN`
  - pode ser classic PAT com `repo`, ou fine-grained token com `Contents: Read and write` no repo `HMiranda00/h_blender_addons`

O workflow sincroniza:

- `index.json`
- `blender_project_manager-<version>.zip`
- `README.md`
- `blender_repo.example.toml`

## Fluxo recomendado

1. Trabalhar normalmente em branch
2. Abrir PR
3. O workflow `CI` roda os testes puros
4. Quando estiver pronto para producao, fazer merge em `master`
5. O workflow `Release Extension` publica automaticamente no `h_blender_addons`

## Comando basico

Se esse repo ainda nao estiver clonado localmente, o script pode clonar sozinho:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/deploy_extension_repo.ps1 `
  -TargetRepoUrl "https://github.com/HMiranda00/h_blender_addons.git"
```

Esse comando:

- usa `..\h_blender_addons` como clone local padrao ao lado deste repo;
- le `extension_repo/index.json` do repo atual;
- detecta o `zip` referenciado pela versao atual;
- copia `index.json` e o `zip` para o repo externo;
- remove zips antigos de `blender_project_manager` no destino para evitar lixo historico.

## Repo agregador com subpasta

```powershell
powershell -ExecutionPolicy Bypass -File scripts/deploy_extension_repo.ps1 `
  -TargetRepoPath "C:\Users\henrique\github\my-addons" `
  -TargetSubdir "blender_project_manager"
```

## Commit e push automaticos

```powershell
powershell -ExecutionPolicy Bypass -File scripts/deploy_extension_repo.ps1 `
  -TargetRepoUrl "https://github.com/HMiranda00/h_blender_addons.git" `
  -Commit `
  -Push
```

Opcoes uteis:

- `-TargetRepoPath "C:\Users\henrique\github\h_blender_addons"`: usa um checkout local especifico.
- `-Branch "main"`: faz checkout explicito antes de commitar.
- `-CommitMessage "Publish Blender Project Manager extension v1.6.4"`: sobrescreve a mensagem padrao.
- `-SourceArtifactsDir "C:\...\extension_repo"`: usa outro diretorio de artefatos.

Para o repo `h_blender_addons`, o layout atual e raiz simples, sem `TargetSubdir`.

## Layout esperado no repo de publicacao

O script sincroniza:

- `index.json`
- `blender_project_manager-<version>.zip`
- `blender_repo.toml`, se existir em `extension_repo/`

Se o seu repo de publicacao usa GitHub Pages ou raw GitHub content, garanta apenas que o Blender esteja apontando para a URL que serve esse `index.json`.
