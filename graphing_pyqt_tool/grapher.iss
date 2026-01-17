; ============================================================
; Inno Setup Script for Grapher Client
; ============================================================

[Setup]
AppName=GrapherClient
AppVersion=1.0.0
AppPublisher=NEL
DefaultDirName={commonpf}\GrapherClient
DefaultGroupName=GrapherClient
OutputDir=installer_output
OutputBaseFilename=GrapherClientInstaller
Compression=lzma
SolidCompression=yes
WizardStyle=modern

PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Icon for installer itself
SetupIconFile=resources\icons\icon.ico

[Files]
; Include all PyInstaller output
Source: "dist\GrapherClient.exe"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\GrapherClient"; Filename: "{app}\GrapherClient.exe"
Name: "{commondesktop}\GrapherClient"; Filename: "{app}\GrapherClient.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked

[Run]
Filename: "{app}\GrapherClient.exe"; Description: "Launch GrapherClient"; Flags: nowait postinstall skipifsilent