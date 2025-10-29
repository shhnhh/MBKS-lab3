from tkinter import ttk

from _style.scrollbar import Scrollbar
from _style.toolbutton import Toolbutton
from _style.separator import Separator
from _style.frame import Frame, LabelFrame
from _style.button import Button
from _style.label import Label
from _style.paned_window import PanedWindow
from _style.combobox import Combobox
from _style.progressbar import Progressbar
from _style.checkbutton import Checkbutton


class Style(ttk.Style):

    def __init__(self):
        super().__init__()

        self.theme_use('clam')

        Scrollbar()
        Toolbutton()
        Separator()
        Frame()
        LabelFrame()
        Button()
        Label()
        PanedWindow()
        Combobox()
        Progressbar()
        Checkbutton()
