@echo off
setlocal EnableExtensions
title Tomato OS - VirtualBox
set "OVA=%~dp0Tomato-OS.ova"
if not exist "%OVA%" goto missing_ova
set "VBOX=%ProgramFiles%\Oracle\VirtualBox\VBoxManage.exe"
if not exist "%VBOX%" for %%I in (VBoxManage.exe) do set "VBOX=%%~$PATH:I"
if not defined VBOX goto missing_virtualbox
if not exist "%VBOX%" goto missing_virtualbox
echo Tomato OS wird in VirtualBox vorbereitet...
"%VBOX%" showvminfo "Tomato OS" --machinereadable >nul 2>&1
if not errorlevel 1 goto start_vm
echo Importiere Tomato-OS.ova. Das kann einige Minuten dauern.
"%VBOX%" import "%OVA%" --vsys 0 --vmname "Tomato OS"
if errorlevel 1 goto failed
"%VBOX%" modifyvm "Tomato OS" --nic1 nat --graphicscontroller vmsvga --vram 128
if errorlevel 1 goto failed
:start_vm
echo Starte Tomato OS...
"%VBOX%" startvm "Tomato OS" --type gui
if errorlevel 1 goto failed
echo Fertig. Beim ersten Start Benutzername und Passwort anlegen.
exit /b 0
:missing_ova
echo Tomato-OS.ova wurde nicht gefunden.
echo Bitte die gesamte heruntergeladene ZIP-Datei entpacken.
goto failed
:missing_virtualbox
echo VirtualBox wurde nicht gefunden.
echo Bitte VirtualBox installieren und diese Datei erneut starten.
goto failed
:failed
echo.
echo Die Einrichtung konnte nicht abgeschlossen werden.
pause
exit /b 1
