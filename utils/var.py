class CallbackVar:

    def __init__(self, init_value=None):
        self._value = init_value
        self.callback = lambda: None

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, new_value):
        self._value = new_value
        self.callback()

    