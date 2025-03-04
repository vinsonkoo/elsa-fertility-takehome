"""
Text Editor - Runner Script

This script sets up the Python environment correctly and launches the text editor.
It ensures all imports work properly regardless of how the script is executed.
"""

import os
import sys
import subprocess
import time


def ensure_socket_canvas_running():
    """Check if socket_canvas.py is running, and start it if not."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 5005))
        s.close()
        print("Socket Canvas already running.")
        return True
    except:
        print("Starting Socket Canvas...")
        try:
            process = subprocess.Popen(
                [sys.executable, 'socket_canvas.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            time.sleep(1)
            return True
        except Exception as e:
            print(f"Error starting Socket Canvas: {e}")
            return False


def run_text_editor():
    """Set up environment and run the text editor."""
    # Add the current directory to the Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    try:
        from main import main
        main()
    except ImportError as e:
        print(f"Error importing main module: {e}")
        print("Attempting to run main.py directly...")

        try:
            subprocess.run([sys.executable, 'main.py'])
        except Exception as e:
            print(f"Error running main.py: {e}")
            return False

    return True


if __name__ == "__main__":
    if ensure_socket_canvas_running():
        run_text_editor()
    else:
        print("Failed to start Socket Canvas. Please start it manually and try again.")
