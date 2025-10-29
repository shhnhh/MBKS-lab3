from tkinter import *
from tkinter import ttk

class Combobox(ttk.Style):

    def __init__(self):
        super().__init__()

        self.configure(
            'Combobox.TButton',
            background='white',
            relief=FLAT,
            focuscolor='white',
            highlightthickness=0
        )

        self.map('Combobox.TButton', background=[('active', '#F0F0F0'),
                                                 ('!active', 'white')])
        
        self.configure(
            'Combobox.TEntry', 
            borderwidth=0,
            relief=FLAT,
            highlightthickness=0,
            focuscolor='white',
            background='red',
            bordercolor='white'
        )

        self.map('Combobox.TEntry', bordercolor=[('focus', 'white')])
