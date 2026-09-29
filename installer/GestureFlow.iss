#define MyAppName "GestureFlow"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "GestureFlow"
#define MyAppExeName "GestureFlow.exe"

[Setup]
AppId={{6D9D0A45-5B9D-4E34-A6C7-7D4D2A0E3B5B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\GestureFlow
DefaultGroupName={#MyAppName}
PrivilegesRequired=lowest
OutputDir=..\release
OutputBaseFilename=GestureFlow-Setup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}

[Files]
Source: "..\dist\GestureFlow\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion
Source: "..\THIRD_PARTY_NOTICES.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\PRIVACY_POLICY_TEMPLATE.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\EULA_TEMPLATE.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\GestureFlow"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\GestureFlow"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch GestureFlow"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\data"
