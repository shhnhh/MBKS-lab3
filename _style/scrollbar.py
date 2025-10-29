from tkinter import ttk

from _style._scrollbar.images import images
from utils.load import load

class Scrollbar(ttk.Style):

    def __init__(self):
        super().__init__()

        load(images['scrollbar-arrow-left'], (15, 15), name='img_left')
        load(images['scrollbar-arrow-left-active'], (15, 15), name='img_left_active')
        load(images['scrollbar-arrow-left-pressed'], (15, 15), name='img_left_pressed')
        load(images['scrollbar-arrow-right'], (15, 15), name='img_right')
        load(images['scrollbar-arrow-right-active'], (15, 15), name='img_right_active')
        load(images['scrollbar-arrow-right-pressed'], (15, 15), name='img_right_pressed')
        load(images['scrollbar-arrow-up'], (15, 15), name='img_up')
        load(images['scrollbar-arrow-up-active'], (15, 15), name='img_up_active')
        load(images['scrollbar-arrow-up-pressed'], (15, 15), name='img_up_pressed')
        load(images['scrollbar-arrow-down'], (15, 15), name='img_down')
        load(images['scrollbar-arrow-down-active'], (15, 15), name='img_down_active')
        load(images['scrollbar-arrow-down-pressed'], (15, 15), name='img_down_pressed')

        self.configure(
                'TScrollbar',
                width=15,
                gripcount=0,
                background='#ADADAD',
                troughcolor='#E1E1E1',
                bordercolor='#E1E1E1'
        )

        self.element_create('Scrollbar.leftarrow', 'image', 'img_left',
                            ('pressed', '!disabled', 'img_left_pressed'),
                            ('active', '!disabled', 'img_left_active'))
        self.element_create('Scrollbar.rightarrow', 'image', 'img_right',
                            ('pressed', '!disabled', 'img_right_pressed'),
                            ('active', '!disabled', 'img_right_active'))
        self.element_create('Scrollbar.uparrow', 'image', 'img_up',
                            ('pressed', '!disabled', 'img_up_pressed'),
                            ('active', '!disabled', 'img_up_active'))
        self.element_create('Scrollbar.downarrow', 'image', 'img_down',
                            ('pressed', '!disabled', 'img_down_pressed'),
                            ('active', '!disabled', 'img_down_active'))

        self.layout('Horizontal.TScrollbar',
            [('Horizontal.Scrollbar.trough', {'children':
                [('Horizontal.Scrollbar.leftarrow', {'side': 'left', 'sticky': ''}),
                ('Horizontal.Scrollbar.rightarrow', {'side': 'right', 'sticky': ''}),
                ('Horizontal.Scrollbar.thumb', {'unit': '1', 'children':
                    [('Horizontal.Scrollbar.grip', {'sticky': ''})],
                    'sticky': 'nswe'})],
                'sticky': 'we'})])

        self.layout('Vertical.TScrollbar',
            [('Vertical.Scrollbar.trough', {'children':
                [('Vertical.Scrollbar.uparrow', {'side': 'top', 'sticky': ''}),
                ('Vertical.Scrollbar.downarrow', {'side': 'bottom', 'sticky': ''}),
                ('Vertical.Scrollbar.thumb', {'unit': '1', 'children':
                    [('Vertical.Scrollbar.grip', {'sticky': ''})],
                    'sticky': 'nswe'})],
                'sticky': 'ns'})])