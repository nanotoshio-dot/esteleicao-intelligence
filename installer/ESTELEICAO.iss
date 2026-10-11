#ifndef AppVersion
  #error AppVersion must be supplied from VERSION
#endif

[Setup]
AppId={{97C0F8A1-2C58-4827-8EB0-D70162D859F9}
AppName=ESTELEIÇÃO Intelligence
AppVersion={#AppVersion}
DefaultDirName={localappdata}\Programs\ESTELEICAO
DefaultGroupName=ESTELEIÇÃO Intelligence
PrivilegesRequired=lowest
OutputDir=output
OutputBaseFilename=ESTELEICAO-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\ESTELEICAO.exe
CloseApplications=yes

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; Flags: unchecked

[Files]
Source: "..\dist\ESTELEICAO\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\ESTELEIÇÃO Intelligence"; Filename: "{app}\ESTELEICAO.exe"
Name: "{autodesktop}\ESTELEIÇÃO Intelligence"; Filename: "{app}\ESTELEICAO.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\ESTELEICAO.exe"; Description: "Abrir ESTELEIÇÃO Intelligence"; Flags: nowait postinstall skipifsilent
