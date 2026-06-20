[Setup]
AppName=OpenHam Logger
AppVersion=0.2.5
DefaultDirName={autopf}\OpenHam
DefaultGroupName=OpenHam
OutputDir=.\releases
OutputBaseFilename=OpenHam_Setup_0.2.5
Compression=lzma
SolidCompression=yes

[Files]
; 1. Copy the main executable
Source: "dist\OpenHam Logger 0.2.5\OpenHam Logger 0.2.5.exe"; DestDir: "{app}"; Flags: ignoreversion

; 2. CRITICAL: Bundle your starter/template database file into the installation folder!
; 'uninsneveruninstall' ensures that if the user updates or uninstalls the app later, 
; Inno Setup won't delete their hard-earned ham radio logs!
;Source: "source\ham_log.db"; DestDir: "{app}"; Flags: uninsneveruninstall

; 3. Copy all support DLLs, assets, and folders inside the dist folder
Source: "dist\OpenHam Logger 0.2.5\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
; Force the installer to create the empty plugins folder for mods!
Name: "{app}\plugins"

[Icons]
Name: "{group}\OpenHam"; Filename: "{app}\OpenHam_Logger 0.2.5.exe"
Name: "{autodesktop}\OpenHam"; Filename: "{app}\OpenHam_Logger 0.2.5.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked