# Blender Project Manager

A comprehensive Blender addon for managing complex animation projects with multiple roles and assets.

![Version](https://img.shields.io/badge/version-1.6.0.0-blue.svg)
![Blender](https://img.shields.io/badge/Blender-2.80+-orange.svg)
![License](https://img.shields.io/badge/license-GPL%20v3-green.svg)

## Overview

Blender Project Manager is a powerful addon designed to streamline the workflow of animation projects by providing tools for:

- Project organization and structure
- Shot management
- Role-based workflow
- Asset management
- Version control
- Assembly system

## Features

### Project Management

- **Project Creation**: Create new projects with standardized folder structure
- **Project Loading**: Quick access to recent projects
- **Flexible Root System**: Support for both fixed and flexible project root paths
- **Project Structure**:
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

### Role System

- **Customizable Roles**: Define different departments/roles (Animation, Lookdev, Layout, etc.)
- **Role Settings**:
  - Custom icons and colors
  - Publish path presets
  - Collection visibility settings
  - World ownership
  - Assembly inclusion/exclusion
  - Link/Append behavior

### Shot Management

- **Shot Creation**: Create new shots with role-specific file structure
- **Role Files**: Separate files for each role in a shot
- **Assembly System**: Automatic assembly file creation and management
- **Role Status**: Visual feedback on available roles per shot

### Asset Management

- **Asset Creation**: Convert collections to assets with proper categorization
- **Asset Browser Integration**: Automatic setup of asset libraries
- **Asset Categories**:
  - Props
  - Characters
  - Environments
- **Asset Workflows**:
  - Create new asset files
  - Convert existing files to assets
  - Mark collections as assets
  - Extract assets from shots

### Version Control

- **WIP Versions**: Automatic versioning of work-in-progress files
- **Publishing System**: Standardized publish system for sharing work between roles
- **File Organization**: Clear separation between WIP and published files

### Assembly System

- **Automatic Assembly**: Creates and maintains assembly files for each shot
- **Link Management**: Smart handling of linked collections and overrides
- **Render Preparation**: Tools for preparing assembly files for rendering
  - Make local options
  - Resource packing
  - Missing file check
  - Render settings setup

## Installation

1. Download the latest release
2. In Blender, go to Edit > Preferences > Add-ons
3. Click "Install" and select the downloaded .zip file
4. Enable the addon by checking the box

## Configuration

### Initial Setup

1. Open Blender Preferences > Add-ons
2. Find "Blender Project Manager"
3. Configure the root path system:
   - Fixed Root: All projects under a single root directory
   - Flexible Root: Projects can be created anywhere

### Role Configuration

1. Add roles using the "Add Role" button
2. Configure each role:
   - Set role name and description
   - Choose icon and collection color
   - Configure publish path settings
   - Set link behavior (Link/Append)
   - Configure special settings (World ownership, Assembly inclusion)

### Asset Browser Setup

The addon automatically configures the Asset Browser for each project:
1. Creates project-specific asset library
2. Sets up standard catalogs (Props, Characters, Environments)
3. Manages asset previews and metadata

## Workflow

### Creating a New Project

1. Click "Create New Project"
2. Set project name and location
3. Project structure is automatically created

### Working with Shots

1. Create a new shot using "Create Shot"
2. Select the role you'll be working on
3. Work on your specific role file
4. Use "Publish Version" when ready to share

### Asset Creation

1. Create or select a collection
2. Click "Create Asset"
3. Choose asset type and settings
4. Asset is automatically categorized and available in the Asset Browser

### Assembly Management

1. Open shot assembly using "Open Assembly"
2. Use "Rebuild Assembly" to update links
3. "Prepare for Render" to create render-ready file

## Best Practices

- **File Organization**:
  - Keep WIP files in WIP folders
  - Always publish before linking to assembly
  - Use standardized naming conventions

- **Asset Management**:
  - Create clean, self-contained assets
  - Use proper categorization
  - Keep asset files lightweight

- **Version Control**:
  - Regular WIP saves
  - Clear publish descriptions
  - Verify links before publishing

## Troubleshooting

### Common Issues

1. **Broken Links**
   - Use "Reload Assets" to refresh all links
   - Check if source files exist
   - Verify publish paths

2. **Missing Assets**
   - Verify Asset Browser setup
   - Check asset file location
   - Reload Asset Browser

3. **Assembly Problems**
   - Use "Rebuild Assembly" to fix broken links
   - Verify role publish files
   - Check role settings in preferences

## Support

For bug reports and feature requests, please use the GitHub Issues page.

## License

This project is licensed under the GNU General Public License v3.0

For more information, see the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html).

## Credits

Created by:
- Henrique Miranda
- Higor Pereira 