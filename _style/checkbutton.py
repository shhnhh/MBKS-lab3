from tkinter import ttk

from _style._checkbutton.images import images
from utils.load import load

class Checkbutton(ttk.Style):

    def __init__(self):
        super().__init__()

        load(images['checkbutton-indicator-selected'], (20, 20), name='checkbutton_indicator_selected')
        load(images['checkbutton-indicator-deselected'], (20, 20), name='checkbutton_indicator_deselected')
        load(images['checkbutton-indicator-disabled'], (20, 20), name='checkbutton_indicator_disabled')

        self.configure(
            'design1.TCheckbutton',
            background='#363636',
            foreground='white',
        )

        self.configure(
            'design2.TCheckbutton',
            background='white',
            foreground='black',
        )

        self.map("TCheckbutton",
            background=[],
            indicatorcolor=[('selected', '#0078D7'), ('!selected', '#0078D7')],
		)

        self.element_create(
			'MyCheckbutton.indicator', 'image', 'checkbutton_indicator_deselected',
			('selected', 'checkbutton_indicator_selected'),
			('active', 'pressed', 'checkbutton_indicator_deselected'),
			('disabled', 'checkbutton_indicator_disabled'),
		)

        self.layout('TCheckbutton', 
            [('Checkbutton.padding',
                {'children': 
                    [('MyCheckbutton.indicator', {'side': 'left', 'sticky': ''}),
                        ('Checkbutton.label', {'sticky': 'nswe'})],
                'sticky': 'nswe'})])
