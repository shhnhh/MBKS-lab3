from tkinter import ttk

class Button(ttk.Style):

    def __init__(self):
        super().__init__()

        self.configure(
            'TButton',
            background='#E1E1E1',
            borderwidth=3,
            relief='solid',
            bordercolor='#ADADAD',
            padding=2
        )

        self.map('TButton', bordercolor=[('disabled', '#E1E1E1')],
                            foreground=[("disabled", "#E1E1E1")],
                            background=[("disabled", "#F0F0F0")])

        self.layout('TButton', 
            [('Button.border', {'border': '1', 'children': 
                    [('Button.padding', {'children': 
                        [('Button.label', {'sticky': 'nswe'})],
                    'sticky': 'nswe'})],
            'sticky': 'nswe'})])