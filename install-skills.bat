@echo off
REM Installation script for Claude Code Skills (Windows)
REM This script copies skills from this repository to %USERPROFILE%\.claude\skills\

setlocal enabledelayedexpansion

set "REPO_DIR=%~dp0"
set "SKILLS_DIR=%USERPROFILE%\.claude\skills"
set "SKILLS_MANIFEST=%REPO_DIR%skills-registry.json"

echo 📦 Installing Claude Code Skills from agents-and-commands repository
echo.

if not exist "%SKILLS_MANIFEST%" (
    echo ❌ Skill manifest not found at %SKILLS_MANIFEST%
    exit /b 1
)

REM Create skills directory if it doesn't exist
if not exist "%SKILLS_DIR%" (
    echo Creating %SKILLS_DIR%...
    mkdir "%SKILLS_DIR%"
)

if "%~1"=="" (
    echo Installing all skills...
    echo.
    for /f "usebackq tokens=*" %%S in (`powershell -NoProfile -Command "(Get-Content -Raw '%SKILLS_MANIFEST%' | ConvertFrom-Json).skills | ForEach-Object { $_.name }"`) do (
        call :install_skill "%%S"
    )
) else (
    echo Installing specified skills...
    echo.
    call :process_args %*
)

goto end

:process_args
if "%~1"=="" exit /b 0
call :install_skill "%~1"
shift
goto process_args

:install_skill
set "SKILL_NAME=%~1"
set "RELATIVE_PATH="
for /f "usebackq tokens=*" %%P in (`powershell -NoProfile -Command "(Get-Content -Raw '%SKILLS_MANIFEST%' | ConvertFrom-Json).skills | Where-Object name -eq '%~1' | Select-Object -ExpandProperty path"` ) do (
    set "RELATIVE_PATH=%%P"
)

if "!RELATIVE_PATH!"=="" (
    echo ❌ Skill not found in manifest: %~1
    exit /b 1
)

set "SOURCE_PATH=%REPO_DIR%!RELATIVE_PATH!"
set "SOURCE_PATH=!SOURCE_PATH:/=\!"
set "DEST_PATH=%SKILLS_DIR%\%~1"

if not exist "!SOURCE_PATH!" (
    echo ❌ Skill directory not found: !SOURCE_PATH!
    exit /b 1
)

if exist "!DEST_PATH!" (
    echo ⚠️  %~1 already exists. Overwriting...
    rmdir /s /q "!DEST_PATH!"
)

echo ✅ Installing: %~1
xcopy "!SOURCE_PATH!" "!DEST_PATH!\" /E /I /Q >nul
exit /b 0

:end
echo.
echo ✨ Installation complete!
echo.
echo Installed skills are now available in Claude Code.
echo You can invoke them by name or via the Skill tool.
echo.
echo Example usage:
echo   - 'Use grasshopper-analyzer to analyze this file'
echo   - 'Run dynamo-analyzer on this graph'
echo   - 'Convert this article with markdown-to-xml'
echo.

pause
exit /b 0
