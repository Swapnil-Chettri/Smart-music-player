import sys
import os
import platform


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)


if platform.system() == "Windows":
    
    vlc_paths = [
        r"C:\Program Files\VideoLAN\VLC",
        r"C:\Program Files (x86)\VideoLAN\VLC"
    ]
    
    vlc_found = False
    for path in vlc_paths:
        if os.path.exists(path):
            try:
                os.add_dll_directory(path)
                print(f"✅ VLC found and registered at: {path}")
                vlc_found = True
                break
            except Exception as e:
                print(f"⚠️ Could not register DLL directory: {e}")
    
    if not vlc_found:
        print("❌ WARNING: VLC installation not found in standard paths.")
        print("   If the app crashes, ensure VLC is installed.")


try:
    from src.ui.main_window import App
    import tkinter as tk
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("   Make sure you are running this from the root folder using: python -m src.main")
    sys.exit(1)

if __name__ == "__main__":
    print("🚀 Starting Smart Music Player...")
    
    
    app = App()
    

    try:
        app.mainloop()
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user.")
