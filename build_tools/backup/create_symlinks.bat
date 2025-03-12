@echo off
echo Criando links simbolicos para o Blender Project Manager

:: Verifica se está rodando como administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Executando com privilégios de administrador...
) else (
    echo Este script precisa ser executado como administrador!
    echo Por favor, clique com o botão direito e selecione "Executar como administrador"
    pause
    exit /b 1
)

:: Executa o script Python
python "%~dp0create_symlinks.py"

pause 