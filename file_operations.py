"""
Text Editor - File Operations Module

This module handles file operations like opening, saving, and creating new files.
"""

import os


def file_new(editor):
    """Create a new empty file."""
    editor.lines = [""]
    editor.cursor_x = 0
    editor.cursor_y = 0
    editor.scroll_y = 0
    editor.file_path = None
    editor.modified = False
    editor.redraw()


def file_open(editor):
    """Open a file dialog and load a file."""
    # Since we don't have a proper file dialog in this environment,
    # we'll simulate by asking for a filename in the status bar
    editor.draw_rect(0, 0, editor.canvas_width,
                     editor.status_height, editor.status_bg_color)
    editor.draw_text(editor.padding, 3, editor.status_text_color,
                     "Enter filename to open: ")

    try:
        file_path = input("Enter filename to open: ")
        with open(file_path, 'r') as f:
            editor.lines = f.read().splitlines()
            if not editor.lines or editor.lines[-1] != "":
                editor.lines.append("")
            editor.file_path = file_path
            editor.cursor_x = 0
            editor.cursor_y = 0
            editor.scroll_y = 0
            editor.modified = False
            print(f"Opened file: {file_path}")
    except Exception as e:
        print(f"Error opening file: {e}")

    editor.redraw()


def file_save(editor):
    """Save the current file."""
    if not editor.file_path:
        file_path = input("Enter filename to save: ")
        if not file_path:
            print("Save cancelled")
            editor.redraw()
            return
        editor.file_path = file_path

    try:
        with open(editor.file_path, 'w') as f:
            f.write('\n'.join(editor.lines))
        editor.modified = False
        print(f"Saved file: {editor.file_path}")
    except Exception as e:
        print(f"Error saving file: {e}")

    editor.redraw()
