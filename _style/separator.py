from tkinter import ttk

class Separator(ttk.Style):

    def __init__(self):
        super().__init__()

        self.configure('TSeparator', background='#E9E8E8')