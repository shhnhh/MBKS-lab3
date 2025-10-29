from tkinter import ttk

from utils.load import load
from _style._toolbutton.images import images

class Toolbutton(ttk.Style):

    def __init__(self):
        super().__init__()

        load(images['default'], (30, 30), name='toolbutton_default')
        load(images['active'], (30, 30), name='toolbutton_active')
        load(images['selected'], (30, 30), name='toolbutton_selected')
        load(images['disabled'], (30, 30), name='toolbutton_disabled')
        load(images['pressed'], (30, 30), name='toolbutton_pressed')

        self.configure('design1.Toolbutton', background='#404040')
        self.configure('design2.Toolbutton', background='#E9E8E8')

        self.map('Toolbutton', background=[])

        self.element_create('Toolbutton.background', 'image', 'toolbutton_default',
                            ('pressed', 'toolbutton_pressed'),
                            ('selected', 'toolbutton_selected'),
                            ('active', 'toolbutton_active'),
                            ('disabled', 'toolbutton_disabled'))

        self.layout('Toolbutton', 
            [('Toolbutton.background', {'sticky': 'nswe', 'children': 
                [('Toolbutton.label', {'sticky': 'nswe'})]
            })]
        )