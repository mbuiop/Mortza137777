#!/usr/bin/env python3
"""
Galaxy Advanced 3D Game Installer - نصب کننده بازی
ACTOn Game Studio
"""

import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
import tarfile
import shutil
from pathlib import Path

class GameInstaller:
    """نصب کننده حرفه‌ای بازی"""
    
    def __init__(self):
        self.game_name = "Galaxy Advanced 3D Game"
        self.version = "1.0.0"
        self.developer = "ACTOn Game Studio"
        self.install_dir = self.get_default_install_dir()
        self.required_packages = self.get_required_packages()
        
    def get_default_install_dir(self):
        """دریافت مسیر پیش‌فرض نصب"""
        system = platform.system()
        
        if system == "Windows":
            return Path.home() / "AppData" / "Local" / "GalaxyGame"
        elif system == "Darwin":  # macOS
            return Path.home() / "Applications" / "GalaxyGame.app"
        else:  # Linux و سایر سیستم‌ها
            return Path.home() / ".local" / "share" / "galaxy-game"
            
    def get_required_packages(self):
        """لیست پکیج‌های مورد نیاز"""
        return {
            'pygame': 'pygame',
            'numpy': 'numpy', 
            'opencv-python': 'cv2',
            'Pillow': 'PIL',
            'pyopengl': 'OpenGL',
            'pygame-gui': 'pygame_gui'
        }
        
    def check_system_requirements(self):
        """بررسی نیازمندی‌های سیستم"""
        print("🔍 Checking system requirements...")
        
        system = platform.system()
        arch = platform.architecture()[0]
        python_version = platform.python_version()
        
        print(f"💻 System: {system} {arch}")
        print(f"🐍 Python: {python_version}")
        
        # بررسی حداقل نیازمندی‌ها
        min_python = (3, 8)
        current_python = tuple(map(int, python_version.split('.')[:2]))
        
        if current_python < min_python:
            print(f"❌ Python {min_python[0]}.{min_python[1]}+ required")
            return False
            
        # بررسی حافظه
        try:
            import psutil
            memory_gb = psutil.virtual_memory().total / (1024**3)
            if memory_gb < 2:
                print("❌ At least 2GB RAM required")
                return False
            print(f"💾 RAM: {memory_gb:.1f} GB")
        except ImportError:
            print("⚠️ Could not check RAM (psutil not available)")
            
        # بررسی فضای دیسک
        disk_free_gb = shutil.disk_usage(self.install_dir).free / (1024**3)
        if disk_free_gb < 1:
            print("❌ At least 1GB free disk space required")
            return False
        print(f"💿 Free space: {disk_free_gb:.1f} GB")
        
        print("✅ System requirements met!")
        return True
        
    def install_python_packages(self):
        """نصب پکیج‌های پایتون"""
        print("📦 Installing Python packages...")
        
        for package, import_name in self.required_packages.items():
            try:
                # بررسی اگر پکیج از قبل نصب شده
                __import__(import_name)
                print(f"✅ {package} already installed")
            except ImportError:
                print(f"📥 Installing {package}...")
                try:
                    subprocess.check_call([
                        sys.executable, "-m", "pip", "install", package
                    ])
                    print(f"✅ {package} installed successfully")
                except subprocess.CalledProcessError:
                    print(f"❌ Failed to install {package}")
                    return False
                    
        print("✅ All Python packages installed!")
        return True
        
    def create_game_directory(self):
        """ایجاد دایرکتوری بازی"""
        print("📁 Creating game directory...")
        
        try:
            self.install_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ Game directory created: {self.install_dir}")
            return True
        except Exception as e:
            print(f"❌ Failed to create game directory: {e}")
            return False
            
    def copy_game_files(self):
        """کپی فایل‌های بازی"""
        print("📄 Copying game files...")
        
        try:
            # کپی فایل‌های اصلی
            current_dir = Path(__file__).parent
            game_files = [
                'galaxy_game_3d.py',
                'game_entities.py', 
                'requirements.txt'
            ]
            
            for file in game_files:
                source = current_dir / file
                destination = self.install_dir / file
                if source.exists():
                    shutil.copy2(source, destination)
                    print(f"✅ Copied {file}")
                    
            # ایجاد فایل اجرایی
            self.create_launcher()
            
            print("✅ Game files copied successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to copy game files: {e}")
            return False
            
    def create_launcher(self):
        """ایجاد فایل اجرایی"""
        system = platform.system()
        launcher_content = self.generate_launcher_script()
        launcher_path = self.install_dir / self.get_launcher_name()
        
        try:
            with open(launcher_path, 'w', encoding='utf-8') as f:
                f.write(launcher_content)
                
            # قابل اجرا کردن در لینوکس و مک
            if system != "Windows":
                launcher_path.chmod(0o755)
                
            print(f"✅ Launcher created: {launcher_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create launcher: {e}")
            return False
            
    def get_launcher_name(self):
        """نام فایل اجرایی بر اساس سیستم عامل"""
        system = platform.system()
        if system == "Windows":
            return "GalaxyGame.bat"
        else:
            return "GalaxyGame.sh"
            
    def generate_launcher_script(self):
        """تولید اسکریپت اجرایی"""
        system = platform.system()
        game_script = self.install_dir / "galaxy_game_3d.py"
        
        if system == "Windows":
            return f'''@echo off
chcp 65001 >nul
echo Starting Galaxy Advanced 3D Game...
echo Developed by ACTOn Game Studio
python "{game_script}" %*
pause
'''
        else:
            return f'''#!/bin/bash
echo "Starting Galaxy Advanced 3D Game..."
echo "Developed by ACTOn Game Studio"
cd "{self.install_dir}"
python3 "{game_script}" "$@"
'''
        
    def create_desktop_shortcut(self):
        """ایجاد میانبر دسکتاپ"""
        system = platform.system()
        
        if system == "Windows":
            self.create_windows_shortcut()
        elif system == "Darwin":
            self.create_mac_shortcut()
        else:
            self.create_linux_shortcut()
            
    def create_windows_shortcut(self):
        """ایجاد میانبر ویندوز"""
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, "Galaxy Advanced 3D Game.lnk")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = str(self.install_dir / "GalaxyGame.bat")
            shortcut.WorkingDirectory = str(self.install_dir)
            shortcut.IconLocation = str(self.install_dir / "game_icon.ico")
            shortcut.save()
            
            print("✅ Windows desktop shortcut created!")
            
        except ImportError:
            print("⚠️ Could not create Windows shortcut (pywin32 not available)")
        except Exception as e:
            print(f"⚠️ Could not create desktop shortcut: {e}")
            
    def create_mac_shortcut(self):
        """ایجاد میانبر مک"""
        try:
            app_dir = Path.home() / "Applications" / "GalaxyGame.app"
            app_dir.mkdir(parents=True, exist_ok=True)
            
            # ایجاد ساختار برنامه مک
            contents_dir = app_dir / "Contents" / "MacOS"
            contents_dir.mkdir(parents=True, exist_ok=True)
            
            # اسکریپت اجرایی
            launcher_script = contents_dir / "GalaxyGame"
            with open(launcher_script, 'w') as f:
                f.write('''#!/bin/bash
cd "{}"
python3 "{}"
'''.format(self.install_dir, self.install_dir / "galaxy_game_3d.py"))
            
            launcher_script.chmod(0o755)
            
            # فایل Info.plist
            plist_path = app_dir / "Contents" / "Info.plist"
            with open(plist_path, 'w') as f:
                f.write('''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>GalaxyGame</string>
    <key>CFBundleName</key>
    <string>Galaxy Advanced 3D Game</string>
    <key>CFBundleIdentifier</key>
    <string>com.acton.galaxygame</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
</dict>
</plist>''')
            
            print("✅ macOS application bundle created!")
            
        except Exception as e:
            print(f"⚠️ Could not create macOS shortcut: {e}")
            
    def create_linux_shortcut(self):
        """ایجاد میانبر لینوکس"""
        try:
            desktop_file = Path.home() / ".local" / "share" / "applications" / "galaxy-game.desktop"
            desktop_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(desktop_file, 'w') as f:
                f.write(f'''[Desktop Entry]
Version=1.0
Type=Application
Name=Galaxy Advanced 3D Game
Comment=Epic space adventure game
Exec={self.install_dir / "GalaxyGame.sh"}
Path={self.install_dir}
Icon={self.install_dir / "game_icon.png"}
Terminal=false
Categories=Game;
''')
            
            print("✅ Linux desktop shortcut created!")
            
        except Exception as e:
            print(f"⚠️ Could not create Linux shortcut: {e}")
            
    def create_game_icon(self):
        """ایجاد آیکون بازی"""
        try:
            # اینجا می‌توان یک آیکون ساده ایجاد کرد
            # در نسخه واقعی، یک فایل آیکون واقعی استفاده می‌شود
            icon_path = self.install_dir / "game_icon.png"
            
            # ایجاد یک آیکون ساده با PIL
            from PIL import Image, ImageDraw
            
            img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # رسم یک سفینه ساده
            draw.ellipse([16, 16, 48, 48], fill=(0, 100, 255))
            draw.polygon([32, 12, 24, 32, 40, 32], fill=(255, 200, 0))
            
            img.save(icon_path)
            print("✅ Game icon created!")
            
        except ImportError:
            print("⚠️ Could not create game icon (PIL not available)")
        except Exception as e:
            print(f"⚠️ Could not create game icon: {e}")
            
    def verify_installation(self):
        """بررسی صحت نصب"""
        print("🔍 Verifying installation...")
        
        required_files = [
            'galaxy_game_3d.py',
            'game_entities.py',
            self.get_launcher_name()
        ]
        
        for file in required_files:
            if not (self.install_dir / file).exists():
                print(f"❌ Missing file: {file}")
                return False
                
        # تست اجرای بازی
        try:
            result = subprocess.run([
                sys.executable, "-c", 
                "import pygame; import numpy; print('✅ Dependencies OK')"
            ], capture_output=True, text=True, cwd=self.install_dir, timeout=10)
            
            if "OK" in result.stdout:
                print("✅ Game dependencies verified!")
            else:
                print("❌ Dependency check failed")
                return False
                
        except subprocess.TimeoutExpired:
            print("⚠️ Dependency check timed out")
        except Exception as e:
            print(f"⚠️ Verification error: {e}")
            
        print("✅ Installation verified successfully!")
        return True
        
    def show_installation_summary(self):
        """نمایش خلاصه نصب"""
        print("\n" + "="*50)
        print("🎉 GALAXY ADVANCED 3D GAME INSTALLATION COMPLETE!")
        print("="*50)
        print(f"📁 Installation directory: {self.install_dir}")
        print(f"🚀 Launcher: {self.install_dir / self.get_launcher_name()}")
        print(f"👨‍💻 Developer: {self.developer}")
        print(f"🔄 Version: {self.version}")
        print("\n🎮 How to play:")
        print("  - Arrow keys: Move spaceship")
        print("  - Space: Shoot")
        print("  - ESC: Pause/Quit")
        print("\n🌟 Enjoy your space adventure!")
        print("="*50)
        
    def install(self):
        """اجرای فرآیند نصب کامل"""
        print("🚀 Galaxy Advanced 3D Game Installer")
        print("👨‍💻 Developed by ACTOn Game Studio")
        print("="*50)
        
        # بررسی نیازمندی‌های سیستم
        if not self.check_system_requirements():
            print("❌ System requirements not met. Installation aborted.")
            return False
            
        # ایجاد دایرکتوری بازی
        if not self.create_game_directory():
            return False
            
        # نصب پکیج‌های پایتون
        if not self.install_python_packages():
            return False
            
        # کپی فایل‌های بازی
        if not self.copy_game_files():
            return False
            
        # ایجاد آیکون
        self.create_game_icon()
        
        # ایجاد میانبر
        self.create_desktop_shortcut()
        
        # بررسی نصب
        if not self.verify_installation():
            return False
            
        # نمایش خلاصه
        self.show_installation_summary()
        
        print("✅ Installation completed successfully!")
        return True
        
    def uninstall(self):
        """حذف بازی"""
        print("🗑️ Uninstalling Galaxy Advanced 3D Game...")
        
        try:
            if self.install_dir.exists():
                shutil.rmtree(self.install_dir)
                print(f"✅ Removed game directory: {self.install_dir}")
                
            # حذف میانبرهای دسکتاپ
            self.remove_desktop_shortcuts()
            
            print("✅ Game uninstalled successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Uninstall failed: {e}")
            return False
            
    def remove_desktop_shortcuts(self):
        """حذف میانبرهای دسکتاپ"""
        system = platform.system()
        
        try:
            if system == "Windows":
                import winshell
                desktop = winshell.desktop()
                shortcut_path = os.path.join(desktop, "Galaxy Advanced 3D Game.lnk")
                if os.path.exists(shortcut_path):
                    os.remove(shortcut_path)
                    
            elif system == "Darwin":
                app_dir = Path.home() / "Applications" / "GalaxyGame.app"
                if app_dir.exists():
                    shutil.rmtree(app_dir)
                    
            else:  # Linux
                desktop_file = Path.home() / ".local" / "share" / "applications" / "galaxy-game.desktop"
                if desktop_file.exists():
                    desktop_file.unlink()
                    
            print("✅ Desktop shortcuts removed!")
            
        except Exception as e:
            print(f"⚠️ Could not remove desktop shortcuts: {e}")

def main():
    """تابع اصلی نصب کننده"""
    installer = GameInstaller()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--uninstall":
        installer.uninstall()
    else:
        installer.install()

if __name__ == "__main__":
    main()
