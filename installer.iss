[Setup]
AppName=OpenHam Logger 0.2.1
AppVersion=0.2.1
DefaultDirName={autopf}\OpenHam_0.2.1
DefaultGroupName=
OutputDir=.
OutputBaseFilename=OpenHam_0.2.1_Setup
Compression=lzma
SolidCompression=yes

[Files]
; 1. Copy the main executable
Source: "dist\OpenHam Logger 0.2.1\OpenHam Logger 0.2.1.exe"; DestDir: "{app}"; Flags: ignoreversion
; 2. Copy all support DLLs, assets, and folders inside the dist folder
Source: "dist\OpenHam Logger 0.2.1\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
; CRITICAL: Force the installer to create the empty plugins folder for mods!
Name: "{app}\plugins"

[Icons]
; Create Start Menu shortcut
Name: "{group}\OpenHam"; Filename: "{app}\OpenHam Logger 0.2.1.exe"
; Create Desktop shortcut
Name: "{autodesktop}\OpenHam"; Filename: "{app}\OpenHam Logger 0.2.1.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked