; Script Inno Setup para Sistema PyME Chile
; Requiere: Inno Setup 6+ (https://jrsoftware.org/isinfo.php)
; Requiere: Docker Desktop instalado en el equipo destino

#define MyAppName "Sistema PyME Chile"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Tu Empresa"
#define MyAppURL "http://localhost:8000"
#define MyAppExeName "pyme-launcher.exe"

[Setup]
AppId={{E8A2F4B6-3D7C-4E8A-9F2B-1A5C7D9E3F6B}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={autopf}\PyMEChile
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=
OutputDir=output
OutputBaseFilename=Sistema-PyME-Chile-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
Source: "..\docker-compose.yml"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\backend\*"; DestDir: "{app}\backend"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\frontend\*"; DestDir: "{app}\frontend"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "pyme-launcher.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "pyme-stop.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "setup-first-run.bat"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\pyme-launcher.bat"; WorkingDir: "{app}"
Name: "{group}\Detener Sistema"; Filename: "{app}\pyme-stop.bat"; WorkingDir: "{app}"
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\pyme-launcher.bat"; WorkingDir: "{app}"

[Run]
Filename: "{app}\setup-first-run.bat"; Parameters: ""; WorkingDir: "{app}"; \
  Description: "Configurar e iniciar el sistema por primera vez"; \
  Flags: postinstall waituntilterminated runascurrentuser

[Code]
function DockerInstalled(): Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec('docker', '--version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Result := Result and (ResultCode = 0);
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  if not DockerInstalled() then begin
    MsgBox('Docker Desktop no está instalado.' + #13#10 +
           'Por favor instala Docker Desktop desde https://www.docker.com/products/docker-desktop/' + #13#10 +
           'y reinicia la instalación.', mbError, MB_OK);
    Result := False;
  end;
end;
