# Fluxo de Trabalho

Este documento descreve o fluxo de trabalho típico ao utilizar o Blender Project Manager, desde a criação de um projeto até a renderização final.

## Configuração Inicial

### 1. Configuração das Preferências do Addon

Antes de começar a usar o addon, é recomendado configurar as preferências:

1. Abra o Blender e vá para `Edit > Preferences > Add-ons`
2. Localize o addon "Blender Project Manager"
3. Clique no expansor para acessar as preferências
4. Configure:
   - **Sistema de Raiz**: Escolha entre raiz fixa ou flexível
   - **Roles**: Configure as funções/departamentos necessários para seu projeto
   - **Caminhos de Publicação**: Configure onde cada role irá publicar seus arquivos

### 2. Criação de um Novo Projeto

1. No painel do addon (localizado no N-Panel), clique em "Create New Project"
2. Preencha:
   - Nome do projeto
   - Localização (dependendo da configuração de raiz)
   - Código do projeto (prefixo para arquivos)
3. Clique em "Create Project"
4. O addon criará automaticamente a estrutura de pastas necessária

## Trabalhando com Shots

### 1. Criação de um Shot

1. Com um projeto aberto, clique em "Create Shot"
2. Preencha:
   - Número do shot (ex: 010, 020)
   - Nome descritivo (opcional)
3. O addon criará automaticamente:
   - Estrutura de pastas para o shot
   - Arquivos iniciais para cada role configurada
   - Um arquivo de assembly inicial

### 2. Trabalhando em uma Role Específica

1. Selecione o shot no qual deseja trabalhar usando "Open Shot"
2. Escolha a role em que deseja trabalhar (ex: ANIMATION, LOOKDEV)
3. O arquivo WIP mais recente será aberto, ou um novo será criado
4. Trabalhe normalmente no Blender
5. Quando precisar salvar, use o botão "Save WIP" no painel do addon
   - Isso salvará o arquivo com um número de versão incrementado

### 3. Referenciando Trabalho de Outras Roles

Se você precisar referenciar o trabalho de outras roles:

1. No arquivo da sua role, clique em "Link Role"
2. Selecione a role que deseja vincular
3. O addon importará automaticamente o conteúdo publicado da role selecionada

### 4. Publicando seu Trabalho

Quando estiver pronto para compartilhar seu trabalho com outras roles:

1. Use o botão "Publish Version"
2. Adicione uma descrição para documentar as alterações
3. O addon:
   - Salvará uma cópia na pasta PUBLISH
   - Atualizará o arquivo de assembly automaticamente (se configurado)
   - Manterá sua versão WIP atual

## Trabalhando com Assets

### 1. Criação de Assets

Existem várias maneiras de criar assets:

#### Criando Um Novo Asset do Zero:

1. Clique em "Create Asset"
2. Escolha o tipo (PROPS, CHR, ENV)
3. Digite um nome para o asset
4. Selecione "New File" como modo de salvamento
5. Um novo arquivo será criado na pasta apropriada de assets

#### Convertendo Collections Existentes em Assets:

1. Selecione uma collection no Outliner
2. Clique em "Create Asset"
3. Escolha o tipo e nome
4. Selecione o modo de salvamento desejado:
   - "New File": Cria um novo arquivo para o asset
   - "Save As": Salva o arquivo atual como asset
   - "Mark Only": Apenas marca como asset sem criar novo arquivo

#### Extraindo Assets de um Shot:

1. No arquivo de uma role específica, selecione a collection que deseja transformar em asset
2. Clique em "Create Asset"
3. O addon automaticamente:
   - Salvará a collection como um novo asset
   - Substituirá a collection original por uma referência ao asset

### 2. Usando Assets

1. Abra o Asset Browser (pode usar o botão "Asset Browser View")
2. Navegue até o catálogo apropriado (Props, Characters, Environments)
3. Arraste e solte assets na sua cena
4. O addon manterá os links adequados e permitirá atualizações quando o asset original for modificado

## Trabalhando com Assembly

### 1. Abrindo o Assembly de um Shot

1. Use o botão "Open Assembly" no painel do shot
2. O addon abrirá o arquivo de assembly, mostrando o trabalho combinado de todas as roles

### 2. Reconstruindo o Assembly

Se houver alterações nas publicações de roles:

1. No arquivo de assembly, clique em "Rebuild Assembly"
2. O addon:
   - Atualizará todas as referências
   - Manterá overrides existentes
   - Reorganizará as collections conforme necessário

### 3. Preparando para Renderização

Quando estiver pronto para renderizar:

1. No arquivo de assembly, clique em "Prepare for Render"
2. Configure as opções desejadas:
   - Make Local: Torna locais objetos vinculados selecionados
   - Pack Resources: Empacota texturas e recursos externos
   - Check Missing Files: Verifica arquivos ausentes
   - Setup Render Settings: Configura propriedades de renderização
3. O addon processará as opções selecionadas e criará um arquivo pronto para renderização

## Fluxo Completo de Exemplo

1. **Configuração**:
   - Configurar as preferências do addon
   - Criar um novo projeto

2. **Layout Inicial**:
   - Criar um shot
   - Trabalhar no arquivo LAYOUT
   - Configurar câmeras e bloqueio básico
   - Publicar versão LAYOUT

3. **Modelagem/Lookdev**:
   - Criar assets necessários
   - Trabalhar nos arquivos LOOKDEV dos shots
   - Publicar versões LOOKDEV

4. **Animação**:
   - Abrir arquivo ANIMATION
   - Linkar trabalho de LAYOUT
   - Criar animação
   - Publicar versões ANIMATION

5. **Montagem Final**:
   - Abrir arquivo ASSEMBLY
   - Reconstruir se necessário
   - Verificar integração de todos os elementos
   - Preparar para renderização

6. **Renderização**:
   - Configurar render settings finais
   - Iniciar renderização

Este fluxo de trabalho pode ser adaptado conforme as necessidades específicas de cada projeto e equipe. 