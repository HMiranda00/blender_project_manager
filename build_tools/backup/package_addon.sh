#!/bin/bash
echo "Empacotando Blender Project Manager..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
python3 "$SCRIPT_DIR/package_addon.py"
echo ""
echo "Pressione ENTER para sair..."
read 