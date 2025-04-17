"""
GeoTherm - Instalador

Este script cria um instalador para o programa GeoTherm.
"""

import os
import sys
import platform
import shutil
import subprocess
import zipfile

def create_installer():
    """Cria um instalador para o programa GeoTherm."""
    print("Criando instalador para o GeoTherm...")
    
    # Detectar sistema operacional
    system = platform.system()
    print(f"Sistema operacional detectado: {system}")
    
    # Criar diretório de build
    build_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build")
    dist_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
    
    # Limpar diretórios anteriores
    for directory in [build_dir, dist_dir]:
        if os.path.exists(directory):
            print(f"Limpando diretório: {directory}")
            shutil.rmtree(directory)
        os.makedirs(directory)
    
    # Verificar se PyInstaller está instalado
    try:
        import PyInstaller
        print("PyInstaller encontrado.")
    except ImportError:
        print("PyInstaller não encontrado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Criar especificação para PyInstaller
    spec_file = os.path.join(build_dir, "GeoTherm.spec")
    
    with open(spec_file, "w") as f:
        f.write("""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GeoTherm',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GeoTherm',
)
""")
    
    # Criar ícone
    resources_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")
    if not os.path.exists(resources_dir):
        os.makedirs(resources_dir)
    
    # Executar PyInstaller
    print("Executando PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "PyInstaller", spec_file])
    
    # Criar instalador específico para cada sistema operacional
    if system == "Windows":
        create_windows_installer(dist_dir)
    elif system == "Darwin":  # macOS
        create_macos_installer(dist_dir)
    elif system == "Linux":
        create_linux_installer(dist_dir)
    else:
        print(f"Sistema operacional não suportado: {system}")
        create_zip_package(dist_dir)
    
    print("Instalador criado com sucesso!")

def create_windows_installer(dist_dir):
    """
    Cria um instalador para Windows.
    
    Parâmetros:
        dist_dir (str): Diretório de distribuição
    """
    print("Criando instalador para Windows...")
    
    # Verificar se NSIS está disponível
    nsis_available = False
    try:
        subprocess.check_call(["makensis", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        nsis_available = True
    except (subprocess.SubprocessError, FileNotFoundError):
        print("NSIS não encontrado. Criando pacote ZIP em vez de instalador.")
    
    if nsis_available:
        # Criar script NSIS
        nsis_script = os.path.join(dist_dir, "GeoTherm_installer.nsi")
        
        with open(nsis_script, "w") as f:
            f.write("""
!include "MUI2.nsh"

; Definir informações do instalador
Name "GeoTherm"
OutFile "GeoTherm_Setup.exe"
InstallDir "$PROGRAMFILES\\GeoTherm"
InstallDirRegKey HKCU "Software\\GeoTherm" ""

; Solicitar privilégios de administrador
RequestExecutionLevel admin

; Interface
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\\Contrib\\Graphics\\Icons\\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\\Contrib\\Graphics\\Icons\\modern-uninstall.ico"

; Páginas
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Idiomas
!insertmacro MUI_LANGUAGE "Portuguese"

; Seção principal
Section "GeoTherm" SecMain
  SetOutPath "$INSTDIR"
  
  ; Copiar arquivos
  File /r "GeoTherm\\*.*"
  
  ; Criar atalhos
  CreateDirectory "$SMPROGRAMS\\GeoTherm"
  CreateShortcut "$SMPROGRAMS\\GeoTherm\\GeoTherm.lnk" "$INSTDIR\\GeoTherm.exe"
  CreateShortcut "$DESKTOP\\GeoTherm.lnk" "$INSTDIR\\GeoTherm.exe"
  
  ; Registrar desinstalador
  WriteRegStr HKCU "Software\\GeoTherm" "" $INSTDIR
  WriteUninstaller "$INSTDIR\\Uninstall.exe"
  CreateShortcut "$SMPROGRAMS\\GeoTherm\\Desinstalar.lnk" "$INSTDIR\\Uninstall.exe"
SectionEnd

; Seção de desinstalação
Section "Uninstall"
  ; Remover arquivos
  RMDir /r "$INSTDIR"
  
  ; Remover atalhos
  Delete "$DESKTOP\\GeoTherm.lnk"
  RMDir /r "$SMPROGRAMS\\GeoTherm"
  
  ; Remover registro
  DeleteRegKey HKCU "Software\\GeoTherm"
SectionEnd
""")
        
        # Executar NSIS
        print("Executando NSIS...")
        subprocess.check_call(["makensis", nsis_script])
        
        # Mover instalador para diretório de distribuição
        shutil.move(os.path.join(os.path.dirname(dist_dir), "GeoTherm_Setup.exe"), os.path.join(dist_dir, "GeoTherm_Setup.exe"))
    else:
        create_zip_package(dist_dir)

def create_macos_installer(dist_dir):
    """
    Cria um instalador para macOS.
    
    Parâmetros:
        dist_dir (str): Diretório de distribuição
    """
    print("Criando instalador para macOS...")
    
    # Criar arquivo .app
    app_dir = os.path.join(dist_dir, "GeoTherm.app")
    if os.path.exists(app_dir):
        shutil.rmtree(app_dir)
    
    # Criar estrutura de diretórios
    os.makedirs(os.path.join(app_dir, "Contents", "MacOS"))
    os.makedirs(os.path.join(app_dir, "Contents", "Resources"))
    
    # Copiar executável
    shutil.copytree(os.path.join(dist_dir, "GeoTherm"), os.path.join(app_dir, "Contents", "MacOS", "GeoTherm"))
    
    # Criar arquivo Info.plist
    with open(os.path.join(app_dir, "Contents", "Info.plist"), "w") as f:
        f.write("""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>GeoTherm</string>
    <key>CFBundleIconFile</key>
    <string>GeoTherm.icns</string>
    <key>CFBundleIdentifier</key>
    <string>com.geotherm.app</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>GeoTherm</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
""")
    
    # Verificar se hdiutil está disponível
    try:
        subprocess.check_call(["hdiutil", "version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Criar arquivo DMG
        dmg_file = os.path.join(dist_dir, "GeoTherm.dmg")
        subprocess.check_call([
            "hdiutil", "create", "-volname", "GeoTherm", "-srcfolder", app_dir,
            "-ov", "-format", "UDZO", dmg_file
        ])
        
        print(f"Arquivo DMG criado: {dmg_file}")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("hdiutil não encontrado. Criando apenas o arquivo .app.")

def create_linux_installer(dist_dir):
    """
    Cria um instalador para Linux.
    
    Parâmetros:
        dist_dir (str): Diretório de distribuição
    """
    print("Criando instalador para Linux...")
    
    # Criar script de instalação
    install_script = os.path.join(dist_dir, "install.sh")
    
    with open(install_script, "w") as f:
        f.write("""#!/bin/bash

# Script de instalação do GeoTherm

# Verificar se está sendo executado como root
if [ "$EUID" -ne 0 ]; then
  echo "Este script deve ser executado como root (sudo)."
  exit 1
fi

# Diretório de instalação
INSTALL_DIR="/opt/geotherm"

# Criar diretório de instalação
mkdir -p "$INSTALL_DIR"

# Copiar arquivos
cp -r GeoTherm/* "$INSTALL_DIR"

# Tornar executável
chmod +x "$INSTALL_DIR/GeoTherm"

# Criar link simbólico
ln -sf "$INSTALL_DIR/GeoTherm" "/usr/local/bin/geotherm"

# Criar arquivo .desktop
cat > /usr/share/applications/geotherm.desktop << EOF
[Desktop Entry]
Name=GeoTherm
Comment=Programa para Modelamento de Fluxo Térmico
Exec=$INSTALL_DIR/GeoTherm
Icon=$INSTALL_DIR/resources/icon.png
Terminal=false
Type=Application
Categories=Science;Education;
EOF

echo "GeoTherm instalado com sucesso!"
echo "Execute 'geotherm' no terminal ou procure por 'GeoTherm' no menu de aplicativos."
""")
    
    # Tornar script executável
    os.chmod(install_script, 0o755)
    
    # Criar script de desinstalação
    uninstall_script = os.path.join(dist_dir, "uninstall.sh")
    
    with open(uninstall_script, "w") as f:
        f.write("""#!/bin/bash

# Script de desinstalação do GeoTherm

# Verificar se está sendo executado como root
if [ "$EUID" -ne 0 ]; then
  echo "Este script deve ser executado como root (sudo)."
  exit 1
fi

# Remover arquivos
rm -rf "/opt/geotherm"
rm -f "/usr/local/bin/geotherm"
rm -f "/usr/share/applications/geotherm.desktop"

echo "GeoTherm desinstalado com sucesso!"
""")
    
    # Tornar script executável
    os.chmod(uninstall_script, 0o755)
    
    # Criar pacote tar.gz
    tar_file = os.path.join(dist_dir, "GeoTherm_Linux.tar.gz")
    
    # Mudar para o diretório de distribuição
    current_dir = os.getcwd()
    os.chdir(dist_dir)
    
    try:
        # Criar arquivo tar.gz
        subprocess.check_call([
            "tar", "-czf", os.path.basename(tar_file), "GeoTherm", "install.sh", "uninstall.sh"
        ])
        
        print(f"Arquivo tar.gz criado: {tar_file}")
    except subprocess.SubprocessError:
        print("Erro ao criar arquivo tar.gz.")
    
    # Voltar para o diretório original
    os.chdir(current_dir)

def create_zip_package(dist_dir):
    """
    Cria um pacote ZIP.
    
    Parâmetros:
        dist_dir (str): Diretório de distribuição
    """
    print("Criando pacote ZIP...")
    
    # Criar arquivo ZIP
    zip_file = os.path.join(dist_dir, "GeoTherm.zip")
    
    with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Adicionar arquivos
        for root, _, files in os.walk(os.path.join(dist_dir, "GeoTherm")):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, dist_dir)
                zipf.write(file_path, arcname)
    
    print(f"Arquivo ZIP criado: {zip_file}")

if __name__ == "__main__":
    create_installer()
