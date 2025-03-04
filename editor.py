"""
Text Editor - Core Module

This module contains the main TextEditor class that manages the editor state
and coordinates interactions between other modules.
"""

import socket
import threading


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

        # Initialize function bindings with placeholder methods
        # These will be replaced after imports
        self._initialize_placeholders()

        # Bind actual functions after importing modules
        self._bind_module_functions()

    def _initialize_placeholders(self):
        """Initialize placeholder methods to avoid null reference errors."""
        # Cursor operations
        self.cursor_move_left = lambda: None
        self.cursor_move_right = lambda: None
        self.cursor_move_up = lambda: None
        self.cursor_move_down = lambda: None
        self.cursor_move_line_start = lambda: None
        self.cursor_move_line_end = lambda: None
        self.cursor_page_up = lambda: None
        self.cursor_page_down = lambda: None
        self.cursor_ensure_visible = lambda: None

        # Selection operations
        self.selection_get_normalized = lambda: (0, 0, 0, 0)
        self.selection_get_text = lambda: ""
        self.selection_delete = lambda: None
        self.selection_copy = lambda: None
        self.selection_cut = lambda: None
        self.text_paste = lambda: None

        # File operations
        self.file_new = lambda: None
        self.file_open = lambda: None
        self.file_save = lambda: None

        # UI operations
        self.redraw = lambda: None
        self.update_visible_area = lambda: None
        self.clear = lambda: None
        self.draw_rect = lambda x, y, w, h, c: None
        self.draw_text = lambda x, y, c, t: None

        # Input handling
        self.key_handle_down = lambda key: None
        self.key_handle_up = lambda key: None
        self.text_insert = lambda text: None
        self.backspace_delete_char = lambda: None
        self.delete_forward_char = lambda: None
        self.enter_new_line = lambda: None
        self.mouse_handle_click = lambda x, y: None
        self.mouse_handle_drag = lambda x, y: None
        self.mouse_handle_up = lambda x, y: None
        self.handle_resize = lambda w, h: None
        self.handle_event = lambda event: None

        # Key handlers dictionary
        self.key_handlers = {}

    def _bind_module_functions(self):
        """Import modules and bind their functions to this instance."""
        try:
            # Import modules here to avoid circular imports
            # These imports need to be inside this method
            from cursor import (
                cursor_move_left, cursor_move_right, cursor_move_up, cursor_move_down,
                cursor_move_line_start, cursor_move_line_end, cursor_page_up, cursor_page_down,
                cursor_ensure_visible
            )
            from selection import (
                selection_get_normalized, selection_get_text, selection_delete,
                selection_copy, selection_cut, text_paste
            )
            from file_operations import file_new, file_open, file_save
            from ui import redraw, update_visible_area, clear, draw_rect, draw_text
            from input_handlers import (
                key_handle_down, key_handle_up, text_insert, backspace_delete_char, delete_forward_char,
                enter_new_line, mouse_handle_click, mouse_handle_drag, mouse_handle_up,
                handle_resize, handle_event
            )

            # Special key mappings for common operations
            self.key_handlers = {
                'BackSpace': lambda: backspace_delete_char(self),
                'Delete': lambda: delete_forward_char(self),
                'Return': lambda: enter_new_line(self),
                'Tab': lambda: text_insert(self, "    "),
                'space': lambda: text_insert(self, " "),
                'Left': lambda: cursor_move_left(self),
                'Right': lambda: cursor_move_right(self),
                'Up': lambda: cursor_move_up(self),
                'Down': lambda: cursor_move_down(self),
                'Home': lambda: cursor_move_line_start(self),
                'End': lambda: cursor_move_line_end(self),
                'Prior': lambda: cursor_page_up(self),
                'Next': lambda: cursor_page_down(self),
                # Ignore modifier keys
                'Alt_L': lambda: None,
                'Alt_R': lambda: None,
                'Meta_L': lambda: None,
                'Meta_R': lambda: None,
                'Control_L': lambda: None,
                'Control_R': lambda: None
            }

            # Bind methods from other modules to this instance
            self.cursor_move_left = lambda: cursor_move_left(self)
            self.cursor_move_right = lambda: cursor_move_right(self)
            self.cursor_move_up = lambda: cursor_move_up(self)
            self.cursor_move_down = lambda: cursor_move_down(self)
            self.cursor_move_line_start = lambda: cursor_move_line_start(self)
            self.cursor_move_line_end = lambda: cursor_move_line_end(self)
            self.cursor_page_up = lambda: cursor_page_up(self)
            self.cursor_page_down = lambda: cursor_page_down(self)
            self.cursor_ensure_visible = lambda: cursor_ensure_visible(self)

            # Selection operations
            self.selection_get_normalized = lambda: selection_get_normalized(
                self)
            self.selection_get_text = lambda: selection_get_text(self)
            self.selection_delete = lambda: selection_delete(self)
            self.selection_copy = lambda: selection_copy(self)
            self.selection_cut = lambda: selection_cut(self)
            self.text_paste = lambda: text_paste(self)

            # File operations
            self.file_new = lambda: file_new(self)
            self.file_open = lambda: file_open(self)
            self.file_save = lambda: file_save(self)

            # UI operations
            self.redraw = lambda: redraw(self)
            self.update_visible_area = lambda: update_visible_area(self)
            self.clear = lambda: clear(self)
            self.draw_rect = lambda x, y, w, h, c: draw_rect(
                self, x, y, w, h, c)
            self.draw_text = lambda x, y, c, t: draw_text(self, x, y, c, t)

            # Input handling
            self.key_handle_down = lambda key: key_handle_down(self, key)
            self.key_handle_up = lambda key: key_handle_up(self, key)
            self.text_insert = lambda text: text_insert(self, text)
            self.backspace_delete_char = lambda: backspace_delete_char(self)
            self.delete_forward_char = lambda: delete_forward_char(self)
            self.enter_new_line = lambda: enter_new_line(self)
            self.mouse_handle_click = lambda x, y: mouse_handle_click(
                self, x, y)
            self.mouse_handle_drag = lambda x, y: mouse_handle_drag(self, x, y)
            self.mouse_handle_up = lambda x, y: mouse_handle_up(self, x, y)
            self.handle_resize = lambda w, h: handle_resize(self, w, h)
            self.handle_event = lambda event: handle_event(self, event)

            print("Successfully loaded and bound all modules")
        except ImportError as e:
            print(f"Error importing modules: {e}")
            print("Some editor functionality may be limited")

    def connect(self):
        """Connect to the socket canvas server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"Connected to socket canvas at {self.host}:{self.port}")

            self.running = True
            self.event_thread = threading.Thread(target=self.listen_for_events)
            self.event_thread.daemon = True
            self.event_thread.start()

            self.update_visible_area()
            self.redraw()

            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False

    def disconnect(self):
        """Disconnect from the socket canvas server."""
        if self.connected:
            self.running = False
            self.socket.close()
            self.connected = False
            print("Disconnected from socket canvas")

    def send_command(self, command):
        """Send a command to the socket canvas."""
        if not self.connected:
            print("Not connected to socket canvas")
            return

        try:
            if not command.endswith('\n'):
                command += '\n'
            self.socket.send(command.encode())
        except Exception as e:
            print(f"Failed to send command: {e}")

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
