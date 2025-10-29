from tkinter import ttk

class Progressbar(ttk.Style):

    def __init__(self):
        super().__init__()

        self.configure(
            'TProgressbar',
            background="lightblue",
            troughcolor="lightgray",
            lightcolor="lightblue",
        )