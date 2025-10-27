#!/usr/bin/env python3
# admin.py — приложение администратора для управления матрицей доступа
import json
import os
import time
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from widgets.custom_label import EditableLabel
from string import ascii_letters

DATA_FILE = "access_matrix.json"
LOG_FILE = "admin_log.txt"
MAX_SUBJECT_LEN = 256


def write_audit(*args):
    """Записывает строку в audit-лог."""
    try:
        t = time.strftime("[%Y-%m-%d %H:%M:%S]")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(t + " " + " ".join(str(a) for a in args) + "\n")
    except Exception:
        pass  # не критично, если не удалось записать


def load_matrix(path=DATA_FILE):
    if not os.path.exists(path):
        return {"objects": [], "subjects": {}}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("objects", [])
        data.setdefault("subjects", {})
        for s, objs in list(data["subjects"].items()):
            data["subjects"][s] = list(dict.fromkeys(objs))
        data["objects"] = list(dict.fromkeys(data["objects"]))
        return data
    except Exception as e:
        messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить {path}:\n{e}")
        return {"objects": [], "subjects": {}}


def save_matrix(data, path=DATA_FILE):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить {path}:\n{e}")


def validate_object_token(tok):
    return len(tok) == 1 and tok.isalpha() and tok in ascii_letters


def parse_subjects(text):
    return [s.strip() for s in text.replace(",", " ").split() if s.strip()]


def parse_objects(text):
    items = [s.strip() for s in text if s.strip()]
    for it in items:
        if not validate_object_token(it):
            raise ValueError(f"Неверный объект '{it}'. Объект — одна латинская буква (регистр важен).")
    return items


# --- Команды ---
def create(data, subject, objects_list):
    if not subject:
        raise ValueError("Пустое имя субъекта.")
    if len(subject) > MAX_SUBJECT_LEN:
        raise ValueError(f"Длина имени субъекта превышает {MAX_SUBJECT_LEN} символов.")
    if subject in data["subjects"]:
        grant(data, [subject], objects_list)
        return "existing"
    for o in objects_list:
        if o not in data["objects"]:
            data["objects"].append(o)
    data["subjects"][subject] = list(dict.fromkeys(objects_list))
    return "created"


def grant(data, subjects_list, objects_list):
    if not subjects_list:
        raise ValueError("Не указаны субъекты.")
    for s in subjects_list:
        if s not in data["subjects"]:
            raise ValueError(f"Субъект '{s}' не существует.")
    for o in objects_list:
        if o not in data["objects"]:
            data["objects"].append(o)
    for s in subjects_list:
        cur = set(data["subjects"].get(s, []))
        cur.update(objects_list)
        data["subjects"][s] = list(cur)


def remove(data, subjects_list, objects_list):
    if not subjects_list:
        raise ValueError("Не указаны субъекты.")
    for s in subjects_list:
        if s not in data["subjects"]:
            raise ValueError(f"Субъект '{s}' не существует.")
    for s in subjects_list:
        cur = set(data["subjects"].get(s, []))
        for o in objects_list:
            cur.discard(o)
        data["subjects"][s] = list(cur)


def grant_all(data, subjects_list):
    if not subjects_list:
        raise ValueError("Не указаны субъекты.")
    all_objs = list(data["objects"])
    for s in subjects_list:
        if s not in data["subjects"]:
            raise ValueError(f"Субъект '{s}' не существует.")
        data["subjects"][s] = list(dict.fromkeys(all_objs))


def remove_all(data, subjects_list):
    if not subjects_list:
        raise ValueError("Не указаны субъекты.")
    for s in subjects_list:
        if s not in data["subjects"]:
            raise ValueError(f"Субъект '{s}' не существует.")
        data["subjects"][s] = []


# --- GUI ---
class AdminApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Администратор — управление матрицей доступа")
        self.geometry("1100x650")
        self.minsize(900, 500)
        self.data_file = DATA_FILE
        self.data = load_matrix(self.data_file)

        ttk.Style().theme_use("clam")

        # Filters
        self.filter_subject = tk.StringVar()
        self.filter_object = tk.StringVar()

        self.build_layout()
        self.check_vars = {}
        self.build_matrix_ui()

    # --- GUI construction ---
    def build_layout(self):
        top_filter = ttk.Frame(self)
        top_filter.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(top_filter, text="Фильтр субъектов:").pack(side=tk.LEFT)
        subj_entry = ttk.Entry(top_filter, textvariable=self.filter_subject, width=20)
        subj_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(top_filter, text="Фильтр объектов:").pack(side=tk.LEFT)
        obj_entry = ttk.Entry(top_filter, textvariable=self.filter_object, width=10)
        obj_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(top_filter, text="Применить фильтр", command=self.build_matrix_ui).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_filter, text="Сбросить фильтр", command=self.reset_filters).pack(side=tk.LEFT, padx=5)

        # Split frames
        self.left_frame = ttk.Frame(self)
        self.right_frame = ttk.Frame(self)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        # Scrollable matrix
        self.matrix_canvas = tk.Canvas(self.left_frame)
        self.matrix_scroll_y = ttk.Scrollbar(self.left_frame, orient=tk.VERTICAL, command=self.matrix_canvas.yview)
        self.matrix_scroll_x = ttk.Scrollbar(self.left_frame, orient=tk.HORIZONTAL, command=self.matrix_canvas.xview)
        self.matrix_canvas.configure(yscrollcommand=self.matrix_scroll_y.set, xscrollcommand=self.matrix_scroll_x.set)
        self.matrix_canvas.grid(row=0, column=0, sticky=tk.NSEW)
        self.matrix_scroll_y.grid(row=0, column=1, sticky=tk.NS)
        self.matrix_scroll_x.grid(row=1, column=0, sticky=tk.EW)
        
        ttk.Button(
            self.left_frame, text="Применить изменения", command=self.apply_matrix_changes
        ).grid(row=2, column=0)

        self.matrix_frame = ttk.Frame(self.matrix_canvas)
        self.matrix_canvas.create_window((0, 0), window=self.matrix_frame, anchor="nw")
        self.matrix_frame.bind(
            "<Configure>", lambda e: self.matrix_canvas.configure(scrollregion=self.matrix_canvas.bbox("all"))
        )

        self.build_controls()

    def reset_filters(self):
        self.filter_subject.set("")
        self.filter_object.set("")
        self.build_matrix_ui()

    def build_controls(self):
        self.controls_canvas = tk.Canvas(self.right_frame)
        self.controls_scroll_y = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.controls_canvas.yview)
        self.controls_canvas.configure(yscrollcommand=self.controls_scroll_y.set)
        self.controls_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.controls_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.update_idletasks()

        rf = ttk.Frame(self.controls_canvas)
        self.controls_canvas.create_window((0, 0), window=rf, anchor=tk.NW, width=self.controls_canvas.winfo_width() - 10)

        rf.bind("<Configure>", lambda e: self.controls_canvas.configure(scrollregion=self.controls_canvas.bbox("all")))
        
        ttk.Label(rf, text="Управление субъектами/объектами", font=("Arial", 12, "bold")).pack(pady=5)

        sub_frame = ttk.Labelframe(rf, text="Добавить субъект")
        sub_frame.pack(fill=tk.X, pady=5)
        ttk.Label(sub_frame, text="Имя субъекта:").pack(anchor="w")
        self.add_subject_entry = ttk.Entry(sub_frame)
        self.add_subject_entry.pack(fill=tk.X, pady=3)
        ttk.Button(sub_frame, text="Добавить (без прав)", command=self.on_add_subject).pack(fill=tk.X)

        obj_frame = ttk.Labelframe(rf, text="Добавить объект")
        obj_frame.pack(fill=tk.X, pady=5)
        ttk.Label(obj_frame, text="Объект (одна буква):").pack(anchor="w")
        self.add_object_entry = ttk.Entry(obj_frame)
        self.add_object_entry.pack(fill=tk.X, pady=3)
        ttk.Button(obj_frame, text="Добавить объект", command=self.on_add_object).pack(fill=tk.X)
        ttk.Button(obj_frame, text="Удалить объект", command=self.on_delete_object).pack(fill=tk.X, pady=2)

        cmd_frame = ttk.Labelframe(rf, text="Команды")
        cmd_frame.pack(fill=tk.X, pady=5)
        ttk.Label(cmd_frame, text="Субъекты:").pack(anchor="w")
        self.cmd_subjects = ttk.Entry(cmd_frame)
        self.cmd_subjects.pack(fill=tk.X, pady=2)
        ttk.Label(cmd_frame, text="Объекты:").pack(anchor="w")
        self.cmd_objects = ttk.Entry(cmd_frame)
        self.cmd_objects.pack(fill=tk.X, pady=2)
        ttk.Button(cmd_frame, text="grant", command=self.on_grant).pack(fill=tk.X)
        ttk.Button(cmd_frame, text="create", command=self.on_create).pack(fill=tk.X)
        ttk.Button(cmd_frame, text="remove", command=self.on_remove).pack(fill=tk.X)
        ttk.Button(cmd_frame, text="grant_all", command=self.on_grant_all).pack(fill=tk.X)
        ttk.Button(cmd_frame, text="remove_all", command=self.on_remove_all).pack(fill=tk.X)

        file_frame = ttk.Labelframe(rf, text="Файл")
        file_frame.pack(fill=tk.X, pady=5)
        ttk.Button(file_frame, text="Сохранить", command=self.on_save).pack(fill=tk.X, pady=2)
        ttk.Button(file_frame, text="Загрузить из файла...", command=self.on_load_from).pack(fill=tk.X, pady=2)
        ttk.Button(file_frame, text="Экспорт...", command=self.on_export).pack(fill=tk.X, pady=2)

        info_frame = ttk.Labelframe(rf, text="Информация")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.info_text = tk.Text(info_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.info_text.pack(fill=tk.BOTH, expand=True)

    # --- Matrix UI ---
    def build_matrix_ui(self):
        for c in self.matrix_frame.winfo_children():
            c.destroy()
        self.check_vars = {}

        objs = [o for o in self.data["objects"] if self.filter_object.get() in o]
        subs = [s for s in self.data["subjects"].keys() if self.filter_subject.get() in s]

        ttk.Label(self.matrix_frame, text="Субъект\\Объект", borderwidth=1, relief="ridge").grid(row=0, column=0)
        for j, obj in enumerate(objs, 1):
            ttk.Label(self.matrix_frame, text=obj, borderwidth=1, relief="ridge", anchor="center").grid(
                row=0, column=j, sticky="nsew"
            )

        for i, subj in enumerate(subs, 1):
            left = ttk.Frame(self.matrix_frame)
            left.grid(row=i, column=0, sticky="nsew", padx=1, pady=1)
            btn = ttk.Button(left, text='🗙', width=2, command=lambda s=subj: self.delete_subject(s))
            btn.pack(side=tk.LEFT)
            EditableLabel(left, text=subj).pack(side=tk.LEFT)
            for j, obj in enumerate(objs, 1):
                var = tk.IntVar(value=1 if obj in self.data["subjects"].get(subj, []) else 0)
                cb = ttk.Checkbutton(self.matrix_frame, variable=var)
                cb.grid(row=i, column=j, sticky="nsew", padx=1, pady=1)
                self.check_vars[(subj, obj)] = var

        for c in range(len(objs) + 1):
            self.matrix_frame.grid_columnconfigure(c, weight=1)

    # --- Utility ---
    def log(self, *args):
        t = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{t}] " + " ".join(str(a) for a in args)
        self.info_text.config(state=tk.NORMAL)
        self.info_text.insert("end", line + "\n")
        self.info_text.see("end")
        self.info_text.config(state=tk.DISABLED)
        write_audit(*args)

    def apply_matrix_changes(self):
        for (s, o), var in self.check_vars.items():
            if s in self.data["subjects"]:
                allowed = set(self.data["subjects"][s])
                if var.get():
                    allowed.add(o)
                else:
                    allowed.discard(o)
                self.data["subjects"][s] = list(allowed)
        save_matrix(self.data)
        self.log("Матрица обновлена и сохранена.")

    # --- Controls ---
    def on_add_subject(self):
        name = self.add_subject_entry.get().strip()
        if not name:
            messagebox.showwarning("Валидация", "Имя субъекта пустое.")
            return
        if len(name) > MAX_SUBJECT_LEN:
            messagebox.showwarning("Валидация", f"Имя слишком длинное (макс {MAX_SUBJECT_LEN}).")
            return
        if name in self.data["subjects"]:
            messagebox.showinfo("Инфо", "Такой субъект уже существует.")
            return
        self.data["subjects"][name] = []
        self.build_matrix_ui()
        self.log(f"Добавлен субъект {name}")

    def on_add_object(self):
        obj = self.add_object_entry.get().strip()
        if not validate_object_token(obj):
            messagebox.showwarning("Ошибка", "Объект должен быть одной латинской буквой.")
            return
        if obj in self.data["objects"]:
            messagebox.showinfo("Инфо", "Такой объект уже существует.")
            return
        self.data["objects"].append(obj)
        self.build_matrix_ui()
        self.log(f"Добавлен объект {obj}")

    def on_delete_object(self):
        obj = self.add_object_entry.get().strip()
        if not obj:
            messagebox.showwarning("Валидация", "Введите объект для удаления.")
            return
        if obj not in self.data["objects"]:
            messagebox.showinfo("Инфо", f"Объект {obj} не найден.")
            return
        if not messagebox.askyesno("Подтверждение", f"Удалить объект '{obj}' и все связанные права?"):
            return
        self.data["objects"].remove(obj)
        for s in self.data["subjects"]:
            if obj in self.data["subjects"][s]:
                self.data["subjects"][s].remove(obj)
        self.build_matrix_ui()
        self.log(f"Удалён объект {obj}")

    def on_grant(self):
        try:
            subs = parse_subjects(self.cmd_subjects.get())
            objs = parse_objects(self.cmd_objects.get())
            grant(self.data, subs, objs)
            self.build_matrix_ui()
            self.log(f"grant {subs} -> {objs}")
        except Exception as e:
            messagebox.showerror("Ошибка grant", str(e))

    def on_create(self):
        try:
            subs = parse_subjects(self.cmd_subjects.get()) if self.cmd_subjects.get().strip() else []
            objs = parse_objects(self.cmd_objects.get()) if self.cmd_objects.get().strip() else []
            for subj in subs:
                status = create(self.data, subj, objs)
                self.log(f"create {subj} -> {objs} ({status})")
            self.build_matrix_ui()
        except Exception as e:
            messagebox.showerror("Ошибка create", str(e))

    def on_remove(self):
        try:
            subs = parse_subjects(self.cmd_subjects.get())
            objs = parse_objects(self.cmd_objects.get())
            remove(self.data, subs, objs)
            self.build_matrix_ui()
            self.log(f"remove {subs} -/-> {objs}")
        except Exception as e:
            messagebox.showerror("Ошибка remove", str(e))

    def on_grant_all(self):
        try:
            subs = parse_subjects(self.cmd_subjects.get())
            grant_all(self.data, subs)
            self.build_matrix_ui()
            self.log(f"grant_all {subs}")
        except Exception as e:
            messagebox.showerror("Ошибка grant_all", str(e))

    def on_remove_all(self):
        try:
            subs = parse_subjects(self.cmd_subjects.get())
            remove_all(self.data, subs)
            self.build_matrix_ui()
            self.log(f"remove_all {subs}")
        except Exception as e:
            messagebox.showerror("Ошибка remove_all", str(e))

    def on_save(self):
        save_matrix(self.data)
        self.log("Матрица сохранена в файл.")

    def on_load_from(self):
        path = filedialog.askopenfilename(title="Загрузить матрицу", filetypes=[("JSON", "*.json")])
        if not path:
            return
        self.data = load_matrix(path)
        self.data_file = path
        self.build_matrix_ui()
        self.log(f"Загружена матрица из {path}")

    def on_export(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not path:
            return
        save_matrix(self.data, path)
        self.log(f"Экспортирована матрица в {path}")

    def rename_subject(self, subj):
        new = simpledialog.askstring("Переименование", f"Новое имя для '{subj}':", parent=self)
        if not new:
            return
        if new in self.data["subjects"]:
            messagebox.showerror("Ошибка", "Такое имя уже существует.")
            return
        self.data["subjects"][new] = self.data["subjects"].pop(subj)
        self.build_matrix_ui()
        self.log(f"Переименован {subj} -> {new}")

    def delete_subject(self, subj):
        if not messagebox.askyesno("Подтверждение", f"Удалить субъекта '{subj}'?"):
            return
        self.data["subjects"].pop(subj, None)
        self.build_matrix_ui()
        self.log(f"Удалён субъект {subj}")


if __name__ == "__main__":
    app = AdminApp()
    app.mainloop()
