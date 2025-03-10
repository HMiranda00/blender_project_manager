# Preferências do Addon

O Blender Project Manager oferece um conjunto completo de preferências e configurações que permitem adaptar o addon às necessidades específicas de cada equipe e projeto.

## Acesso às Preferências

Para acessar as preferências do addon:
1. Abra o Blender
2. Vá para `Edit > Preferences > Add-ons`
3. Localize "Blender Project Manager" na lista
4. Expanda o item clicando na seta lateral

## Configurações Principais

### Sistema de Raiz do Projeto

#### Use Fixed Root
- **Descrição**: Define se todos os projetos serão criados sob um único diretório raiz
- **Opções**: True/False
- **Efeito**: 
  - Quando ativado, todos os projetos são criados no caminho definido em "Fixed Root Path"
  - Quando desativado, os projetos podem ser criados em qualquer lugar do sistema de arquivos

#### Fixed Root Path
- **Descrição**: Caminho para a pasta raiz que conterá todos os projetos
- **Visível quando**: "Use Fixed Root" está ativado
- **Formato recomendado**: Um caminho de diretório que tenha permissões de escrita

### Roles (Mapeamento de Funções)

Esta seção permite configurar diferentes roles (funções/departamentos) no fluxo de trabalho. Cada role tem seu próprio conjunto de configurações:

#### Role Name
- **Descrição**: Nome da role/função (ex: ANIMATION, LOOKDEV, LAYOUT)
- **Formato recomendado**: Texto curto, preferencialmente em maiúsculas

#### Description
- **Descrição**: Descrição breve da função desta role
- **Uso**: Exibido como tooltip na interface

#### Link Type
- **Descrição**: Define como esta role será vinculada a outras partes do projeto
- **Opções**:
  - **LINK**: Cria um link (referência) à coleção original
  - **APPEND**: Adiciona uma cópia da coleção ao arquivo atual
- **Efeito**: Controla o comportamento quando esta role é referenciada em outros arquivos

#### Icon
- **Descrição**: Ícone que representa esta role na interface
- **Opções**: Diversos ícones do Blender, categorizados por função (Animation, Materials, Models, etc.)
- **Efeito**: Visual, facilita a identificação rápida da role

#### Collection Color
- **Descrição**: Cor que será aplicada à coleção desta role no Outliner
- **Opções**: Cores padrão do Blender para coleções (Red, Orange, Yellow, etc.)
- **Efeito**: Visual, facilita a identificação de coleções de diferentes roles

#### Hide Viewport Default
- **Descrição**: Define se a coleção desta role deve iniciar oculta no viewport
- **Opções**: True/False
- **Efeito**: Controla a visibilidade inicial da coleção no viewport

#### Exclude from View Layer
- **Descrição**: Define se a coleção deve ser excluída da view layer por padrão
- **Opções**: True/False
- **Efeito**: Controla a inclusão inicial da coleção na view layer

#### Show Status
- **Descrição**: Mostra o status desta role no painel principal
- **Opções**: True/False
- **Efeito**: Controla a visibilidade do status da role no painel do projeto

#### Controls World
- **Descrição**: Define se esta role é responsável pelo World da cena
- **Opções**: True/False
- **Efeito**: Quando verdadeiro, o World desta role será usado no assembly

#### Skip Assembly
- **Descrição**: Define se esta role será incluída no arquivo de assembly do shot
- **Opções**: True/False
- **Efeito**: Quando verdadeiro, esta role não será incluída automaticamente nos arquivos de assembly

#### Publish Folder
- **Descrição**: Seleciona o caminho de publicação para esta role
- **Opções**:
  - **SHOTS**: Publica na estrutura de shots
  - **CHARACTERS**: Publica na pasta de personagens
  - **PROPS**: Publica na pasta de props
  - **CUSTOM**: Utiliza um caminho personalizado
- **Efeito**: Determina onde os arquivos publicados desta role serão salvos

#### Custom Path
- **Descrição**: Caminho personalizado para os arquivos publicados desta role
- **Visível quando**: "Publish Folder" está definido como "CUSTOM"
- **Formato**: Caminho que pode incluir placeholders como `{root}`, `{projectCode}`, `{shot}`, `{role}`, `{assetName}`

## Gerenciamento de Roles

### Botões de Controle

#### Add Role
- **Função**: Adiciona uma nova role à lista
- **Comportamento**: Cria uma nova role com configurações padrão

#### Remove Role
- **Função**: Remove a role selecionada da lista
- **Comportamento**: Exclui permanentemente a role e suas configurações

## Projetos Recentes

### Recent Projects
- **Descrição**: Lista de projetos recentemente acessados
- **Funcionalidades**:
  - Clique para carregar o projeto
  - Opções para remover da lista
  - Filtros e busca

### Show All Projects
- **Descrição**: Mostra todos os projetos recentes ou apenas os 3 mais recentes
- **Opções**: True/False
- **Efeito**: Controla a quantidade de projetos recentes exibidos por padrão

## Exportação e Importação de Configurações

### Export Settings
- **Função**: Exporta todas as configurações para um arquivo JSON
- **Uso**: Compartilhar configurações entre equipes ou fazer backup

### Import Settings
- **Função**: Importa configurações de um arquivo JSON
- **Uso**: Carregar configurações compartilhadas ou restaurar de backup

## Melhores Práticas para Configuração

### Configuração de Roles

- **Roles Essenciais**: Configure pelo menos as roles básicas como LAYOUT, ANIMATION e LOOKDEV
- **Cores Distintas**: Use cores distintas para cada role para fácil identificação
- **Descrições Claras**: Forneça descrições claras para cada role para orientar novos usuários

### Configuração de Caminhos

- **Caminho Raiz Acessível**: Se usar raiz fixa, escolha um caminho acessível a todos os membros da equipe
- **Consistência**: Mantenha a mesma configuração de raiz para todos os usuários que colaboram no mesmo projeto

### Controle de Assembly

- **Responsabilidade do World**: Atribua o controle do World a apenas uma role (geralmente LOOKDEV ou LAYOUT)
- **Roles Skip Assembly**: Configure roles técnicas ou de suporte para pular o assembly quando não forem necessárias na renderização final

Estas configurações formam a base do fluxo de trabalho do Blender Project Manager e devem ser adaptadas às necessidades específicas de cada projeto e equipe. 