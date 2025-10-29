from tkinter import *
from tkinter import ttk
from CTkMessagebox import CTkMessagebox
import customtkinter as ctk
from widgets.toolbutton import ToolButton
from widgets.custom_scrollbar import CustomScrollbar
from string import ascii_letters

STEP = 30

def validate_object_token(tok):
    return len(tok) == 1 and tok.isalpha() and tok in ascii_letters

class Matrix(ttk.Frame):

    def __init__(self, parent, data={}):
        super().__init__(parent)

        self.data = data
        self.check_vars = {}
        self.max_length = 15
        self._selected = set()

        self.btns = ttk.Frame(self, padding=5)
        self.canvas = Canvas(self, background='#2b2b2b', highlightthickness=0)
        self.yscrollbar = CustomScrollbar(self, orient=VERTICAL, command=self.canvas.yview)
        self.xscrollbar = CustomScrollbar(self, orient=HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.yscrollbar.set, xscrollcommand=self.xscrollbar.set)

        self.btn_add_row = ToolButton(
            self.btns,
            alias='btn-add-row',
            style='design1.Toolbutton',
            command=self.add_subject
        )

        separator_1 = ttk.Separator(self.btns, orient=VERTICAL)

        self.btn_add_col = ToolButton(
            self.btns,
            alias='btn-add-col',
            style='design1.Toolbutton',
            command=self.add_object
        )

        separator_2 = ttk.Separator(self.btns, orient=VERTICAL)

        self.btn_delete = ToolButton(
            self.btns,
            alias='btn-delete',
            style='design1.Toolbutton',
            command=self.delete_selected
        )

        separator_3 = ttk.Separator(self.btns, orient=VERTICAL)

        self.btn_save = ToolButton(
            self.btns,
            alias='btn-save',
            style='design1.Toolbutton',
            command=self.apply_matrix_changes
        )

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.btns.grid(row=0, column=0, columnspan=2, sticky=EW)
        self.canvas.grid(row=1, column=0, sticky=NSEW)
        self.yscrollbar.grid(row=1, column=1, sticky=NS)
        self.xscrollbar.grid(row=2, column=0, sticky=EW)

        self.btn_add_row.pack(side=LEFT)
        separator_1.pack(side=LEFT, fill=Y, pady=5, padx=5)
        self.btn_add_col.pack(side=LEFT)
        separator_2.pack(side=LEFT, fill=Y, pady=5, padx=5)
        self.btn_delete.pack(side=LEFT)
        separator_3.pack(side=LEFT, fill=Y, pady=5, padx=5)
        self.btn_save.pack(side=LEFT)

        self.bind('<Configure>', lambda event: self.redraw())
        self.canvas.bind('<Button-1>', lambda event: self.focus_set())

    def redraw(self):
        self.check_vars = {}

        self.update_idletasks()
        self.canvas.delete(ALL)

        objs = [o for o in self.data["objects"]]
        subs = [s for s in self.data["subjects"].keys()]

        self.canvas.create_rectangle(
            0, 0, 130, STEP,
            fill='#363636', 
            outline='#ADADAD',
            width=1
        )

        self.canvas.create_text(
            5, STEP // 2,
            text='Субъект\\Объект',
            fill='white',
            font=('Arial', 12),
            anchor=W
        )

        for i, obj in enumerate(objs):
            self.canvas.create_rectangle(
                130 + STEP * i, 0,
                130 + STEP * (i + 1), STEP,
                fill='#363636', 
                outline='#ADADAD',
                width=1,
                tags=(f'col_{i}', f'bg_col_{i}')
            )
            self.canvas.create_text(
                130 + STEP * i + STEP // 2, STEP // 2,
                text=obj,
                fill='white',
                font=('Arial', 12),
                anchor=CENTER,
                tags=(f'col_{i}', f'text_col_{i}')
            )
            self.canvas.tag_bind(f'col_{i}', '<Enter>', lambda event, idx=i: self.enter(f'col_{idx}'))
            self.canvas.tag_bind(f'col_{i}', '<Leave>', lambda event, idx=i: self.leave(f'col_{idx}'))
            self.canvas.tag_bind(f'col_{i}', '<Double-Button-1>', lambda event, idx=i: self.edit_text(f'col_{idx}'))
            self.canvas.tag_bind(f'col_{i}', '<Button-1>', lambda event, idx=i: self.select(f'col_{idx}'))
            self.canvas.tag_bind(f'col_{i}', '<Control-Button-1>', lambda event, idx=i: self.multiselect(f'col_{idx}'))

        for i, subj in enumerate(subs):
            self.canvas.create_rectangle(
                0, STEP * (i + 1),
                130, STEP * (i + 2),
                fill='#363636', 
                outline='#ADADAD',
                width=1,
                tags=(f'row_{i}', f'bg_row_{i}')
            )
            self.canvas.create_text(
                65, STEP * (i + 1) + STEP // 2,
                text=self._trim_text(subj),
                fill='white',
                font=('Arial', 12),
                anchor=CENTER,
                tags=(f'row_{i}', f'text_row_{i}')
            )
            self.canvas.tag_bind(f'row_{i}', '<Enter>', lambda event, idx=i: self.enter(f'row_{idx}'))
            self.canvas.tag_bind(f'row_{i}', '<Leave>', lambda event, idx=i: self.leave(f'row_{idx}'))
            self.canvas.tag_bind(f'row_{i}', '<Double-Button-1>', lambda event, idx=i: self.edit_text(f'row_{idx}'))
            self.canvas.tag_bind(f'row_{i}', '<Button-1>', lambda event, idx=i: self.select(f'row_{idx}'))
            self.canvas.tag_bind(f'row_{i}', '<Control-Button-1>', lambda event, idx=i: self.multiselect(f'row_{idx}'))
            for j, obj in enumerate(objs):
                var = IntVar(value=1 if obj in self.data["subjects"].get(subj, []) else 0)
                cb = ttk.Checkbutton(self.canvas, variable=var, style='design1.TCheckbutton')
                self.canvas.create_rectangle(
                    130, STEP * (i + 1),
                    130 + STEP * (j + 1), STEP * (i + 2),
                    fill='#363636', 
                    outline='#ADADAD',
                    width=1
                )
                self.canvas.create_window(
                    130 + STEP // 2 + STEP * j, 
                    STEP * (i + 1) + STEP // 2,
                    window=cb,
                    anchor=CENTER
                )
                self.check_vars[(subj, obj)] = var
        
        self.canvas.config(scrollregion=self.canvas.bbox(ALL))

    def edit_text(self, tag):
        objs = [o for o in self.data["objects"]]
        subs = [s for s in self.data["subjects"].keys()]
        s, idx = tag.split('_')
        bbox = self.canvas.bbox(tag)
        text = objs[int(idx)] if s == 'col' else subs[int(idx)]
        entry = ttk.Entry(self.canvas)
        entry.insert(0, text)
        entry.focus_set()
        self.canvas.create_window(
            bbox[0], bbox[1],
            width=bbox[2] - bbox[0],
            height=bbox[3] - bbox[1],
            anchor=NW,
            window=entry,
            tags=(f'widget_{tag}',)
        )

        def select_all(event):
            widget = event.widget
            widget.select_range(0, END)
            widget.icursor(END)

        def save(event):
            if entry.winfo_ismapped():
                match s:
                    case 'row':
                        self.rename_subject(text, entry.get())
                    case 'col': 
                        new_name = entry.get()
                        if not validate_object_token(new_name):
                            CTkMessagebox(
                                title="Ошибка", 
                                message="Объект должен быть одной латинской буквой.",
                                icon="warning"
                            )
                        else:
                            self.rename_object(text, new_name)
                self.canvas.delete(f'widget_{tag}')
                self.event_generate('<<TextChanged>>')

        def cancel(event):
            if entry.winfo_ismapped():
                self.canvas.delete(f'widget_{tag}')
                self.event_generate('<<TextChanged>>')

        entry.bind('<Return>', save)
        entry.bind('<FocusOut>', save)
        entry.bind("<Escape>", cancel)
        entry.bind('<Control-KeyRelease-a>', select_all)

    def rename_subject(self, old_name, new_name):
        if new_name and new_name != old_name:
            if new_name in self.data["subjects"]:
                CTkMessagebox(
                    title="Ошибка", 
                    message=f"Субъект '{new_name}' уже существует!",
                    icon="cancel"
                )
                return False
            
            self.data["subjects"][new_name] = self.data["subjects"].pop(old_name)
            self.redraw()
            return True
        return False

    def rename_object(self, old_name, new_name):
        if new_name and new_name != old_name:
            if new_name in self.data["objects"]:
                CTkMessagebox(
                    title="Ошибка", 
                    message=f"Объект '{new_name}' уже существует!",
                    icon="cancel"
                )
                return False
            
            index = self.data["objects"].index(old_name)
            self.data["objects"][index] = new_name
            
            for subject in self.data["subjects"]:
                if old_name in self.data["subjects"][subject]:
                    idx = self.data["subjects"][subject].index(old_name)
                    self.data["subjects"][subject][idx] = new_name
            
            self.redraw()
            return True
        return False
    
    def _trim_text(self, text):
        if len(text) > self.max_length:
            return text[:self.max_length-3] + "..."
        return text
    
    def enter(self, tag):
        if tag in self._selected:
            return
        self.canvas.itemconfig(f'bg_{tag}', fill="#2d4a6e")

    def leave(self, tag):
        if tag in self._selected:
            return
        self.canvas.itemconfig(f'bg_{tag}', fill='#363636')

    def select(self, tag):
        self.unselect()
        self._selected = {tag}
        self.canvas.itemconfig(f'bg_{tag}', fill="#1e5ba6")

    def multiselect(self, tag):
        if tag in self._selected:
            self._selected.remove(tag)
            self.canvas.itemconfig(f'bg_{tag}', fill='#363636')
        else:
            self._selected.add(tag)
            self.canvas.itemconfig(f'bg_{tag}', fill="#1e5ba6")

    def unselect(self):
        for tag in self._selected:
            self.canvas.itemconfig(f'bg_{tag}', fill='#363636')
        self._selected.clear()

    def add_col(self, label):
        self.data['objects'].append('')
        self.redraw()

    def add_subject(self):
        dialog = ctk.CTkInputDialog(text="Введите имя субъекта:", title="Новый субъект")
        subject = dialog.get_input()
        
        if subject and subject.strip():
            subject = subject.strip()
            if subject in self.data["subjects"]:
                CTkMessagebox(
                    title="Ошибка", 
                    message=f"Субъект '{subject}' уже существует!",
                    icon="cancel"
                )
            else:
                self.data["subjects"][subject] = []
                self.redraw()

    def add_object(self):
        dialog = ctk.CTkInputDialog(text="Введите объект (одна латинская буква):", title="Новый объект")
        obj = dialog.get_input()
        
        if obj and validate_object_token(obj):
            if obj in self.data["objects"]:
                CTkMessagebox(
                    title="Ошибка", 
                    message=f"Объект '{obj}' уже существует!",
                    icon="cancel"
                )
            else:
                self.data["objects"].append(obj)
                self.redraw()
        elif obj:
            CTkMessagebox(
                title="Ошибка", 
                message="Объект должен быть одной латинской буквой!",
                icon="warning"
            )

    def delete_selected(self):
        if not self._selected:
            CTkMessagebox(
                title="Внимание", 
                message="Не выбрано ни одного элемента для удаления.",
                icon="warning"
            )
            return
            
        msg = CTkMessagebox(
            title="Подтверждение удаления",
            message="Вы действительно хотите удалить выбранные элементы?",
            icon="question",
            option_1="Отмена",
            option_2="Удалить"
        )
        
        if msg.get() == "Удалить":
            rows_to_delete = []
            cols_to_delete = []
            
            for tag in self._selected:
                if tag.startswith('row_'):
                    rows_to_delete.append(tag)
                elif tag.startswith('col_'):
                    cols_to_delete.append(tag)
            
            rows_to_delete.sort(key=lambda x: int(x.split('_')[1]), reverse=True)
            cols_to_delete.sort(key=lambda x: int(x.split('_')[1]), reverse=True)
            
            subjects = list(self.data["subjects"].keys())
            objects = self.data["objects"]
            subjects_to_delete = []
            
            for row_tag in rows_to_delete:
                _, idx = row_tag.split('_')
                idx = int(idx)
                if idx < len(subjects):
                    subject_to_delete = subjects[idx]
                    if subject_to_delete in self.data["subjects"]:
                        del self.data["subjects"][subject_to_delete]
            for col_tag in cols_to_delete:
                _, idx = col_tag.split('_')
                idx = int(idx)
                if idx < len(objects):
                    object_to_delete = objects[idx]
                    if object_to_delete in self.data["objects"]:
                        self.data["objects"].remove(object_to_delete)
                    for subject in self.data["subjects"]:
                        if object_to_delete in self.data["subjects"][subject]:
                            self.data["subjects"][subject].remove(object_to_delete)

            self._selected.clear()
            self.redraw()

    def apply_matrix_changes(self):
        for (s, o), var in self.check_vars.items():
            if s in self.data["subjects"]:
                allowed = set(self.data["subjects"][s])
                if var.get():
                    allowed.add(o)
                else:
                    allowed.discard(o)
                self.data["subjects"][s] = list(allowed)
        self.event_generate('<<MatrixChanged>>')
        
        CTkMessagebox(
            title="Сохранено", 
            message="Изменения в матрице доступа успешно применены.",
            icon="check"
        )