from tkinter import *
from tkinter import ttk

class Frame(ttk.Style):

    def __init__(self):
        super().__init__()

        self.configure('TFrame', background='#404040')
        self.configure('design2.TFrame', background='#E9E8E8')
        self.configure('design3.TFrame', background='#D9D9D9')
        self.configure('design4.TFrame', background='#B9DBFA')
        self.configure('design5.TFrame', background='#F0F0F0')
        self.configure('design6.TFrame', background='#E1E1E1')
        self.configure('design7.TFrame', background='#323232')
        self.configure('design8.TFrame', bordercolor='#ADADAD')
        self.configure('design9.TFrame', background='#ADADAD')

class LabelFrame(ttk.Style):

    def __init__(self):
        super().__init__()

        self.configure('TLabelframe', background='white')


