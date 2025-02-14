# Project Manager for Blender

A comprehensive project management addon for Blender that helps organize and streamline the workflow in animation and VFX production pipelines.

## Features

- **Project Management**
  - Create and manage multiple projects
  - Organize shots and scenes
  - Team-based workflow support
  - Solo project mode for individual work

- **Role-Based System**
  - Define different roles (Animation, Lighting, FX, etc.)
  - Custom role configurations
  - Role-specific file organization
  - Automatic file versioning

- **Assembly System**
  - Centralized shot assembly
  - Automatic collection linking
  - Easy role integration
  - Real-time shot preview

- **Version Control**
  - Automatic versioning of WIP files
  - Publish system for final versions
  - Version history tracking
  - Easy file recovery

## Installation

1. Download the addon zip file
2. In Blender, go to Edit > Preferences > Add-ons
3. Click "Install" and select the downloaded zip file
4. Enable the addon by checking the checkbox

## Configuration

### Project Settings

- **Project Type**
  - TEAM: For collaborative projects with multiple roles
  - SOLO: For individual projects

### Role Configuration

1. Go to the addon preferences
2. Add roles using the "+" button
3. Configure each role with:
   - Role name
   - Description
   - Link type (Link/Append)
   - File paths
   - World ownership
   - Assembly integration

## Usage

### Creating a New Project

1. Open the Project Manager panel (N-Panel)
2. Click "Create Project"
3. Fill in:
   - Project name
   - Project type (TEAM/SOLO)
   - Base path
4. Click "Create"

### Creating Shots

1. Select a project
2. Click "Create Shot"
3. Choose:
   - Shot number or scene name
   - Your role
4. The addon will:
   - Create necessary folders
   - Set up initial files
   - Create assembly file (in TEAM mode)

### Working with Roles

1. **Opening Role Files**
   - Select project and shot
   - Click "Open Role"
   - Choose between WIP and Publish versions

2. **Linking Roles**
   - Open your role file
   - Click "Link Role"
   - Select the role to link
   - The addon will link the appropriate collections

3. **Publishing**
   - Work in your WIP file
   - Use version control
   - Publish when ready

### Assembly Management

The assembly system is a central file that combines all roles' work for preview and integration.

- **Location**: SHOTS/ASSEMBLY folder
- **Purpose**: Preview and integrate all roles' work
- **Features**:
  - Automatic collection linking
  - No WIP versions (single file)
  - Updated during shot creation
  - Can be rebuilt manually

### File Structure

```
PROJECT_ROOT/
├── SHOTS/
│   ├── SHOT_001/
│   │   ├── ANIMATION/
│   │   │   ├── PUBLISH/
│   │   │   │   └── _WIP/
│   │   │   └── ...
│   ├── ASSEMBLY/
│   │   └── PROJECT_SHOT_001_ASSEMBLY.blend
│   └── !LOCAL/
└── ASSETS/
```

## Best Practices

1. **File Management**
   - Always work in WIP files
   - Publish only when necessary
   - Keep the assembly updated

2. **Role Workflow**
   - Stay within your role's scope
   - Use linking instead of appending when possible
   - Maintain clean collections

3. **Assembly Usage**
   - Don't modify the assembly directly
   - Use rebuild when needed
   - Check assembly status regularly

## Troubleshooting

Common issues and solutions:

1. **Missing WIP Folder**
   - Ensure the role is properly configured
   - Check file permissions
   - Verify project structure

2. **Linking Issues**
   - Check if the source file exists
   - Verify collection names
   - Ensure proper role configuration

3. **Assembly Problems**
   - Use "Rebuild Assembly" to fix linking issues
   - Check if all required files exist
   - Verify role configurations

## Technical Details

- **Version Control**: Automatic versioning with _WIP suffix
- **File Naming**: PROJECT_SHOT_ROLE.blend
- **Collection Management**: One main collection per role
- **Assembly System**: Direct linking from publish files
- **Context Management**: Automatic context saving and loading

## Support

For bug reports and feature requests, please use the issue tracker on the project's repository.

## License

[Your License Information Here]
