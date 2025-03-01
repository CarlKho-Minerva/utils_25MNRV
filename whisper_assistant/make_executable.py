"""
Script to create a standalone executable for Carl's Whisper Assistant
"""
import os
import subprocess
import sys

def create_executable():
    """Create a standalone executable using PyInstaller"""
    try:
        # Check if PyInstaller is installed
        try:
            import PyInstaller
        except ImportError:
            print("PyInstaller not found. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
        # Get the script directory - use forward slashes to avoid escape issues
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_dir_safe = script_dir.replace('\\', '/')
        
        # Create spec file for better control
        spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{script_dir_safe}/tray_app.py'],
    pathex=['{script_dir_safe}'],
    binaries=[],
    datas=[],
    hiddenimports=['pynput.keyboard._win32', 'pynput.mouse._win32'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Add .env file if it exists
if os.path.exists(os.path.join(r'{script_dir}', '.env')):
    a.datas += [('.env', os.path.join(r'{script_dir}', '.env'), 'DATA')]

# Add icon file if it exists
if os.path.exists(os.path.join(r'{script_dir}', 'carls_whisper.ico')):
    a.datas += [('carls_whisper.ico', os.path.join(r'{script_dir}', 'carls_whisper.ico'), 'DATA')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="Carls Whisper",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon=os.path.join(r'{script_dir}', 'carls_whisper.ico') if os.path.exists(os.path.join(r'{script_dir}', 'carls_whisper.ico')) else None,
)
"""
        
        # Write the spec file with proper escaping for Windows paths
        spec_path = os.path.join(script_dir, "whisper_assistant.spec")
        with open(spec_path, "w") as f:
            f.write(spec_content)
        
        # Run PyInstaller
        print("Building executable...")
        subprocess.check_call([
            sys.executable, 
            "-m", 
            "PyInstaller", 
            "--clean",
            spec_path
        ])
        
        print("\nBuild complete!")
        print(f"Executable can be found in: {os.path.join(script_dir, 'dist')}")
        
        return True
    except Exception as e:
        print(f"Error creating executable: {str(e)}")
        return False

if __name__ == "__main__":
    create_executable()
