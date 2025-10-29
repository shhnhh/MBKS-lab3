from tkinter import *
from tkinter import ttk

class CustomScrollbar(ttk.Scrollbar):

    def set(self, *args):
        super().set(*args)

        if DISABLED in self.state():
            if hasattr(self, 'pack_kwargs'):
                self.pack_forget()
            elif hasattr(self, 'grid_kwargs'):
                self.grid_forget()
            elif hasattr(self, 'place_kwargs'):
                self.place_forget()
        else:
            if hasattr(self, 'pack_kwargs'):
                self.pack(**self.pack_kwargs)
            elif hasattr(self, 'grid_kwargs'):
                self.grid(**self.grid_kwargs)
            elif hasattr(self, 'place_kwargs'):
                self.place(**self.place_kwargs)

    def pack(self, **kwargs):
        super().pack(**kwargs)
        self.pack_kwargs = kwargs

    def grid(self, **kwargs):
        super().grid(**kwargs)
        self.grid_kwargs = kwargs

    def place(self, **kwargs):
        super().place(**kwargs)
        self.place_kwargs = kwargs