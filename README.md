# Simple Text Editor

A modular text editor built using a socket-based canvas API.

## Prerequisites

- Python 3.x

## Setup and Running

### Option 1: Using the Launcher

1. Run the launcher script:
   ```
   python run.py
   ```
   This will automatically:
   - Start the socket canvas server if it's not already running
   - Launch the text editor

### Option 2: Manual Start

1. Start the socket canvas API in one terminal:
   ```
   python socket_canvas.py
   ```

2. Launch the text editor in another terminal:
   ```
   python main.py
   ```

## Features

- Basic text editing
- Navigation (arrow keys, Home/End, Page Up/Down)
- Text selection with mouse or keyboard
- Clipboard operations (copy, cut, paste)
- File operations (new, open, save)
- Status bar with file information
- Line numbers

## Keyboard Shortcuts

- **Ctrl+N**: Create new document
- **Ctrl+O**: Open file
- **Ctrl+S**: Save file
- **Ctrl+C**: Copy selected text
- **Ctrl+X**: Cut selected text
- **Ctrl+V**: Paste text

## Project Structure

- **run.py**: Launcher script that handles environment setup
- **socket_canvas.py**: Underlying canvas API server
- **main.py**: Entry point for the editor
- **editor.py**: Core editor class
- **cursor.py**: Cursor movement handling
- **selection.py**: Text selection operations
- **input_handlers.py**: Keyboard and mouse input processing
- **file_operations.py**: File saving/loading
- **ui.py**: Rendering and display functions

## Implementation Notes

This text editor demonstrates a clean, modular architecture with separate components for different aspects of functionality. It uses a socket-based approach to communicate between the text editor logic and the canvas display, showing how to build a GUI application with a client-server architecture.