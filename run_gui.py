#!/usr/bin/env python3
"""
Wumpus World Pygame GUI Launcher
Simple launcher for the pygame-based graphical interface
"""

import sys
import os
import subprocess

def check_pygame():
    """Check if pygame is installed"""
    try:
        import pygame
        return True
    except ImportError:
        return False

def install_pygame():
    """Install pygame"""
    print("Installing pygame...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Main launcher function"""
    print("🏰 Wumpus World - AI Agent GUI Launcher")
    print("=" * 50)
    
    # Check if pygame is available
    if not check_pygame():
        print("❌ Pygame not found!")
        print("Would you like to install it? (y/n): ", end="")
        response = input().lower().strip()
        
        if response in ['y', 'yes']:
            if install_pygame():
                print("✅ Pygame installed successfully!")
            else:
                print("❌ Failed to install pygame")
                print("Please install manually: pip install pygame")
                return
        else:
            print("Please install pygame manually: pip install pygame")
            return
    
    print("✅ Pygame is available")
    print("🚀 Starting Wumpus World GUI...")
    
    # Change to the source directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(script_dir, "Source")
    
    if os.path.exists(source_dir):
        os.chdir(source_dir)
    
    # Import and run the GUI
    try:
        # Add Source directory to Python path
        if source_dir not in sys.path:
            sys.path.insert(0, source_dir)
        
        from pygame_gui import WumpusWorldPygameGUI
        gui = WumpusWorldPygameGUI()
        gui.run()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required files are in the Source directory")
        print("Available files:", os.listdir(source_dir) if os.path.exists(source_dir) else "Source directory not found")
    except Exception as e:
        print(f"❌ Error running GUI: {e}")

if __name__ == "__main__":
    main()
