@echo off
echo Instalando extensao diretamente no Blender...

REM Definir caminhos
set TARGET_DIR=C:\Users\HenriqueMiranda\AppData\Roaming\Blender Foundation\Blender\4.3\extensions\user_default\blender_project_manager
set BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 4.3\blender.exe

REM Tentar fechar o Blender (silenciosamente)
taskkill /f /im blender.exe >nul 2>&1
if %ERRORLEVEL% EQU 0 (
   echo Blender fechado com sucesso.
) else (
   echo Blender nao estava em execucao ou nao foi possivel fecha-lo.
)

REM Limpar diretorio de destino
if exist "%TARGET_DIR%" (
    echo Limpando diretorio existente...
    rd /s /q "%TARGET_DIR%"
)

REM Criar diretorio
echo Criando diretorio de destino...
mkdir "%TARGET_DIR%" 2>nul

REM Copiar arquivos
echo Copiando arquivos...
xcopy /E /Y /I /EXCLUDE:build_tools\exclude.txt . "%TARGET_DIR%"

echo.
echo Instalacao concluida!
echo A extensao foi instalada em:
echo %TARGET_DIR%
echo.

REM Abrir o Blender
echo Abrindo o Blender...
if exist "%BLENDER_EXE%" (
    start "" "%BLENDER_EXE%"
    echo Blender iniciado com sucesso!
) else (
    echo AVISO: Nao foi possivel encontrar o executavel do Blender.
    echo Por favor, abra o Blender manualmente.
    pause
) 