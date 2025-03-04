"""
Text Editor - Main Entry Point

This module serves as the entry point for the text editor application.
It initializes the editor and handles the main program loop.
"""

import time
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from editor import TextEditor
except ImportError as e:
    print(f"Error importing TextEditor: {e}")
    print("Make sure all module files are in the same directory.")
    sys.exit(1)


def main():
    """Start the text editor application."""
    editor = TextEditor()

    if not editor.connect():
        return

    try:
        print("Text editor is running. Press Ctrl+C to exit...")
        print("\nKeyboard shortcuts:")
        print("  Ctrl+S: Save file")
        print("  Ctrl+O: Open file")
        print("  Ctrl+N: New file")
        print("  Ctrl+C: Copy")
        print("  Ctrl+X: Cut")
        print("  Ctrl+V: Paste")

        while editor.running:
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nEditor closed by user")

    finally:
        editor.disconnect()


if __name__ == "__main__":
    main()
