# Documentação dos Operadores

Este documento detalha os principais operadores disponíveis no addon Blender Project Manager e suas funcionalidades.

## Gerenciamento de Projetos

### CreateProjectOperator (`project.create_project`)
- **Descrição**: Cria um novo projeto com a estrutura de pastas padronizada.
- **Funcionalidades**:
  - Define nome e localização do projeto
  - Cria estrutura de pastas organizada (SHOTS, ASSETS 3D, etc.)
  - Configura o Asset Browser para o projeto
  - Adiciona o projeto à lista de projetos recentes

### LoadProjectOperator (`project.load_project`)
- **Descrição**: Carrega um projeto existente no Blender.
- **Funcionalidades**:
  - Permite selecionar um projeto da lista de recentes ou um caminho personalizado
  - Configura o ambiente do Blender para o projeto selecionado
  - Adiciona o projeto à lista de projetos recentes

### RecentProjectOperators (`project.clear_recent_list`, etc.)
- **Descrição**: Gerencia a lista de projetos recentes.
- **Funcionalidades**:
  - Adiciona projetos à lista de recentes
  - Remove projetos da lista
  - Limpa toda a lista de projetos recentes
  - Permite filtragem e busca de projetos recentes

## Gestão de Shots

### CreateShotOperator (`project.create_shot`)
- **Descrição**: Cria um novo shot dentro do projeto atual.
- **Funcionalidades**:
  - Define nome e número do shot
  - Cria estrutura de pastas para o shot (WIP, PUBLISH para cada role)
  - Cria arquivo de assembly inicial
  - Configura arquivos iniciais para cada role

### OpenShotOperator (`project.open_shot`)
- **Descrição**: Abre um shot existente no projeto atual.
- **Funcionalidades**:
  - Lista shots disponíveis no projeto
  - Permite selecionar a role a ser aberta
  - Abre o arquivo apropriado (WIP ou publicado)

## Roles e Arquivos

### LinkRoleOperator (`project.link_role`)
- **Descrição**: Vincula (link) ou anexa (append) o trabalho de outras roles ao arquivo atual.
- **Funcionalidades**:
  - Lista roles disponíveis para o shot atual
  - Aplica o método de vinculação configurado nas preferências (Link ou Append)
  - Gerencia importação de collections com nomes apropriados

### OpenRoleFileOperator (`project.open_role_file`)
- **Descrição**: Abre um arquivo específico de uma role para o shot atual.
- **Funcionalidades**:
  - Abre o arquivo WIP mais recente ou o arquivo publicado
  - Permite navegação rápida entre diferentes roles de um mesmo shot

## Sistema de Assembly

### ASSEMBLY_OT_open (`project.open_assembly`)
- **Descrição**: Abre o arquivo de assembly do shot atual.
- **Funcionalidades**:
  - Salva o arquivo atual antes de abrir o assembly
  - Registra o arquivo anterior para facilitar o retorno
  - Abre o arquivo de assembly do shot

### ASSEMBLY_OT_rebuild (`project.rebuild_assembly`)
- **Descrição**: Reconstrói o arquivo de assembly, atualizando todas as referências.
- **Funcionalidades**:
  - Remove referências quebradas
  - Religa todas as roles publicadas
  - Atualiza a estrutura de collections
  - Mantém overrides existentes

### ASSEMBLY_OT_prepare_render (`project.prepare_render`)
- **Descrição**: Prepara o arquivo de assembly para renderização.
- **Funcionalidades**:
  - Opções para tornar locais (make local) objetos vinculados
  - Empacota recursos externos (texturas, etc.)
  - Verifica arquivos ausentes
  - Configura propriedades de renderização

## Gestão de Assets

### ASSET_OT_create_asset (`project.create_asset`)
- **Descrição**: Cria novos assets ou marca collections existentes como assets.
- **Funcionalidades**:
  - Define tipo de asset (PROPS, CHR, ENV)
  - Suporta diferentes modos de salvamento:
    - Criar novo arquivo
    - Salvar arquivo atual como asset
    - Apenas marcar como asset sem criar novo arquivo
  - Integração com o Asset Browser do Blender
  - Comportamento especial quando usado em arquivos de shot

### ASSET_OT_reload_links (`project.reload_links`)
- **Descrição**: Recarrega links de assets no arquivo atual.
- **Funcionalidades**:
  - Atualiza referências a assets
  - Corrige links quebrados
  - Sincroniza com a biblioteca de assets

## Configuração do Asset Browser

### AssetBrowserSetupOperator (`project.setup_asset_browser`)
- **Descrição**: Configura o Asset Browser do Blender para o projeto atual.
- **Funcionalidades**:
  - Cria biblioteca de assets para o projeto
  - Configura catálogos padrão (Props, Characters, Environments)
  - Define caminhos de biblioteca

### AssetBrowserViewOperator (`project.asset_browser_view`)
- **Descrição**: Configura a visualização do Asset Browser.
- **Funcionalidades**:
  - Ajusta layout e visibilidade de painéis
  - Configura filtros e categorias
  - Otimiza a visualização para o fluxo de trabalho do projeto

## Controle de Versão

### VersionControlOperators (`project.save_wip`, `project.publish_version`)
- **Descrição**: Gerencia o controle de versões dos arquivos de trabalho.
- **Funcionalidades**:
  - Save WIP: Salva uma nova versão de trabalho com número incrementado
  - Publish Version: Publica a versão atual para compartilhamento
  - Gerencia a nomenclatura de arquivos e organização
  - Mantém registro de versões e histórico

## Operadores de UI

### UIOperators (`project.toggle_panel_section`, etc.)
- **Descrição**: Gerencia elementos da interface do usuário do addon.
- **Funcionalidades**:
  - Controla visibilidade de seções do painel
  - Gerencia estados expandidos/colapsados
  - Controla filtros e opções de visualização

Cada operador é projetado para trabalhar de forma integrada com os outros componentes do sistema, mantendo a consistência e integridade da estrutura do projeto. 