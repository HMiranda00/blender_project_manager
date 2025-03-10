# Estrutura de Projeto

O Blender Project Manager utiliza uma estrutura padronizada de pastas para organizar projetos de animação. Esta estrutura foi projetada para facilitar o gerenciamento de arquivos, a colaboração entre departamentos e o controle de versões.

## Estrutura Básica de Pastas

```
PROJECT_ROOT/
├── SHOTS/
│   ├── SHOT_010/
│   │   ├── ANIMATION/
│   │   │   ├── WIP/
│   │   │   └── PUBLISH/
│   │   ├── LOOKDEV/
│   │   └── ASSEMBLY/
│   └── SHOT_020/
├── ASSETS 3D/
│   ├── PROPS/
│   ├── CHR/
│   └── ENV/
└── ...
```

## Explicação da Estrutura

### SHOTS/

Esta pasta contém todos os shots do projeto. Cada shot é organizado em uma pasta separada, geralmente nomeada com um prefixo numérico (ex: SHOT_010, SHOT_020, etc).

Dentro de cada pasta de shot, existem pastas para cada role (função/departamento) configurada nas preferências do addon:

- **ANIMATION/** - Contém arquivos relacionados à animação
- **LOOKDEV/** - Contém arquivos relacionados ao desenvolvimento visual
- **LAYOUT/** - Contém arquivos relacionados ao layout da cena
- *E outras pastas para roles customizadas*

Cada pasta de role contém:
- **WIP/** - Arquivos de trabalho em progresso, com versionamento automático
- **PUBLISH/** - Versões publicadas, prontas para serem usadas no assembly

### ASSEMBLY/

Cada shot tem uma pasta para arquivos de assembly, que combinam o trabalho de diferentes roles em um único arquivo. O sistema de assembly gerencia automaticamente os links entre os arquivos publicados pelas diferentes roles.

### ASSETS 3D/

Contém todos os assets do projeto, organizados em subcategorias:
- **PROPS/** - Objetos e elementos de cena
- **CHR/** - Personagens e modelos de personagens
- **ENV/** - Ambientes e elementos de cenário

Cada asset pode ter sua própria estrutura, semelhante à estrutura dos shots, com pastas específicas para diferentes roles e versões.

## Sistema de Arquivos

### Convenção de Nomenclatura

O addon utiliza um sistema padronizado para nomear arquivos:

- **Arquivos WIP**: `{nome_do_shot}_{role}_v{numero_versao}.blend`
  - Exemplo: `SHOT_010_ANIMATION_v001.blend`

- **Arquivos Publicados**: `{nome_do_shot}_{role}.blend`
  - Exemplo: `SHOT_010_ANIMATION.blend`

- **Arquivos de Assembly**: `{nome_do_shot}_ASSEMBLY.blend`
  - Exemplo: `SHOT_010_ASSEMBLY.blend`

### Versionamento

O sistema de versionamento automático funciona da seguinte forma:
1. Arquivos WIP são salvos com um número de versão incremental
2. Quando um arquivo é publicado, uma cópia é salva na pasta PUBLISH sem o número de versão
3. O arquivo de assembly sempre referencia os arquivos publicados mais recentes

## Configuração de Raiz do Projeto

O addon suporta dois modos de configuração de raiz:

1. **Raiz Fixa** (Fixed Root):
   - Todos os projetos são criados sob um único diretório raiz
   - Facilita a organização centralizada de múltiplos projetos
   - A raiz fixa é configurada nas preferências do addon

2. **Raiz Flexível** (Flexible Root):
   - Os projetos podem ser criados em qualquer local do sistema de arquivos
   - Oferece mais flexibilidade para organização personalizada
   - Cada projeto tem seu próprio caminho completo armazenado

## Integração com o Asset Browser

O addon configura automaticamente o Asset Browser do Blender para cada projeto:
1. Cria uma biblioteca de assets específica para o projeto
2. Configura catálogos padrão (Props, Characters, Environments)
3. Gerencia previews e metadados dos assets

Esta estrutura padronizada ajuda a manter a consistência entre diferentes projetos e facilita o trabalho colaborativo entre múltiplos departamentos. 