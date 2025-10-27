import tkinter as tk

class EditableLabel(tk.Frame):
    def __init__(self, parent, text="", max_length=10, **kwargs):
        super().__init__(parent)
        self.text = text
        self.max_length = max_length
        
        # Создаем Label с обрезанным текстом
        self.label = tk.Label(self, text=self._trim_text(text), cursor="hand2", **kwargs)
        self.label.pack(fill='x')
        self.label.bind("<Double-Button-1>", self.start_edit)
    
    def _trim_text(self, text):
        """Обрезает текст и добавляет многоточие если нужно"""
        if len(text) > self.max_length:
            return text[:self.max_length-3] + "..."
        return text
    
    def start_edit(self, event=None):
        """Начинает редактирование"""
        # Скрываем Label
        self.label.pack_forget()
        
        # Создаем Entry с полным текстом
        self.entry = tk.Entry(self, width=10)
        self.entry.insert(0, self.text)
        self.entry.pack(fill='x')
        self.entry.focus()
        self.entry.select_range(0, tk.END)
        
        # Привязываем события
        self.entry.bind("<Return>", self.save_text)
        self.entry.bind("<Escape>", self.cancel_edit)
        self.entry.bind("<FocusOut>", self.save_text)  # Сохраняем при потере фокуса
    
    def save_text(self, event=None):
        """Сохраняет текст"""
        new_text = self.entry.get()
        self.text = new_text
        self.entry.destroy()
        
        # Показываем Label с обрезанным текстом
        self.label.config(text=self._trim_text(new_text))
        self.label.pack(fill='x')
    
    def cancel_edit(self, event=None):
        """Отменяет редактирование"""
        self.entry.destroy()
        self.label.pack(fill='x')
    
    def get(self):
        """Возвращает полный текст"""
        return self.text
    
    def set(self, new_text):
        """Устанавливает новый текст"""
        self.text = new_text
        self.label.config(text=self._trim_text(new_text))
    
    def set_max_length(self, max_length):
        """Устанавливает максимальную длину для обрезки"""
        self.max_length = max_length
        self.label.config(text=self._trim_text(self.text))