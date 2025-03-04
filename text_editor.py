"""
Simple Text Editor

A Tkinter-based text editor implementation using the socket canvas API.
Features: text input/editing, selection, copy/paste, basic file operations.

Usage:
    1. Start socket canvas: python socket_canvas.py
    2. Run editor: python text_editor.py
"""

import socket
import threading
import time
import os


class TextEditor:
    """A simple text editor using the socket canvas API."""

    def __init__(self, host='127.0.0.1', port=5005):
        # Socket connection
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.event_thread = None
        self.running = False

        # Canvas properties
        self.canvas_width = 800
        self.canvas_height = 600

        # Text editor state
        self.lines = [""]
        self.cursor_x = 0
        self.cursor_y = 0
        self.scroll_y = 0
        self.file_path = None
        self.modified = False

        # Selection state
        self.selection_active = False
        self.selection_start_x = 0
        self.selection_start_y = 0
        self.selection_end_x = 0
        self.selection_end_y = 0

        self.char_width = 8
        self.char_height = 14

        # Editor colors
        self.bg_color = "#ffffff"
        self.text_color = "#000000"
        self.cursor_color = "#ff0000"
        self.status_bg_color = "#cccccc"
        self.status_text_color = "#000000"
        self.line_number_bg_color = "#eeeeee"
        self.line_number_text_color = "#555555"
        self.selection_bg_color = "#add8e6"

        # Editor metrics
        self.padding = 5
        self.status_height = 20
        self.line_number_width = 40
        self.text_area_start_y = self.status_height + self.padding
        self.text_area_start_x = self.line_number_width + self.padding

        # Visible area (in characters)
        self.visible_cols = 0
        self.visible_rows = 0

        # Input state
        self.shift_pressed = False
        self.control_pressed = False
        self.debug_mode = False

        self.clipboard = ""

        # Special key mappings for common operations
        self.key_handlers = {
            'BackSpace': self.backspace_delete_char,
            'Delete': self.delete_forward_char,
            'Return': self.enter_new_line,
            'Tab': lambda: self.text_insert("    "),
            'space': lambda: self.text_insert(" "),
            'Left': self.cursor_move_left,
            'Right': self.cursor_move_right,
            'Up': self.cursor_move_up,
            'Down': self.cursor_move_down,
            'Home': self.cursor_move_line_start,
            'End': self.cursor_move_line_end,
            'Prior': self.cursor_page_up,
            'Next': self.cursor_page_down,
            # Ignore modifier keys
            'Alt_L': lambda: None,
            'Alt_R': lambda: None,
            'Meta_L': lambda: None,
            'Meta_R': lambda: None,
            'Control_L': lambda: None,
            'Control_R': lambda: None
        }

    def connect(self):
        """Connect to the socket canvas server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"Connected to socket canvas at {self.host}:{self.port}")

            # Start the event listening thread
            self.running = True
            self.event_thread = threading.Thread(target=self.listen_for_events)
            self.event_thread.daemon = True
            self.event_thread.start()

            # Initialize the editor UI
            self.update_visible_area()
            self.redraw()

            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False

    def disconnect(self):
        if self.connected:
            self.running = False
            self.socket.close()
            self.connected = False
            print("Disconnected from socket canvas")

    def send_command(self, command):
        if not self.connected:
            print("Not connected to socket canvas")
            return

        try:
            if not command.endswith('\n'):
                command += '\n'
            self.socket.send(command.encode())
        except Exception as e:
            print(f"Failed to send command: {e}")

    def draw_rect(self, x, y, width, height, color):
        self.send_command(f"rect,{x},{y},{width},{height},{color}")

    def draw_text(self, x, y, color, text):
        self.send_command(f"text,{x},{y},{color},{text}")

    def clear(self):
        self.send_command("clear")

    def update_visible_area(self):
        self.visible_cols = (
            self.canvas_width - self.text_area_start_x - self.padding) // self.char_width
        self.visible_rows = (
            self.canvas_height - self.text_area_start_y - self.padding) // self.char_height

    def redraw(self):
        """Redraw the entire editor interface."""
        self.clear()

        self.draw_rect(0, 0, self.canvas_width,
                       self.canvas_height, self.bg_color)

        self.draw_rect(0, 0, self.canvas_width,
                       self.status_height, self.status_bg_color)

        file_name = os.path.basename(
            self.file_path) if self.file_path else "Untitled"
        modified_indicator = "*" if self.modified else ""
        status_text = f"{file_name}{modified_indicator} | Line: {self.cursor_y + 1}/{len(self.lines)} | Col: {self.cursor_x + 1}"
        self.draw_text(self.padding, 3, self.status_text_color, status_text)

        self.draw_rect(0, self.status_height, self.line_number_width,
                       self.canvas_height - self.status_height, self.line_number_bg_color)

        self.draw_line_numbers()
        self.draw_text_content()

        cursor_screen_x = self.text_area_start_x + self.cursor_x * self.char_width
        cursor_screen_y = self.text_area_start_y + \
            (self.cursor_y - self.scroll_y) * self.char_height
        self.draw_rect(cursor_screen_x, cursor_screen_y, 2,
                       self.char_height, self.cursor_color)

    def draw_line_numbers(self):
        visible_end = min(self.scroll_y + self.visible_rows, len(self.lines))

        for i in range(self.scroll_y, visible_end):
            line_number = str(i + 1).rjust(4)
            line_y = self.text_area_start_y + \
                (i - self.scroll_y) * self.char_height
            self.draw_text(self.padding, line_y,
                           self.line_number_text_color, line_number)

    def draw_text_content(self):
        """Draw the visible text content with selection highlighting."""
        visible_end = min(self.scroll_y + self.visible_rows, len(self.lines))
        sel_start_y, sel_start_x, sel_end_y, sel_end_x = self.selection_get_normalized()

        for i in range(self.scroll_y, visible_end):
            line = self.lines[i]
            line_y = self.text_area_start_y + \
                (i - self.scroll_y) * self.char_height

            # If selection is active and this line is within selection
            if self.selection_active and sel_start_y <= i <= sel_end_y:
                if sel_start_y == sel_end_y:  # Selection on a single line
                    # Draw part before selection
                    if sel_start_x > 0:
                        self.draw_text(self.text_area_start_x, line_y,
                                       self.text_color, line[:sel_start_x])

                    # Draw selection background
                    sel_width = (sel_end_x - sel_start_x) * self.char_width
                    if sel_width > 0:
                        self.draw_rect(
                            self.text_area_start_x + sel_start_x * self.char_width,
                            line_y,
                            sel_width,
                            self.char_height,
                            self.selection_bg_color
                        )

                    # Draw selected text
                    self.draw_text(
                        self.text_area_start_x + sel_start_x * self.char_width,
                        line_y,
                        self.text_color,
                        line[sel_start_x:sel_end_x]
                    )

                    # Draw part after selection
                    if sel_end_x < len(line):
                        self.draw_text(
                            self.text_area_start_x + sel_end_x * self.char_width,
                            line_y,
                            self.text_color,
                            line[sel_end_x:]
                        )

                elif i == sel_start_y:  # First line of multi-line selection
                    # Draw part before selection
                    if sel_start_x > 0:
                        self.draw_text(self.text_area_start_x, line_y,
                                       self.text_color, line[:sel_start_x])

                    # Draw selection background
                    sel_width = (len(line) - sel_start_x) * self.char_width
                    if sel_width > 0:
                        self.draw_rect(
                            self.text_area_start_x + sel_start_x * self.char_width,
                            line_y,
                            sel_width,
                            self.char_height,
                            self.selection_bg_color
                        )

                    # Draw selected text
                    self.draw_text(
                        self.text_area_start_x + sel_start_x * self.char_width,
                        line_y,
                        self.text_color,
                        line[sel_start_x:]
                    )

                elif i == sel_end_y:  # Last line of multi-line selection
                    # Draw selection background
                    if sel_end_x > 0:
                        self.draw_rect(
                            self.text_area_start_x,
                            line_y,
                            sel_end_x * self.char_width,
                            self.char_height,
                            self.selection_bg_color
                        )

                    # Draw selected text
                    self.draw_text(
                        self.text_area_start_x,
                        line_y,
                        self.text_color,
                        line[:sel_end_x]
                    )

                    # Draw part after selection
                    if sel_end_x < len(line):
                        self.draw_text(
                            self.text_area_start_x + sel_end_x * self.char_width,
                            line_y,
                            self.text_color,
                            line[sel_end_x:]
                        )

                else:  # Middle lines of multi-line selection
                    # Draw entire line with selection background
                    self.draw_rect(
                        self.text_area_start_x,
                        line_y,
                        len(line) * self.char_width,
                        self.char_height,
                        self.selection_bg_color
                    )

                    # Draw selected text
                    self.draw_text(
                        self.text_area_start_x,
                        line_y,
                        self.text_color,
                        line
                    )
            else:
                # No selection on this line, draw it normally
                self.draw_text(self.text_area_start_x,
                               line_y, self.text_color, line)

    def key_handle_down(self, key):
        """Process keydown events and take appropriate actions."""
        # Handle modifier keys
        if key in ["LeftShift", "RightShift"]:
            self.shift_pressed = True
            return
        elif key in ["LeftControl", "RightControl", "Control_L", "Control_R",
                     "LeftCommand", "RightCommand", "Meta_L", "Meta_R"]:
            self.control_pressed = True
            return
        elif key in ["LeftAlt", "RightAlt", "Alt_L", "Alt_R"]:
            return  # Ignore Alt key presses

        # Handle keyboard shortcuts with Control/Command
        if self.control_pressed:
            if key == "s":
                self.file_save()
                return
            elif key == "o":
                self.file_open()
                return
            elif key == "n":
                self.file_new()
                return
            elif key == "c":
                self.selection_copy()
                return
            elif key == "x":
                self.selection_cut()
                return
            elif key == "v":
                self.text_paste()
                return

        # Handle special keys (arrows, etc.)
        if key in self.key_handlers:
            self.key_handlers[key]()
        # Handle non-standard characters
        elif key == "ø" or key == "??":
            self.text_insert("ø")
        elif key == "ß" or key == "??" or key == "ẞ":
            self.text_insert("ß")
        # Regular character input
        elif len(key) == 1:
            if self.shift_pressed:
                key = key.upper()
            self.text_insert(key)

    def key_handle_up(self, key):
        """Process keyup events to track modifier key states."""
        if key in ["LeftShift", "RightShift"]:
            self.shift_pressed = False
        elif key in ["LeftControl", "RightControl", "Control_L", "Control_R",
                     "LeftCommand", "RightCommand", "Meta_L", "Meta_R"]:
            self.control_pressed = False

    def text_insert(self, text):
        """Insert text at cursor, replacing any selection."""
        if self.selection_active:
            self.selection_delete()
            self.selection_active = False

        current_line = self.lines[self.cursor_y]
        new_line = current_line[:self.cursor_x] + \
            text + current_line[self.cursor_x:]
        self.lines[self.cursor_y] = new_line
        self.cursor_x += len(text)
        self.modified = True
        self.redraw()

    def backspace_delete_char(self):
        """Delete character before cursor or selected text."""
        # Delete selection if active
        if self.selection_active:
            self.selection_delete()
            self.selection_active = False
            self.modified = True
        elif self.cursor_x > 0:
            # Delete character before cursor
            current_line = self.lines[self.cursor_y]
            new_line = current_line[:self.cursor_x-1] + \
                current_line[self.cursor_x:]
            self.lines[self.cursor_y] = new_line
            self.cursor_x -= 1
            self.modified = True
        elif self.cursor_y > 0:
            # Join with previous line
            prev_line = self.lines[self.cursor_y - 1]
            current_line = self.lines[self.cursor_y]
            self.cursor_x = len(prev_line)
            self.lines[self.cursor_y - 1] = prev_line + current_line
            self.lines.pop(self.cursor_y)
            self.cursor_y -= 1
            self.modified = True

        self.cursor_ensure_visible()
        self.redraw()

    def delete_forward_char(self):
        """Delete character after cursor or selected text."""
        # Delete selection if active
        if self.selection_active:
            self.selection_delete()
            self.selection_active = False
            self.modified = True
        else:
            current_line = self.lines[self.cursor_y]
            if self.cursor_x < len(current_line):
                # Delete character at cursor
                new_line = current_line[:self.cursor_x] + \
                    current_line[self.cursor_x+1:]
                self.lines[self.cursor_y] = new_line
                self.modified = True
            elif self.cursor_y < len(self.lines) - 1:
                # Join with next line
                next_line = self.lines[self.cursor_y + 1]
                self.lines[self.cursor_y] = current_line + next_line
                self.lines.pop(self.cursor_y + 1)
                self.modified = True

        self.redraw()

    def enter_new_line(self):
        """Create a new line at the cursor position."""
        current_line = self.lines[self.cursor_y]

        # Split the current line at cursor position
        new_line = current_line[self.cursor_x:]
        self.lines[self.cursor_y] = current_line[:self.cursor_x]

        # Insert the new line after the current one
        self.lines.insert(self.cursor_y + 1, new_line)

        # Move cursor to beginning of new line
        self.cursor_y += 1
        self.cursor_x = 0
        self.modified = True

        self.cursor_ensure_visible()
        self.redraw()

    def cursor_move_left(self):
        """Move the cursor one position to the left."""
        if self.cursor_x > 0:
            self.cursor_x -= 1
        elif self.cursor_y > 0:
            self.cursor_y -= 1
            self.cursor_x = len(self.lines[self.cursor_y])

        self.cursor_ensure_visible()
        self.redraw()

    def cursor_move_right(self):
        """Move the cursor one position to the right."""
        current_line = self.lines[self.cursor_y]

        if self.cursor_x < len(current_line):
            self.cursor_x += 1
        elif self.cursor_y < len(self.lines) - 1:
            self.cursor_y += 1
            self.cursor_x = 0

        self.cursor_ensure_visible()
        self.redraw()

    def cursor_move_up(self):
        """Move the cursor one position up."""
        if self.cursor_y > 0:
            self.cursor_y -= 1
            # Ensure cursor_x is not beyond the end of the new line
            self.cursor_x = min(self.cursor_x, len(self.lines[self.cursor_y]))

        self.cursor_ensure_visible()
        self.redraw()

    def cursor_move_down(self):
        """Move the cursor one position down."""
        if self.cursor_y < len(self.lines) - 1:
            self.cursor_y += 1
            # Ensure cursor_x is not beyond the end of the new line
            self.cursor_x = min(self.cursor_x, len(self.lines[self.cursor_y]))

        self.cursor_ensure_visible()
        self.redraw()

    def cursor_move_line_start(self):
        """Moves the cursor to the start of the current line."""
        self.cursor_x = 0
        self.redraw()

    def cursor_move_line_end(self):
        """Moves the cursor to the end of the current line."""
        self.cursor_x = len(self.lines[self.cursor_y])
        self.redraw()

    def cursor_page_up(self):
        """Move the cursor up by a page."""
        self.cursor_y = max(0, self.cursor_y - self.visible_rows)
        # Ensure cursor_x is not beyond the end of the new line
        self.cursor_x = min(self.cursor_x, len(self.lines[self.cursor_y]))
        self.cursor_ensure_visible()
        self.redraw()

    def cursor_page_down(self):
        """Move the cursor down by a page."""
        self.cursor_y = min(len(self.lines) - 1,
                            self.cursor_y + self.visible_rows)
        # Ensure cursor_x is not beyond the end of the new line
        self.cursor_x = min(self.cursor_x, len(self.lines[self.cursor_y]))
        self.cursor_ensure_visible()
        self.redraw()

    def cursor_ensure_visible(self):
        """Scroll view if needed to ensure cursor is visible."""
        # Scroll up if cursor is above visible area
        if self.cursor_y < self.scroll_y:
            self.scroll_y = self.cursor_y

        # Scroll down if cursor is below visible area
        elif self.cursor_y >= self.scroll_y + self.visible_rows:
            self.scroll_y = self.cursor_y - self.visible_rows + 1

    def mouse_handle_click(self, x, y):
        """Handle mouse click by positioning cursor and starting selection."""
        if x < self.text_area_start_x or y < self.text_area_start_y:
            return

        # Calculate which line was clicked (accounting for scrolling)
        line_index = self.scroll_y + \
            (y - self.text_area_start_y) // self.char_height

        # Ensure the line index is valid
        if line_index >= len(self.lines):
            line_index = len(self.lines) - 1

        # Calculate the character position within the line
        char_index = (x - self.text_area_start_x) // self.char_width

        # Ensure the character index is valid
        current_line = self.lines[line_index]
        if char_index > len(current_line):
            char_index = len(current_line)

        # Update cursor position
        self.cursor_y = line_index
        self.cursor_x = char_index

        # Start a new selection
        self.selection_active = True
        self.selection_start_x = char_index
        self.selection_start_y = line_index
        self.selection_end_x = char_index
        self.selection_end_y = line_index

        self.redraw()

    def mouse_handle_drag(self, x, y):
        """Extend selection during mouse drag."""
        # Ignore if dragging outside text area
        if x < self.text_area_start_x or y < self.text_area_start_y:
            return

        # Calculate text position
        line_index = self.scroll_y + \
            (y - self.text_area_start_y) // self.char_height

        # Auto-scroll if dragging beyond visible area
        if line_index < self.scroll_y:
            self.scroll_y = max(0, self.scroll_y - 1)
        elif line_index >= self.scroll_y + self.visible_rows:
            self.scroll_y = min(
                len(self.lines) - self.visible_rows + 1, self.scroll_y + 1)

        # Ensure the line index is valid
        if line_index >= len(self.lines):
            line_index = len(self.lines) - 1

        # Calculate character position
        char_index = (x - self.text_area_start_x) // self.char_width

        # Ensure the character index is valid
        current_line = self.lines[line_index]
        if char_index > len(current_line):
            char_index = len(current_line)

        # Update selection end point
        self.selection_end_x = char_index
        self.selection_end_y = line_index

        # Update cursor position to match selection end
        self.cursor_x = char_index
        self.cursor_y = line_index

        # Ensure cursor is visible
        self.cursor_ensure_visible()

        # Redraw the editor
        self.redraw()

    def mouse_handle_up(self, x, y):
        """Finalize selection on mouse up."""
        # Update final position if in text area
        if x >= self.text_area_start_x and y >= self.text_area_start_y:
            line_index = self.scroll_y + \
                (y - self.text_area_start_y) // self.char_height

            # Ensure the line index is valid
            if line_index >= len(self.lines):
                line_index = len(self.lines) - 1

            # Calculate character position
            char_index = (x - self.text_area_start_x) // self.char_width

            # Ensure the character index is valid
            current_line = self.lines[line_index]
            if char_index > len(current_line):
                char_index = len(current_line)

            # Update final selection end point
            self.selection_end_x = char_index
            self.selection_end_y = line_index

            # Update cursor position
            self.cursor_x = char_index
            self.cursor_y = line_index

        # Create a selection if start and end positions are different
        if (self.selection_start_x != self.selection_end_x or
                self.selection_start_y != self.selection_end_y):
            self.selection_active = True
        else:
            # If it was just a click (no drag), clear any selection
            self.selection_active = False

        # Redraw to show the selection
        self.redraw()

    def selection_get_normalized(self):
        """Return selection coordinates with start before end."""
        if not self.selection_active:
            return (0, 0, 0, 0)

        if (self.selection_start_y < self.selection_end_y) or \
           (self.selection_start_y == self.selection_end_y and
                self.selection_start_x <= self.selection_end_x):
            return (self.selection_start_y, self.selection_start_x,
                    self.selection_end_y, self.selection_end_x)
        else:
            return (self.selection_end_y, self.selection_end_x,
                    self.selection_start_y, self.selection_start_x)

    def selection_get_text(self):
        """Get the currently selected text."""
        if not self.selection_active:
            return ""

        # Get normalized selection coordinates
        start_y, start_x, end_y, end_x = self.selection_get_normalized()

        # If selection is on a single line
        if start_y == end_y:
            return self.lines[start_y][start_x:end_x]

        # For multi-line selection
        selected_text = []

        # First line (from start_x to end of line)
        selected_text.append(self.lines[start_y][start_x:])

        # Middle lines (entire lines)
        for i in range(start_y + 1, end_y):
            selected_text.append(self.lines[i])

        # Last line (from start of line to end_x)
        selected_text.append(self.lines[end_y][:end_x])

        return "\n".join(selected_text)

    def selection_delete(self):
        """Delete the currently selected text."""
        if not self.selection_active:
            return

        # Get normalized selection coordinates
        start_y, start_x, end_y, end_x = self.selection_get_normalized()

        # If selection is on a single line
        if start_y == end_y:
            current_line = self.lines[start_y]
            self.lines[start_y] = current_line[:start_x] + current_line[end_x:]
            self.cursor_y = start_y
            self.cursor_x = start_x
            return

        # For multi-line selection

        # Create new first line (combining start and end parts)
        first_line = self.lines[start_y][:start_x] + self.lines[end_y][end_x:]

        # Replace the first line and remove the rest of the selected lines
        self.lines[start_y] = first_line
        del self.lines[start_y + 1:end_y + 1]

        # Set cursor to start of the deleted text
        self.cursor_y = start_y
        self.cursor_x = start_x

    def selection_copy(self):
        """Copy the selected text to the clipboard."""
        if not self.selection_active:
            return

        # Get the selected text
        selected_text = self.selection_get_text()
        if selected_text:
            self.clipboard = selected_text

    def selection_cut(self):
        """Cut selected text to clipboard."""
        if not self.selection_active:
            return

        self.selection_copy()
        self.selection_delete()
        self.selection_active = False
        self.modified = True
        self.redraw()

    def text_paste(self):
        """Paste text from clipboard at cursor position."""
        if not self.clipboard:
            return

        # If there is a selection, replace it
        if self.selection_active:
            self.selection_delete()
            self.selection_active = False

        # Handle multi-line paste
        if '\n' in self.clipboard:
            lines = self.clipboard.split('\n')

            # First line gets appended to current line
            current_line = self.lines[self.cursor_y]
            new_first_line = current_line[:self.cursor_x] + lines[0]
            remaining_current_line = current_line[self.cursor_x:]

            # Update current line
            self.lines[self.cursor_y] = new_first_line

            # Insert middle lines
            for i, line in enumerate(lines[1:-1], 1):
                self.lines.insert(self.cursor_y + i, line)

            # Last line gets prepended to remaining text
            if len(lines) > 1:
                last_line = lines[-1] + remaining_current_line
                self.lines.insert(self.cursor_y + len(lines) - 1, last_line)

                # Update cursor position
                self.cursor_y += len(lines) - 1
                self.cursor_x = len(lines[-1])
            else:
                # Handle single line with newline at the end
                self.lines.insert(self.cursor_y + 1, remaining_current_line)
                self.cursor_y += 1
                self.cursor_x = 0
        else:
            # Simple single-line paste
            self.text_insert(self.clipboard)

        self.modified = True
        self.cursor_ensure_visible()
        self.redraw()

    def handle_resize(self, width, height):
        """Update editor dimensions on window resize."""
        self.canvas_width = width
        self.canvas_height = height
        self.update_visible_area()
        self.cursor_ensure_visible()
        self.redraw()

    def file_new(self):
        """Create a new empty file."""
        self.lines = [""]
        self.cursor_x = 0
        self.cursor_y = 0
        self.scroll_y = 0
        self.file_path = None
        self.modified = False
        self.redraw()

    def file_open(self):
        """Open a file dialog and load a file."""
        # Since we don't have a proper file dialog in this environment,
        # we'll simulate by asking for a filename in the status bar
        self.draw_rect(0, 0, self.canvas_width,
                       self.status_height, self.status_bg_color)
        self.draw_text(self.padding, 3, self.status_text_color,
                       "Enter filename to open: ")

        try:
            file_path = input("Enter filename to open: ")
            with open(file_path, 'r') as f:
                self.lines = f.read().splitlines()
                # Add an empty line at the end if there isn't one
                if not self.lines or self.lines[-1] != "":
                    self.lines.append("")
                self.file_path = file_path
                self.cursor_x = 0
                self.cursor_y = 0
                self.scroll_y = 0
                self.modified = False
                print(f"Opened file: {file_path}")
        except Exception as e:
            print(f"Error opening file: {e}")

        self.redraw()

    def file_save(self):
        """Save the current file."""
        if not self.file_path:
            file_path = input("Enter filename to save: ")
            if not file_path:
                print("Save cancelled")
                self.redraw()
                return
            self.file_path = file_path

        try:
            with open(self.file_path, 'w') as f:
                f.write('\n'.join(self.lines))
            self.modified = False
            print(f"Saved file: {self.file_path}")
        except Exception as e:
            print(f"Error saving file: {e}")

        self.redraw()

    def listen_for_events(self):
        """Listen for events from the socket canvas."""
        buffer = ""

        while self.running:
            try:
                data = self.socket.recv(1024).decode()
                if not data:
                    break

                buffer += data

                while '\n' in buffer:
                    event, buffer = buffer.split('\n', 1)
                    self.handle_event(event)

            except Exception as e:
                print(f"Error receiving event: {e}")
                break

        print("Event listener stopped")

    def handle_event(self, event):
        """Process and route events from the socket canvas."""
        parts = event.split(',')
        if not parts:
            return

        event_type = parts[0]

        if event_type == 'resize':
            width, height = int(parts[1]), int(parts[2])
            self.handle_resize(width, height)

        elif event_type == 'keydown':
            key = parts[1]
            self.key_handle_down(key)

        elif event_type == 'keyup':
            key = parts[1]
            self.key_handle_up(key)

        elif event_type == 'mousedown':
            if len(parts) >= 3:
                x, y = int(parts[1]), int(parts[2])
                self.mouse_handle_click(x, y)

        elif event_type == 'mousemove':
            if len(parts) >= 3 and self.selection_active:
                x, y = int(parts[1]), int(parts[2])
                self.mouse_handle_drag(x, y)

        elif event_type == 'mouseup':
            if len(parts) >= 3:
                x, y = int(parts[1]), int(parts[2])
                self.mouse_handle_up(x, y)


def main():
    """Start the text editor application."""
    editor = TextEditor()

    if not editor.connect():
        return

    try:
        # Keep the script running
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
