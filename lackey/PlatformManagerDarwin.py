""" Platform-specific code for Darwin is encapsulated in this module. """

import os
import re
import time
import numpy
import AppKit
import tempfile
import subprocess
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk
    
from PIL import Image, ImageTk, ImageOps

from .Settings import Debug
from .InputEmulation import Keyboard

# Python 3 compatibility
try:
    basestring
except NameError:
    basestring = str

class PlatformManagerDarwin(object):
    """ Abstracts Darwin-specific OS-level features """
    def __init__(self):

        # Mapping to `keyboard` names
        self._SPECIAL_KEYCODES = {
            "BACKSPACE": 	"backspace",
            "TAB": 			"tab",
            "CLEAR": 		"clear",
            "ENTER": 		"enter",
            "SHIFT": 		"shift",
            "CTRL": 		"ctrl",
            "ALT": 			"alt",
            "PAUSE": 		"pause",
            "CAPS_LOCK": 	"caps lock",
            "ESC": 			"esc",
            "SPACE":		"spacebar",
            "PAGE_UP":      "page up",
            "PAGE_DOWN":    "page down",
            "END":			"end",
            "HOME":			"home",
            "LEFT":			"left arrow",
            "UP":			"up arrow",
            "RIGHT":		"right arrow",
            "DOWN":			"down arrow",
            "SELECT":		"select",
            "PRINT":		"print",
            "PRINTSCREEN":	"print screen",
            "INSERT":		"ins",
            "DELETE":		"del",
            "WIN":			"win",
            "CMD":			"win",
            "META":			"win",
            "NUM0":		    "keypad 0",
            "NUM1":		    "keypad 1",
            "NUM2":		    "keypad 2",
            "NUM3":		    "keypad 3",
            "NUM4":		    "keypad 4",
            "NUM5":		    "keypad 5",
            "NUM6":		    "keypad 6",
            "NUM7":		    "keypad 7",
            "NUM8":		    "keypad 8",
            "NUM9":		    "keypad 9",
            "NUM9":		    "keypad 9",
            "SEPARATOR":    83,
            "ADD":	        78,
            "MINUS":        74,
            "MULTIPLY":     55,
            "DIVIDE":       53,
            "F1":			"f1",
            "F2":			"f2",
            "F3":			"f3",
            "F4":			"f4",
            "F5":			"f5",
            "F6":			"f6",
            "F7":			"f7",
            "F8":			"f8",
            "F9":			"f9",
            "F10":			"f10",
            "F11":			"f11",
            "F12":			"f12",
            "F13":			"f13",
            "F14":			"f14",
            "F15":			"f15",
            "F16":			"f16",
            "NUM_LOCK":		"num lock",
            "SCROLL_LOCK":	"scroll lock",
        }
        self._REGULAR_KEYCODES = {
            "0":			"0",
            "1":			"1",
            "2":			"2",
            "3":			"3",
            "4":			"4",
            "5":			"5",
            "6":			"6",
            "7":			"7",
            "8":			"8",
            "9":			"9",
            "a":			"a",
            "b":			"b",
            "c":			"c",
            "d":			"d",
            "e":			"e",
            "f":			"f",
            "g":			"g",
            "h":			"h",
            "i":			"i",
            "j":			"j",
            "k":			"k",
            "l":			"l",
            "m":			"m",
            "n":			"n",
            "o":			"o",
            "p":			"p",
            "q":			"q",
            "r":			"r",
            "s":			"s",
            "t":			"t",
            "u":			"u",
            "v":			"v",
            "w":			"w",
            "x":			"x",
            "y":			"y",
            "z":			"z",
            ";":			";",
            "=":			"=",
            ",":			",",
            "-":			"-",
            ".":			".",
            "/":			"/",
            "`":			"`",
            "[":			"[",
            "\\":			"\\",
            "]":			"]",
            "'":			"'",
            " ":			" ",
        }
        self._UPPERCASE_KEYCODES = {
            "~":			"`",
            "+":			"=",
            ")":			"0",
            "!":			"1",
            "@":			"2",
            "#":			"3",
            "$":			"4",
            "%":			"5",
            "^":			"6",
            "&":			"7",
            "*":			"8",
            "(":			"9",
            "A":			"a",
            "B":			"b",
            "C":			"c",
            "D":			"d",
            "E":			"e",
            "F":			"f",
            "G":			"g",
            "H":			"h",
            "I":			"i",
            "J":			"j",
            "K":			"k",
            "L":			"l",
            "M":			"m",
            "N":			"n",
            "O":			"o",
            "P":			"p",
            "Q":			"q",
            "R":			"r",
            "S":			"s",
            "T":			"t",
            "U":			"u",
            "V":			"v",
            "W":			"w",
            "X":			"x",
            "Y":			"y",
            "Z":			"z",
            ":":			";",
            "<":			",",
            "_":			"-",
            ">":			".",
            "?":			"/",
            "|":			"\\",
            "\"":			"'",
            "{":            "[",
            "}":            "]",
        }

    ## Screen functions

    def getBitmapFromRect(self, x, y, w, h):
        """ Capture the specified area of the (virtual) screen. """
        min_x, min_y, screen_width, screen_height = self._getVirtualScreenRect()
        img = self._getVirtualScreenBitmap() # TODO
        # Limit the coordinates to the virtual screen
        # Then offset so 0,0 is the top left corner of the image
        # (Top left of virtual screen could be negative)
        x1 = min(max(min_x, x), min_x+screen_width) - min_x
        y1 = min(max(min_y, y), min_y+screen_height) - min_y
        x2 = min(max(min_x, x+w), min_x+screen_width) - min_x
        y2 = min(max(min_y, y+h), min_y+screen_height) - min_y
        return numpy.array(img.crop((x1, y1, x2, y2)))
    def getScreenBounds(self, screenId):
        """ Returns the screen size of the specified monitor (0 being the main monitor). """
        screen_details = self.getScreenDetails()
        if not isinstance(screenId, int) or screenId < -1 or screenId >= len(screen_details):
            raise ValueError("Invalid screen ID")
        if screenId == -1:
            # -1 represents the entire virtual screen
            return self._getVirtualScreenRect()
        return screen_details[screenId]["rect"]
    def _getVirtualScreenRect(self):
        """ Returns the rect of all attached screens as (x, y, w, h) """
        monitors = self.getScreenDetails()
        x1 = min([s["rect"][0] for s in monitors])
        y1 = min([s["rect"][1] for s in monitors])
        x2 = max([s["rect"][0]+s["rect"][3] for s in monitors])
        y2 = max([s["rect"][1]+s["rect"][4] for s in monitors])
        return (x1, y1, x2-x1, y2-y1)
    def _getVirtualScreenBitmap(self):
        """ Returns a bitmap of all attached screens """
        filenames = []
        screen_details = self.getScreenDetails()
        for screen in screen_details:
            fh, filepath = tempfile.mkstemp('.png')
            filenames.append(filepath)
            os.close(fh)
        subprocess.call(['screencapture', '-x'] + filenames)

        min_x, min_y, screen_w, screen_h = self._getVirtualScreenRect()
        virtual_screen = Image.new("RGB", (screen_w, screen_h))
        for filename, screen in zip(filenames, screen_details):
            im = Image.open(filename)
            im.load()
            # Capture virtscreen coordinates of monitor
            x, y, w, h = screen["rect"]
            # Convert to image-local coordinates
            x = x - min_x
            y = y - min_y
            # Paste on the virtual screen
            virtual_screen.paste(im, (x, y))
            os.unlink(filename)

    def getScreenDetails(self):
        """ Return list of attached monitors

        For each monitor (as dict), ``monitor["rect"]`` represents the screen as positioned
        in virtual screen. List is returned in device order, with the first element (0)
        representing the primary monitor.
        """
        primary_screen = None
        screens = []
        for monitor in AppKit.NSScreen.screens():
            # Convert screen rect to Lackey-style rect (x,y,w,h) as position in virtual screen
            screen = {
                "rect": (
                    monitor.frame().origin.x,
                    monitor.frame().origin.y,
                    monitor.frame().size.width,
                    monitor.frame().size.height
                )
            }
            screens.append(screen)
        return screens
    def isPointVisible(self, x, y):
        """ Checks if a point is visible on any monitor. """
        for screen in self.getScreenDetails():
            s_x, s_y, s_w, s_h = screen["rect"]
            if (s_x <= x < (s_x + s_w)) and (s_y <= y < (s_y + s_h)):
                return True
        return False

    ## Clipboard functions

    def osCopy(self):
        """ Triggers the OS "copy" keyboard shortcut """
        k = Keyboard()
        k.keyDown("{CTRL}")
        k.type("c")
        k.keyUp("{CTRL}")
    def osPaste(self):
        """ Triggers the OS "paste" keyboard shortcut """
        k = Keyboard()
        k.keyDown("{CTRL}")
        k.type("v")
        k.keyUp("{CTRL}")

    ## Window functions

    def getWindowByTitle(self, wildcard, order=0):
        """ Returns a handle for the first window that matches the provided "wildcard" regex """
        # TODO
        pass
    def getWindowByPID(self, pid, order=0):
        """ Returns a handle for the first window that matches the provided PID """
        # TODO
        pass
    def getWindowRect(self, hwnd):
        """ Returns a rect (x,y,w,h) for the specified window's area """
        # TODO
        pass
    def focusWindow(self, hwnd):
        """ Brings specified window to the front """
        Debug.log(3, "Focusing window: " + str(hwnd))
        # TODO
        pass
    def getWindowTitle(self, hwnd):
        """ Gets the title for the specified window """
        # TODO
        pass
    def getWindowPID(self, hwnd):
        """ Gets the process ID that the specified window belongs to """
        # TODO
        pass
    def getForegroundWindow(self):
        """ Returns a handle to the window in the foreground """
        # TODO
        pass

    ## Highlighting functions

    def highlight(self, rect, seconds=1):
        """ Simulates a transparent rectangle over the specified ``rect`` on the screen.

        Actually takes a screenshot of the region and displays with a
        rectangle border in a borderless window (due to Tkinter limitations)

        If a Tkinter root window has already been created somewhere else,
        uses that instead of creating a new one.
        """
        if tk._default_root is None:
            Debug.log(3, "Creating new temporary Tkinter root")
            temporary_root = True
            root = tk.Tk()
            root.withdraw()
        else:
            Debug.log(3, "Borrowing existing Tkinter root")
            temporary_root = False
            root = tk._default_root
        image_to_show = self.getBitmapFromRect(*rect)
        app = highlightWindow(root, rect, image_to_show)
        timeout = time.time()+seconds
        while time.time() < timeout:
            app.update_idletasks()
            app.update()
        app.destroy()
        if temporary_root:
            root.destroy()

    ## Process functions
    def isPIDValid(self, pid):
        """ Checks if a PID is associated with a running process """
        # TODO
        pass
    def killProcess(self, pid):
        """ Kills the process with the specified PID (if possible) """
        # TODO
        pass
    def getProcessName(self, pid):
        # TODO
        pass

## Helper class for highlighting

class highlightWindow(tk.Toplevel):
    def __init__(self, root, rect, screen_cap):
        """ Accepts rect as (x,y,w,h) """
        self.root = root
        tk.Toplevel.__init__(self, self.root, bg="red", bd=0)

        ## Set toplevel geometry, remove borders, and push to the front
        self.geometry("{2}x{3}+{0}+{1}".format(*rect))
        self.overrideredirect(1)
        self.attributes("-topmost", True)

        ## Create canvas and fill it with the provided image. Then draw rectangle outline
        self.canvas = tk.Canvas(
            self,
            width=rect[2],
            height=rect[3],
            bd=0,
            bg="blue",
            highlightthickness=0)
        self.tk_image = ImageTk.PhotoImage(Image.fromarray(screen_cap[..., [2, 1, 0]]))
        self.canvas.create_image(0, 0, image=self.tk_image, anchor=tk.NW)
        self.canvas.create_rectangle(
            2,
            2,
            rect[2]-2,
            rect[3]-2,
            outline="red",
            width=4)
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)

        ## Lift to front if necessary and refresh.
        self.lift()
        self.update()