"""
Text Editor - Input Handlers Module

This module handles keyboard and mouse input events.
"""


def key_handle_down(editor, key):
    """Process keydown events and take appropriate actions."""
    # Handle modifier keys
    if key in ["LeftShift", "RightShift"]:
        editor.shift_pressed = True
        return
    elif key in ["LeftControl", "RightControl", "Control_L", "Control_R",
                 "LeftCommand", "RightCommand", "Meta_L", "Meta_R"]:
        editor.control_pressed = True
        return
    elif key in ["LeftAlt", "RightAlt", "Alt_L", "Alt_R"]:
        return

    # Handle keyboard shortcuts with Control/Command
    if editor.control_pressed:
        if key == "s":
            editor.file_save()
            return
        elif key == "o":
            editor.file_open()
            return
        elif key == "n":
            editor.file_new()
            return
        elif key == "c":
            editor.selection_copy()
            return
        elif key == "x":
            editor.selection_cut()
            return
        elif key == "v":
            editor.text_paste()
            return

    # Handle special keys (arrows, etc.)
    if key in editor.key_handlers:
        editor.key_handlers[key]()
    # Handle non-standard characters
    elif key == "ø" or key == "??":
        text_insert(editor, "ø")
    elif key == "ß" or key == "??" or key == "ẞ":
        text_insert(editor, "ß")
    # Regular character input
    elif len(key) == 1:
        if editor.shift_pressed:
            key = key.upper()
        text_insert(editor, key)


def key_handle_up(editor, key):
    """Process keyup events to track modifier key states."""
    if key in ["LeftShift", "RightShift"]:
        editor.shift_pressed = False
    elif key in ["LeftControl", "RightControl", "Control_L", "Control_R",
                 "LeftCommand", "RightCommand", "Meta_L", "Meta_R"]:
        editor.control_pressed = False


def text_insert(editor, text):
    """Insert text at cursor, replacing any selection."""
    if editor.selection_active:
        editor.selection_delete()
        editor.selection_active = False

    current_line = editor.lines[editor.cursor_y]
    new_line = current_line[:editor.cursor_x] + \
        text + current_line[editor.cursor_x:]
    editor.lines[editor.cursor_y] = new_line
    editor.cursor_x += len(text)
    editor.modified = True
    editor.redraw()


def backspace_delete_char(editor):
    """Delete character before cursor or selected text."""
    if editor.selection_active:
        editor.selection_delete()
        editor.selection_active = False
        editor.modified = True
    elif editor.cursor_x > 0:
        current_line = editor.lines[editor.cursor_y]
        new_line = current_line[:editor.cursor_x-1] + \
            current_line[editor.cursor_x:]
        editor.lines[editor.cursor_y] = new_line
        editor.cursor_x -= 1
        editor.modified = True
    elif editor.cursor_y > 0:
        prev_line = editor.lines[editor.cursor_y - 1]
        current_line = editor.lines[editor.cursor_y]
        editor.cursor_x = len(prev_line)
        editor.lines[editor.cursor_y - 1] = prev_line + current_line
        editor.lines.pop(editor.cursor_y)
        editor.cursor_y -= 1
        editor.modified = True

    editor.cursor_ensure_visible()
    editor.redraw()


def delete_forward_char(editor):
    """Delete character after cursor or selected text."""
    if editor.selection_active:
        editor.selection_delete()
        editor.selection_active = False
        editor.modified = True
    else:
        current_line = editor.lines[editor.cursor_y]
        if editor.cursor_x < len(current_line):
            new_line = current_line[:editor.cursor_x] + \
                current_line[editor.cursor_x+1:]
            editor.lines[editor.cursor_y] = new_line
            editor.modified = True
        elif editor.cursor_y < len(editor.lines) - 1:
            next_line = editor.lines[editor.cursor_y + 1]
            editor.lines[editor.cursor_y] = current_line + next_line
            editor.lines.pop(editor.cursor_y + 1)
            editor.modified = True

    editor.redraw()


def enter_new_line(editor):
    """Create a new line at the cursor position."""
    current_line = editor.lines[editor.cursor_y]

    new_line = current_line[editor.cursor_x:]
    editor.lines[editor.cursor_y] = current_line[:editor.cursor_x]

    editor.lines.insert(editor.cursor_y + 1, new_line)

    editor.cursor_y += 1
    editor.cursor_x = 0
    editor.modified = True

    editor.cursor_ensure_visible()
    editor.redraw()


def mouse_handle_click(editor, x, y):
    """Handle mouse click by positioning cursor and starting selection."""
    if x < editor.text_area_start_x or y < editor.text_area_start_y:
        return

    # Calculate which line was clicked (accounting for scrolling)
    line_index = editor.scroll_y + \
        (y - editor.text_area_start_y) // editor.char_height

    if line_index >= len(editor.lines):
        line_index = len(editor.lines) - 1

    char_index = (x - editor.text_area_start_x) // editor.char_width

    current_line = editor.lines[line_index]
    if char_index > len(current_line):
        char_index = len(current_line)

    editor.cursor_y = line_index
    editor.cursor_x = char_index

    editor.selection_active = True
    editor.selection_start_x = char_index
    editor.selection_start_y = line_index
    editor.selection_end_x = char_index
    editor.selection_end_y = line_index

    editor.redraw()


def mouse_handle_drag(editor, x, y):
    """Extend selection during mouse drag."""
    if x < editor.text_area_start_x or y < editor.text_area_start_y:
        return

    line_index = editor.scroll_y + \
        (y - editor.text_area_start_y) // editor.char_height

    if line_index < editor.scroll_y:
        editor.scroll_y = max(0, editor.scroll_y - 1)
    elif line_index >= editor.scroll_y + editor.visible_rows:
        editor.scroll_y = min(
            len(editor.lines) - editor.visible_rows + 1, editor.scroll_y + 1)

    if line_index >= len(editor.lines):
        line_index = len(editor.lines) - 1

    char_index = (x - editor.text_area_start_x) // editor.char_width

    current_line = editor.lines[line_index]
    if char_index > len(current_line):
        char_index = len(current_line)

    editor.selection_end_x = char_index
    editor.selection_end_y = line_index

    editor.cursor_x = char_index
    editor.cursor_y = line_index

    editor.cursor_ensure_visible()

    editor.redraw()


def mouse_handle_up(editor, x, y):
    """Finalize selection on mouse up."""
    if x >= editor.text_area_start_x and y >= editor.text_area_start_y:
        line_index = editor.scroll_y + \
            (y - editor.text_area_start_y) // editor.char_height

        if line_index >= len(editor.lines):
            line_index = len(editor.lines) - 1

        char_index = (x - editor.text_area_start_x) // editor.char_width

        current_line = editor.lines[line_index]
        if char_index > len(current_line):
            char_index = len(current_line)

        editor.selection_end_x = char_index
        editor.selection_end_y = line_index

        editor.cursor_x = char_index
        editor.cursor_y = line_index

    if (editor.selection_start_x != editor.selection_end_x or
            editor.selection_start_y != editor.selection_end_y):
        editor.selection_active = True
    else:
        editor.selection_active = False

    editor.redraw()


def handle_resize(editor, width, height):
    """Update editor dimensions on window resize."""
    editor.canvas_width = width
    editor.canvas_height = height
    editor.update_visible_area()
    editor.cursor_ensure_visible()
    editor.redraw()


def handle_event(editor, event):
    """Process and route events from the socket canvas."""
    parts = event.split(',')
    if not parts:
        return

    event_type = parts[0]

    if event_type == 'resize':
        width, height = int(parts[1]), int(parts[2])
        handle_resize(editor, width, height)

    elif event_type == 'keydown':
        key = parts[1]
        key_handle_down(editor, key)

    elif event_type == 'keyup':
        key = parts[1]
        key_handle_up(editor, key)

    elif event_type == 'mousedown':
        if len(parts) >= 3:
            x, y = int(parts[1]), int(parts[2])
            mouse_handle_click(editor, x, y)

    elif event_type == 'mousemove':
        if len(parts) >= 3 and editor.selection_active:
            x, y = int(parts[1]), int(parts[2])
            mouse_handle_drag(editor, x, y)

    elif event_type == 'mouseup':
        if len(parts) >= 3:
            x, y = int(parts[1]), int(parts[2])
            mouse_handle_up(editor, x, y)
