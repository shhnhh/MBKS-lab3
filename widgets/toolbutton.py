from tkinter import *
from tkinter import ttk

from utils.load import load
from _style._toolbutton.images import images

class ToolButton(ttk.Button):

    ICON_SIZE = (18, 18)

    def __init__(self, master, alias, **kwargs):
        super().__init__(
            master, 
            image=load(
                images[alias],
                self.ICON_SIZE
            ),
            **kwargs
        )

class ToolRadiobutton(ttk.Radiobutton):

    ICON_SIZE = (18, 18)

    def __init__(self, master, alias, **kwargs):
        super().__init__(
            master, 
            image=load(
                images[alias],
                self.ICON_SIZE    
            ),
            **kwargs
        )