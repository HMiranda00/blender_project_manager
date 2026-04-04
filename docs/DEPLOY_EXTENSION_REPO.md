# Deploy para o repo de publicacao da extension

Este projeto ja gera os artefatos da Blender Extension localmente em `extension_repo/`.

O passo que faltava era sincronizar esses artefatos para o repositório externo que o Blender consome como fonte remota. O fluxo suportado agora e:

1. Gerar artefatos locais com `scripts/release_new_version.ps1`
2. Fazer push do commit com `extension_repo/` atualizado neste repo
3. O GitHub Actions publica automaticamente em `h_blender_addons`
4. Opcionalmente, usar `scripts/deploy_extension_repo.ps1` para publicar manualmente

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

Workflow:

- [.github/workflows/publish-extension-repo.yml](/Users/henrique/github/blender_project_manager/.github/workflows/publish-extension-repo.yml)

Trigger:

- `push` na branch `master` quando houver mudanca em `extension_repo/**`
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

1. Rodar o build local da extensao:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/release_new_version.ps1 -Version 1.6.4
```

2. Commitar e dar push neste repo, incluindo `extension_repo/`

3. Deixar o workflow publicar automaticamente no `h_blender_addons`

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
