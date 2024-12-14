'''
tkcap

A wrapper for tkinter window for taking its screenshot.
By ghanteyyy https://github.com/ghanteyyy
MIT License

Usage:
    import tkcap

    cap = tkcap.CAP(master)  # 'master' is a tkinter window instance, passed to create a capture object
    cap.capture(FileName)    # Captures a screenshot of the tkinter window and saves it as provided FileName

    # To retrieve the x, y coordinates, width, and height of the tkinter window
    region = cap.get_region()

    # Bind a key (in this case, 'Control + g') to trigger a screenshot capture when pressed
    # Each time 'Control + g' is pressed, the screenshot will be saved as provided FileName
    master.bind('<Control-g>', lambda: cap.capture(FileName))
'''

__all__ = ['CAP']
__version__ = '0.0.4'
__author__ = 'ghanteyyy'

import os
import sys
import subprocess
import collections
import tkinter as tk
import tkinter.tix as tix
from screeninfo import get_monitors
from . import exceptions

if sys.version_info.major < 3:
    raise exceptions.TkCapException('tkcap supports Python 3+ only')

try:
    import pyautogui

except ModuleNotFoundError:
    raise exceptions.TkCapException('tkcap is unable to import pyautogui. Please install pyautogui to use tkcap')


box = collections.namedtuple('box', 'left upper right lower')


class CAP:
    def __init__(self, master):
        if isinstance(master, (tk.Tk, tk.Toplevel, tix.Tk, tix.Toplevel)):
            self.master = master
            self.VALID_EXTENSION = ['tif', 'tiff', 'jpg', 'png', 'jpeg', 'jpe', 'jfif', 'bmp', 'dib', 'gif']

        else:
            raise exceptions.TkCapException('master parameter was expected to be the instance of tkinter')

    def get_box(self):
        '''Get left, upper, right and lower pixel coordinate'''

        self.master.update()

        minimum_x = 0
        minimum_y = 0
        for m in get_monitors():
            minimum_x = min(minimum_x, m.x)
            minimum_y = min(minimum_y, m.y)
        left = self.master.winfo_x() - minimum_x + 8
        right = self.master.winfo_x() + self.master.winfo_width() - minimum_x
        upper = self.master.winfo_y() - minimum_y
        lower = self.master.winfo_y() + self.master.winfo_height() - minimum_y + 29

        return box(left, upper, right, lower)

    def capture(self, imageFilename, overwrite=False, show=False):
        '''Capture and save screenshot of the tkinter window
           Set 'overwrite' parameter to True, to overwrite the file having same name
           Set 'show' parameter to True, to open the image file in file explorer'''

        path = os.path.abspath(os.path.join('.', imageFilename))
        head, tail = os.path.split(path)
        extension = tail.split('.')[-1]

        if not os.path.exists(head):
            raise exceptions.PathNotFoundError(f'The system cannot find path: {head}')

        elif extension not in self.VALID_EXTENSION:
            raise exceptions.ExtensionError(f'unknown file extension: {extension}')

        elif os.path.exists(path) and overwrite is False:
            raise exceptions.ImageNameExistsError(f'Cannot store image having same name: {tail}')

        if overwrite and os.path.exists(path):
            os.remove(path)

        screenshot = pyautogui.screenshot(allScreens=True).crop(self.get_box()) #region=self.get_region())
        screenshot.save(path)

        if show:
            self.master.after(1100, lambda: subprocess.run([os.path.join(os.getenv('WINDIR'), 'explorer.exe'), '/select,', os.path.normpath(path)]))
