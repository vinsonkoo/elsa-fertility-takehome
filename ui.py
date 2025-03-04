"""
Text Editor - UI Module

This module handles all UI rendering operations, including drawing
text content, line numbers, cursor, and other UI elements.
"""

import os


def clear(editor):
    """Clear the canvas."""
    editor.send_command("clear")


def draw_rect(editor, x, y, width, height, color):
    """Draw a rectangle on the canvas."""
    editor.send_command(f"rect,{x},{y},{width},{height},{color}")


def draw_text(editor, x, y, color, text):
    """Draw text on the canvas."""
    editor.send_command(f"text,{x},{y},{color},{text}")


def update_visible_area(editor):
    """Update the visible area dimensions."""
    editor.visible_cols = (
        editor.canvas_width - editor.text_area_start_x - editor.padding) // editor.char_width
    editor.visible_rows = (
        editor.canvas_height - editor.text_area_start_y - editor.padding) // editor.char_height


def redraw(editor):
    """Redraw the entire editor interface."""
    clear(editor)

    draw_rect(editor, 0, 0, editor.canvas_width,
              editor.canvas_height, editor.bg_color)

    draw_rect(editor, 0, 0, editor.canvas_width,
              editor.status_height, editor.status_bg_color)

    file_name = os.path.basename(
        editor.file_path) if editor.file_path else "Untitled"
    modified_indicator = "*" if editor.modified else ""
    status_text = f"{file_name}{modified_indicator} | Line: {editor.cursor_y + 1}/{len(editor.lines)} | Col: {editor.cursor_x + 1}"
    draw_text(editor, editor.padding, 3, editor.status_text_color, status_text)

    draw_rect(editor, 0, editor.status_height, editor.line_number_width,
              editor.canvas_height - editor.status_height, editor.line_number_bg_color)

    draw_line_numbers(editor)
    draw_text_content(editor)

    cursor_screen_x = editor.text_area_start_x + editor.cursor_x * editor.char_width
    cursor_screen_y = editor.text_area_start_y + \
        (editor.cursor_y - editor.scroll_y) * editor.char_height
    draw_rect(editor, cursor_screen_x, cursor_screen_y, 2,
              editor.char_height, editor.cursor_color)


def draw_line_numbers(editor):
    """Draw line numbers for visible lines."""
    visible_end = min(editor.scroll_y + editor.visible_rows, len(editor.lines))

    for i in range(editor.scroll_y, visible_end):
        line_number = str(i + 1).rjust(4)
        line_y = editor.text_area_start_y + \
            (i - editor.scroll_y) * editor.char_height
        draw_text(editor, editor.padding, line_y,
                  editor.line_number_text_color, line_number)


def draw_text_content(editor):
    """Draw the visible text content with selection highlighting."""
    visible_end = min(editor.scroll_y + editor.visible_rows, len(editor.lines))
    sel_start_y, sel_start_x, sel_end_y, sel_end_x = editor.selection_get_normalized()

    for i in range(editor.scroll_y, visible_end):
        line = editor.lines[i]
        line_y = editor.text_area_start_y + \
            (i - editor.scroll_y) * editor.char_height

        # If selection is active and this line is within selection
        if editor.selection_active and sel_start_y <= i <= sel_end_y:
            if sel_start_y == sel_end_y:  # Selection on a single line
                # Draw part before selection
                if sel_start_x > 0:
                    draw_text(editor, editor.text_area_start_x, line_y,
                              editor.text_color, line[:sel_start_x])

                # Draw selection background
                sel_width = (sel_end_x - sel_start_x) * editor.char_width
                if sel_width > 0:
                    draw_rect(
                        editor,
                        editor.text_area_start_x + sel_start_x * editor.char_width,
                        line_y,
                        sel_width,
                        editor.char_height,
                        editor.selection_bg_color
                    )

                # Draw selected text
                draw_text(
                    editor,
                    editor.text_area_start_x + sel_start_x * editor.char_width,
                    line_y,
                    editor.text_color,
                    line[sel_start_x:sel_end_x]
                )

                # Draw part after selection
                if sel_end_x < len(line):
                    draw_text(
                        editor,
                        editor.text_area_start_x + sel_end_x * editor.char_width,
                        line_y,
                        editor.text_color,
                        line[sel_end_x:]
                    )

            elif i == sel_start_y:  # First line of multi-line selection
                # Draw part before selection
                if sel_start_x > 0:
                    draw_text(editor, editor.text_area_start_x, line_y,
                              editor.text_color, line[:sel_start_x])

                # Draw selection background
                sel_width = (len(line) - sel_start_x) * editor.char_width
                if sel_width > 0:
                    draw_rect(
                        editor,
                        editor.text_area_start_x + sel_start_x * editor.char_width,
                        line_y,
                        sel_width,
                        editor.char_height,
                        editor.selection_bg_color
                    )

                # Draw selected text
                draw_text(
                    editor,
                    editor.text_area_start_x + sel_start_x * editor.char_width,
                    line_y,
                    editor.text_color,
                    line[sel_start_x:]
                )

            elif i == sel_end_y:  # Last line of multi-line selection
                # Draw selection background
                if sel_end_x > 0:
                    draw_rect(
                        editor,
                        editor.text_area_start_x,
                        line_y,
                        sel_end_x * editor.char_width,
                        editor.char_height,
                        editor.selection_bg_color
                    )

                # Draw selected text
                draw_text(
                    editor,
                    editor.text_area_start_x,
                    line_y,
                    editor.text_color,
                    line[:sel_end_x]
                )

                # Draw part after selection
                if sel_end_x < len(line):
                    draw_text(
                        editor,
                        editor.text_area_start_x + sel_end_x * editor.char_width,
                        line_y,
                        editor.text_color,
                        line[sel_end_x:]
                    )

            else:  # Middle lines of multi-line selection
                # Draw entire line with selection background
                draw_rect(
                    editor,
                    editor.text_area_start_x,
                    line_y,
                    len(line) * editor.char_width,
                    editor.char_height,
                    editor.selection_bg_color
                )

                # Draw selected text
                draw_text(
                    editor,
                    editor.text_area_start_x,
                    line_y,
                    editor.text_color,
                    line
                )
        else:
            # No selection on this line, draw it normally
            draw_text(editor, editor.text_area_start_x,
                      line_y, editor.text_color, line)
