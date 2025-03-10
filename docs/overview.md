# Visão Geral do Blender Project Manager

## Introdução

O **Blender Project Manager** é um addon projetado para gerenciar projetos complexos de animação no Blender. Ele fornece uma estrutura organizada e um fluxo de trabalho padronizado para equipes que trabalham em projetos de animação, especialmente aqueles que envolvem múltiplos departamentos (roles) e assets.

## Propósito

O principal objetivo deste addon é simplificar o gerenciamento de projetos de animação no Blender, resolvendo desafios comuns como:

- Organização consistente de arquivos e pastas
- Gerenciamento eficiente de shots e assets
- Colaboração entre diferentes departamentos/funções (roles)
- Controle de versão e publicação de trabalhos
- Integração e montagem de elementos de diferentes departamentos

## Principais Conceitos

O addon é construído em torno de alguns conceitos fundamentais:

### 1. Projetos

Um projeto é a unidade organizacional de mais alto nível. Cada projeto possui:
- Uma estrutura padronizada de pastas
- Configurações específicas
- Um conjunto de shots e assets associados

### 2. Shots

Os shots são cenas individuais dentro de um projeto. Cada shot contém:
- Arquivos separados para cada departamento/função (role)
- Um arquivo de montagem (assembly) que integra o trabalho de todos os departamentos
- Versões de trabalho (WIP) e publicadas (PUBLISH)

### 3. Roles (Funções/Departamentos)

As roles representam diferentes responsabilidades ou departamentos em um projeto, como:
- Animação
- Lookdev (desenvolvimento visual)
- Layout
- Rigging
- Efeitos

Cada role tem suas próprias configurações e pode trabalhar em arquivos separados, com regras específicas para como seu trabalho é integrado ao projeto maior.

### 4. Assets

Os assets são elementos reutilizáveis que podem ser compartilhados entre shots, como:
- Personagens
- Props (objetos)
- Ambientes

O addon facilita a criação, categorização e uso desses assets através do Blender Asset Browser.

### 5. Assembly (Montagem)

O sistema de assembly permite combinar automaticamente o trabalho de diferentes departamentos em um arquivo final, gerenciando as referências e mantendo a integridade do projeto.

## Principais Recursos

- **Gestão de Projeto**: Criação e carregamento de projetos com estrutura de pastas padronizada
- **Sistema de Roles**: Configuração personalizada de departamentos com comportamentos específicos
- **Gestão de Shots**: Criação e organização de shots com arquivos específicos para cada role
- **Gestão de Assets**: Integração com o Asset Browser do Blender para gerenciar personagens, props e ambientes
- **Controle de Versão**: Sistema de versionamento automático para arquivos WIP e publicados
- **Sistema de Assembly**: Criação automática de arquivos de montagem que combinam o trabalho de diferentes roles
- **Preparação para Renderização**: Ferramentas para preparar arquivos de assembly para renderização final

O Blender Project Manager foi projetado para ser flexível e adaptável a diferentes fluxos de trabalho, permitindo que equipes de qualquer tamanho possam se beneficiar de uma estrutura organizada e consistente para seus projetos de animação. 