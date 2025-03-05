# Blender Project Manager

A comprehensive project management addon for Blender, designed to streamline animation and VFX production workflows.

[![Download Latest Release](https://img.shields.io/github/v/release/HMiranda00/blender_project_manager?label=Download%20Latest%20Release&style=for-the-badge)](https://github.com/HMiranda00/blender_project_manager/releases/latest/download/blender_project_manager_v1.6.0.0.zip)

![Version](https://img.shields.io/badge/version-1.6.0.0-blue.svg)
![Blender](https://img.shields.io/badge/Blender-2.80+-orange.svg)
![License](https://img.shields.io/badge/license-GPL%20v3-green.svg)

## Features

- Project structure management
- Role-based workflow system
- Asset management
- Shot management and assembly
- Version control integration
- Notification system via webhooks (Discord, Slack)

## Compatibility

- Blender 3.x (Traditional addon system)
- Blender 4.0+ (New extension system)

## Installation

### Blender 3.x

1. Download the latest release ZIP file
2. In Blender, go to Edit > Preferences > Add-ons
3. Click "Install..." and select the downloaded ZIP file
4. Enable the addon by checking the box

### Blender 4.0+

1. Download the latest release ZIP file
2. In Blender, go to Edit > Preferences > Extensions
3. Click "Install..." and select the downloaded ZIP file
4. Enable the extension by checking the box

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

## Recent Code Improvements

The codebase has undergone significant improvements in organization and structure:

### 1. Modularization

Large modules have been split into smaller, focused components for better maintainability:

- **preferences.py** → preferences/ module with specialized components:
  - `__init__.py`: Entry point and registration
  - `preference_class.py`: Core preference classes
  - `preference_utils.py`: Utility functions
  - `preference_io.py`: Import/Export functionality
  - `role_definitions.py`: Role configuration classes
  - `webhooks.py`: Notification system

### 2. Code Documentation

- Comprehensive docstrings in standard Python format
- Type hints for better IDE support and code understanding
- Clear inline comments explaining complex operations

### 3. Blender 4.0+ Extension Support

Special handling has been implemented for the new Blender 4.0+ extension system:

- Dynamic bl_idname resolution to work with Blender's extension naming scheme
- Compatibility layer that works across both addon and extension systems
- Robust error handling with fallbacks for edge cases

## Developer Notes

### Extension System Considerations

The Blender 4.0+ extension system handles package names differently from the traditional addon system:

1. **Package Naming**: Extensions can have prefixed names or different naming conventions to avoid conflicts
2. **Registration**: Extensions are registered differently than traditional addons
3. **Preferences Access**: Accessing preferences requires special handling in the extension system

The code handles these differences through utility functions that:

- Dynamically determine the correct package name
- Support multiple fallback strategies
- Add additional debugging information during registration

For further development, always use the provided utility functions to access addon preferences rather than hardcoding paths or names.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes following the established coding style
4. Add appropriate tests and documentation
5. Submit a pull request
