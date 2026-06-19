[Setup]
AppName=OpenHam Logger
AppVersion=0.2.1
DefaultDirName={autopf}\OpenHam
DefaultGroupName=
OutputDir=.
OutputBaseFilename=OpenHam_Setup
Compression=lzma
SolidCompression=yes

[Files]
; 1. Copy the main executable
Source: "dist\HamLogger\HamLogger.exe"; DestDir: "{app}"; Flags: ignoreversion
; 2. Copy all support DLLs, assets, and folders inside the dist folder
Source: "dist\HamLogger\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
; CRITICAL: Force the installer to create the empty plugins folder for mods!
Name: "{app}\plugins"

[Icons]
; Create Start Menu shortcut
Name: "{group}\OpenHam"; Filename: "{app}\.exe"
; Create Desktop shortcut
Name: "{autodesktop}\OpenHam"; Filename: "{app}\HamLogger.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked