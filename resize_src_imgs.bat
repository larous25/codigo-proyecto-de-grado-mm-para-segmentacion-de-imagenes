@echo off
setlocal enabledelayedexpansion

REM Inicializa las variables
set "source_dirname="
set "dest_dirname="
set "sizes_file="

REM Analiza los argumentos
:parse_args
if "%~1"=="" goto after_parse
if "%~1"=="-sd" (
    set "source_dirname=%~2"
    shift
) else if "%~1"=="--source_dir" (
    set "source_dirname=%~2"
    shift
) else if "%~1"=="-dd" (
    set "dest_dirname=%~2"
    shift
) else if "%~1"=="--dest_dir" (
    set "dest_dirname=%~2"
    shift
) else if "%~1"=="-f" (
    set "sizes_file=%~2"
    shift
) else if "%~1"=="--file" (
    set "sizes_file=%~2"
    shift
) else if "%~1"=="-h" (
    goto usage
) else (
    goto usage
)
shift
goto parse_args

:after_parse

REM Verifica que los argumentos existan
if not defined source_dirname (
    echo FALTA -sd o --source_dir
    goto :eof
)
if not defined dest_dirname (
    echo FALTA -dd o --dest_dir
    goto :eof
)
if not defined sizes_file (
    echo FALTA -f o --file
    goto :eof
)

REM Procesa las imágenes
for /f %%p in (%sizes_file%) do (
    echo Procesando tamaño: %%px%%p
    
    :: Procesar cada archivo en el directorio fuente
    for %%i in ("%source_dirname%\*.*") do (
        set "filepath=%%~fi"
        set "filename=%%~ni"
        set "ext=%%~xi"
        
        echo Redimensionando: !filename!!ext! a %%px%%p
        magick convert "!filepath!" -interpolate Nearest -filter point -resize %%px%%p "!dest_dirname!\!filename!_%%p!ext!"
    )
)


goto :eof

:usage
echo USO: resize_src_imgs.bat -sd source_dir -dd dest_dir -f sizes_file
