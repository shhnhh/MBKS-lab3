from tkinter import *
from tkinter import ttk

class Label(ttk.Style):

    def __init__(self):
        super().__init__()

        self.configure('TLabel', background='white')

        self.configure(
            'design1.TLabel', 
            background='white',
            borderwidth=1,
            relief=SOLID,
            bordercolor='#21699D'
        )