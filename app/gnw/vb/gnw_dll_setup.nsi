; gnw_dll_setup.nsi
;
; This script is based on example2.nsi

;--------------------------------
!define VERSION "1.4.2"

; The name of the installer
Name "GNW_DLL (${VERSION})"

; The file to write
OutFile "gnw_dll_setup-${VERSION}.exe"

; The default installation directory
InstallDir $PROGRAMFILES\RWEST\gnw

; Registry key to check for directory (so if you install again, it will 
; overwrite the old one automatically)
InstallDirRegKey HKLM "Software\RWEST\gnw" "Install_Dir"

; Request application privileges for Windows Vista
RequestExecutionLevel admin

;--------------------------------

; Pages

Page components
Page directory
Page instfiles

UninstPage uninstConfirm
UninstPage instfiles

;--------------------------------

; The stuff to install
Section "Install GNW DLL"

  SectionIn RO
  
  ; Set output path to the installation directory.
  SetOutPath $INSTDIR
  
  ; Put file there
  File "gnw_dll\gnw.dll"
  
  ; Register ActiveX dll
  RegDLL $INSTDIR\gnw.dll
  
  ; Write the installation path into the registry
  WriteRegStr HKLM SOFTWARE\RWEST\gnw "Install_Dir" "$INSTDIR"
  WriteRegStr HKLM SOFTWARE\RWEST\gnw "Version" "${VERSION}"
  
  ; Write the uninstall keys for Windows
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\gnw_dll" "DisplayName" "GNW DLL ${VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\gnw_dll" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\gnw_dll" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\gnw_dll" "NoRepair" 1
  WriteUninstaller "uninstall.exe"
  
SectionEnd

;--------------------------------

; Uninstaller

Section "Uninstall"
  ; Unregister ActiveX dll
  UnRegDLL $INSTDIR\gnw.dll
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\gnw_dll"
  DeleteRegKey HKLM SOFTWARE\RWEST\gnw
  
  
  ; Remove files and uninstaller
  Delete $INSTDIR\gnw.dll
  Delete $INSTDIR\uninstall.exe

  ; Remove directories used
  RMDir "$INSTDIR"

SectionEnd
