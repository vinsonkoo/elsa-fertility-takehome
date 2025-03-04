"""
Text Editor - Selection Module

This module handles text selection operations and clipboard functions.
"""


def selection_get_normalized(editor):
    """Return selection coordinates with start before end."""
    if not editor.selection_active:
        return (0, 0, 0, 0)

    if (editor.selection_start_y < editor.selection_end_y) or \
        (editor.selection_start_y == editor.selection_end_y and
            editor.selection_start_x <= editor.selection_end_x):
        return (editor.selection_start_y, editor.selection_start_x,
                editor.selection_end_y, editor.selection_end_x)
    else:
        return (editor.selection_end_y, editor.selection_end_x,
                editor.selection_start_y, editor.selection_start_x)


def selection_get_text(editor):
    """Get the currently selected text."""
    if not editor.selection_active:
        return ""

    start_y, start_x, end_y, end_x = selection_get_normalized(editor)

    if start_y == end_y:
        return editor.lines[start_y][start_x:end_x]

    selected_text = []

    selected_text.append(editor.lines[start_y][start_x:])

    for i in range(start_y + 1, end_y):
        selected_text.append(editor.lines[i])

    selected_text.append(editor.lines[end_y][:end_x])

    return "\n".join(selected_text)


def selection_delete(editor):
    """Delete the currently selected text."""
    if not editor.selection_active:
        return

    start_y, start_x, end_y, end_x = selection_get_normalized(editor)

    if start_y == end_y:
        current_line = editor.lines[start_y]
        editor.lines[start_y] = current_line[:start_x] + current_line[end_x:]
        editor.cursor_y = start_y
        editor.cursor_x = start_x
        return

    first_line = editor.lines[start_y][:start_x] + editor.lines[end_y][end_x:]

    editor.lines[start_y] = first_line
    del editor.lines[start_y + 1:end_y + 1]

    editor.cursor_y = start_y
    editor.cursor_x = start_x


def selection_copy(editor):
    """Copy the selected text to the clipboard."""
    if not editor.selection_active:
        return

    selected_text = selection_get_text(editor)
    if selected_text:
        editor.clipboard = selected_text


def selection_cut(editor):
    """Cut selected text to clipboard."""
    if not editor.selection_active:
        return

    selection_copy(editor)
    selection_delete(editor)
    editor.selection_active = False
    editor.modified = True
    editor.redraw()


def text_paste(editor):
    """Paste text from clipboard at cursor position."""
    if not editor.clipboard:
        return

    if editor.selection_active:
        selection_delete(editor)
        editor.selection_active = False

    if '\n' in editor.clipboard:
        lines = editor.clipboard.split('\n')

        current_line = editor.lines[editor.cursor_y]
        new_first_line = current_line[:editor.cursor_x] + lines[0]
        remaining_current_line = current_line[editor.cursor_x:]

        editor.lines[editor.cursor_y] = new_first_line

        for i, line in enumerate(lines[1:-1], 1):
            editor.lines.insert(editor.cursor_y + i, line)

        if len(lines) > 1:
            last_line = lines[-1] + remaining_current_line
            editor.lines.insert(editor.cursor_y + len(lines) - 1, last_line)

            editor.cursor_y += len(lines) - 1
            editor.cursor_x = len(lines[-1])
        else:
            editor.lines.insert(editor.cursor_y + 1, remaining_current_line)
            editor.cursor_y += 1
            editor.cursor_x = 0
    else:
        editor.text_insert(editor.clipboard)

    editor.modified = True
    editor.cursor_ensure_visible()
    editor.redraw()
