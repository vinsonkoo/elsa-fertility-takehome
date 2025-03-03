Text Editor
-----------
A simple, Tkinter-based implementation of a canvas that receives commands
and sends events over a plain TCP socket. All commands and events are
comma-delimited and should be terminated with a newline character.

Prerequisites
-------------
Python 3

Goal
----
Create a text editor using the provided socket canvas API.

You will be evaluated on the creativity of your product choices and ability to build a complete and robust product...so go wild! This project is meant to be a pick your own adventure, so make it your own. 

As some inspiration, past submissions have included:

- An implementation of vim
- A fully functional Markdown editor with viewing mode
- A GoogleDocs-esque editor with collaborative editing capabilities


Deliverables
------------
At the end of the 24 hour period, please:

1. Email back a zip of your code that includes a short README on how to run it
2. Send over a short video of you walking through your text editor (we recommend using Loom or any native screen recording tools).


What's Allowed/Not Allowed
--------------------------
Allowed:

- You can code in any language you'd like to implement the text editor, as long as it can establish a TCP connection ;)
- You can modify the socket_canvas.py file to add support for additional features to your text editor
- You can use any resources (e.g. Google, StackOverflow, etc.) and tools (e.g. Cursor, Claude, ChatGPT, etc.) at your disposal

Not Allowed:

- You may not deviate from the core Tkinter-based socket canvas API (i.e. you cannot switch out Tkinter for another GUI/WYSIWIG/Markdown library)

Running the Socket Canvas API
-----------------------------
You can start the socket canvas API by running:

`python socket_canvas.py`

This will spin up the canvas API and expose it over a TCP socket on port 5005.

Establishing a connection with the TCP socket will create a new canvas window that will listen to API commands and emit API events to and from the connection. Closing the connection will also close the canvas window.

Socket Canvas API Commands
--------------------------
The socket canvas API only has 3 commands:

1. You can draw a square of a specific width, height, and color at a given x, y coordinate
2. You can draw a string of a specific color at a given x, y coordinate
3. You can clear the screen by sending the string "clear"

Each commands should be terminated with a newline character. 
The below are examples of how to construct each command:

Drawing a red square at 0,0 with side length of 100 (rect,x,y,width,height,color):
rect,0,0,100,100,#ff0000

Drawing "Hello, world!" in black at 0,0 (text,x,y,color,string):
text,0,0,#000000,Hello world!

Clearing the screen by sending the string:
clear

NOTE: Characters are rendered using a monospace font, measuring 8x14 per character

Socket Canvas API Events
------------------------
In addition to the commands above that can be sent to the canvas API, the canvas API will also emit events that can be listened to by your socket connection. Examples of these events are described below:

Window resize (resize,width,height):
resize,1024,768

Mouse events (mouseevent,x,y):
mousedown,100,100
mouseup,100,100
mousemove,100,100

Keyboard events (keyevent,key_char_or_code):
keydown,a
keyup,a


For some keys, a special string will be sent in the "key_char_or_code" field of the keyboard event:

Return
Tab
space
Up
Down
Left
Right
BackSpace
Escape
LeftShift
LeftControl
LeftAlt
LeftCommand
RightCommand
RightAlt
RightControl
RightShift

