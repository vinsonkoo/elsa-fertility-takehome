"""
Text Editor - Cursor Module

This module handles cursor movement and positioning operations.
"""


def cursor_move_left(editor):
    """Move the cursor one position to the left."""
    if editor.cursor_x > 0:
        editor.cursor_x -= 1
    elif editor.cursor_y > 0:
        editor.cursor_y -= 1
        editor.cursor_x = len(editor.lines[editor.cursor_y])

    cursor_ensure_visible(editor)
    editor.redraw()


def cursor_move_right(editor):
    """Move the cursor one position to the right."""
    current_line = editor.lines[editor.cursor_y]

    if editor.cursor_x < len(current_line):
        editor.cursor_x += 1
    elif editor.cursor_y < len(editor.lines) - 1:
        editor.cursor_y += 1
        editor.cursor_x = 0

    cursor_ensure_visible(editor)
    editor.redraw()


def cursor_move_up(editor):
    """Move the cursor one position up."""
    if editor.cursor_y > 0:
        editor.cursor_y -= 1
        editor.cursor_x = min(editor.cursor_x, len(
            editor.lines[editor.cursor_y]))

    cursor_ensure_visible(editor)
    editor.redraw()


def cursor_move_down(editor):
    """Move the cursor one position down."""
    if editor.cursor_y < len(editor.lines) - 1:
        editor.cursor_y += 1
        editor.cursor_x = min(editor.cursor_x, len(
            editor.lines[editor.cursor_y]))

    cursor_ensure_visible(editor)
    editor.redraw()


def cursor_move_line_start(editor):
    """Moves the cursor to the start of the current line."""
    editor.cursor_x = 0
    editor.redraw()


def cursor_move_line_end(editor):
    """Moves the cursor to the end of the current line."""
    editor.cursor_x = len(editor.lines[editor.cursor_y])
    editor.redraw()


def cursor_page_up(editor):
    """Move the cursor up by a page."""
    editor.cursor_y = max(0, editor.cursor_y - editor.visible_rows)
    editor.cursor_x = min(editor.cursor_x, len(editor.lines[editor.cursor_y]))
    cursor_ensure_visible(editor)
    editor.redraw()


def cursor_page_down(editor):
    """Move the cursor down by a page."""
    editor.cursor_y = min(len(editor.lines) - 1,
                          editor.cursor_y + editor.visible_rows)
    editor.cursor_x = min(editor.cursor_x, len(editor.lines[editor.cursor_y]))
    cursor_ensure_visible(editor)
    editor.redraw()


def cursor_ensure_visible(editor):
    """Scroll view if needed to ensure cursor is visible."""
    if editor.cursor_y < editor.scroll_y:
        editor.scroll_y = editor.cursor_y

    elif editor.cursor_y >= editor.scroll_y + editor.visible_rows:
        editor.scroll_y = editor.cursor_y - editor.visible_rows + 1
