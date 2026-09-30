@echo off
setlocal EnableExtensions
title Tomaten OS - VirtualBox
set "OVA=%~dp0Tomaten-OS.ova"
set "HASHFILE=%~dp0Tomaten-OS.ova.sha256"
if not exist "%OVA%" goto missing_files
if not exist "%HASHFILE%" goto missing_files
for /f "usebackq tokens=1" %%H in ("%HASHFILE%") do set "SHA=%%H"
if not defined SHA goto missing_files
set "VMNAME=Tomaten OS %SHA:~0,8%"
set "VBOX=%ProgramFiles%\Oracle\VirtualBox\VBoxManage.exe"
if not exist "%VBOX%" for %%I in (VBoxManage.exe) do set "VBOX=%%~$PATH:I"
if not defined VBOX goto missing_virtualbox
if not exist "%VBOX%" goto missing_virtualbox
echo Bereite %VMNAME% vor...
"%VBOX%" showvminfo "%VMNAME%" --machinereadable >nul 2>&1
if not errorlevel 1 goto start_vm
echo Importiere die neue OVA. Das kann einige Minuten dauern.
"%VBOX%" import "%OVA%" --vsys 0 --vmname "%VMNAME%"
if errorlevel 1 goto failed
"%VBOX%" modifyvm "%VMNAME%" --nic1 nat --graphicscontroller vmsvga --vram 128
if errorlevel 1 goto failed
:start_vm
echo Starte %VMNAME%...
"%VBOX%" startvm "%VMNAME%" --type gui
if errorlevel 1 goto failed
echo Fertig. Beim ersten Start ein Benutzerkonto anlegen.
exit /b 0
:missing_files
echo Tomaten-OS.ova oder die Pruefsumme fehlt.
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
