; Inno Setup script for Partycja (simple installer)
; To build the installer, install Inno Setup and compile this .iss file.

[Setup]
AppName=Partycja
AppVersion=1.0
DefaultDirName={pf}\Partycja
DefaultGroupName=Partycja
DisableProgramGroupPage=yes
OutputBaseFilename=partycja_installer
Compression=lzma
SolidCompression=yes

[Languages]
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"

[Files]
Source: "{#ProjectPath}\dist\partycja.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Partycja"; Filename: "{app}\partycja.exe"
Name: "{commondesktop}\Partycja"; Filename: "{app}\partycja.exe"

[Run]
Filename: "{app}\partycja.exe"; Description: "Uruchom Partycja"; Flags: nowait postinstall skipifsilent

; Note: replace {#ProjectPath} with the actual project path when compiling,
; or compile from the project folder so the relative path works.
