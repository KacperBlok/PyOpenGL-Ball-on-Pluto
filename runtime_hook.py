import os
import sys

def debug_print():
    print("Current working directory:", os.getcwd())
    print("Directory contents:", os.listdir())
    if hasattr(sys, '_MEIPASS'):
        print("PyInstaller directory:", sys._MEIPASS)
        print("PyInstaller directory contents:", os.listdir(sys._MEIPASS))

debug_print()