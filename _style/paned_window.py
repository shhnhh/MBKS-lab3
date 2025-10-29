from tkinter import ttk

class PanedWindow(ttk.Style):

    def __init__(self):
        super().__init__()

        self.configure(
            'Sash', 
            gripcount=0,
            sashthickness=2,
        )