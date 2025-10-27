#!/usr/bin/env python3
# user.py — приложение пользователя для авторизации и фильтрации строк по матрице доступа
import json
import os
import time
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

DATA_FILE = "access_matrix.json"
POLL_INTERVAL_MS = 1000  # опрашиваем файл каждые 1000 ms

def load_matrix(path=DATA_FILE):
    if not os.path.exists(path):
        return {"objects": [], "subjects": {}}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("objects", [])
        data.setdefault("subjects", {})
        return data
    except Exception as e:
        messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить матрицу:\n{e}")
        return {"objects": [], "subjects": {}}

class UserApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Пользователь — фильтрация по правам доступа")
        self.geometry("600x400")
        self.minsize(500, 300)
        self.data_file = DATA_FILE
        self.data = load_matrix(self.data_file)
        self.last_mtime = os.path.getmtime(self.data_file) if os.path.exists(self.data_file) else None
        self.current_user = None
        self.allowed_set = set()

        ttk.Style().theme_use("clam")

        self.build_ui()
        # Start periodic check for file changes
        self.after(POLL_INTERVAL_MS, self.poll_file_changes)

    def build_ui(self):
        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Login area
        login_frame = ttk.Labelframe(frame, text="Авторизация")
        login_frame.pack(fill=tk.X, pady=5)
        ttk.Label(login_frame, text="Имя пользователя (субъекта):").pack(anchor='w')
        self.user_entry = ttk.Entry(login_frame)
        self.user_entry.pack(fill=tk.X, pady=3)
        self.user_entry.bind("<Return>", lambda e: self.on_login())
        ttk.Button(login_frame, text="Войти", command=self.on_login).pack(pady=2)

        # Current rights
        self.rights_label = ttk.Label(login_frame, text="Текущие права: (не авторизован)")
        self.rights_label.pack(anchor='w', pady=3)

        # Filter area
        filter_frame = ttk.Labelframe(frame, text="Фильтрация")
        filter_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        ttk.Label(filter_frame, text="Введите строку для фильтрации:").pack(anchor='w')
        self.input_text = ttk.Entry(filter_frame)
        self.input_text.pack(fill=tk.X, pady=3)
        self.input_text.bind("<KeyRelease>", lambda e: self.on_filter())

        ttk.Label(filter_frame, text="Результат:").pack(anchor='w')
        self.output_text = tk.Text(filter_frame, height=2)
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=3)

        # Info
        info_frame = ttk.Frame(frame)
        info_frame.pack(fill=tk.X, pady=5)
        ttk.Button(info_frame, text="Обновить матрицу вручную", command=self.reload_matrix).pack(side=tk.LEFT)
        ttk.Button(info_frame, text="Информация о файле матрицы", command=self.show_file_info).pack(side=tk.LEFT, padx=5)

    def on_login(self):
        name = self.user_entry.get().strip()
        if not name:
            messagebox.showwarning("Валидация", "Введите имя пользователя.")
            return
        # Reload matrix to ensure fresh
        self.data = load_matrix(self.data_file)
        if name not in self.data.get("subjects", {}):
            messagebox.showerror("Ошибка авторизации", f"Пользователь '{name}' не найден в матрице доступа.")
            return
        self.current_user = name
        self.allowed_set = set(self.data["subjects"].get(name, []))
        self.rights_label.config(text=f"Текущие права: {''.join(sorted(self.allowed_set)) if self.allowed_set else '(нет прав)'}")
        self.on_filter()
        messagebox.showinfo("Успех", f"Авторизация прошла успешно: {name}")

    def on_filter(self):
        if not self.current_user:
            self.output_text.delete("1.0", "end")
            self.output_text.insert("end", "(сначала авторизуйтесь)")
            return
        s = self.input_text.get()
        # Filter: keep only символы, которые есть в allowed_set (точное совпадение символа)
        res_chars = sorted({ch for ch in s if ch in self.allowed_set})
        result = ''.join(res_chars)
        self.output_text.delete("1.0", "end")
        self.output_text.insert("end", result)

    def reload_matrix(self):
        self.data = load_matrix(self.data_file)
        self.last_mtime = os.path.getmtime(self.data_file) if os.path.exists(self.data_file) else None
        if self.current_user:
            self.allowed_set = set(self.data["subjects"].get(self.current_user, []))
            self.rights_label.config(text=f"Текущие права: {''.join(sorted(self.allowed_set)) if self.allowed_set else '(нет прав)'}")
            self.on_filter()
        messagebox.showinfo("Обновлено", "Матрица доступа загружена заново.")

    def poll_file_changes(self):
        try:
            if os.path.exists(self.data_file):
                m = os.path.getmtime(self.data_file)
                if self.last_mtime is None or m != self.last_mtime:
                    # file changed -> reload
                    self.data = load_matrix(self.data_file)
                    self.last_mtime = m
                    if self.current_user:
                        self.allowed_set = set(self.data["subjects"].get(self.current_user, []))
                        self.rights_label.config(text=f"Текущие права: {''.join(sorted(self.allowed_set)) if self.allowed_set else '(нет прав)'}")
                        self.on_filter()
            # schedule next check
        except Exception as e:
            # Non-fatal; show in small popup
            print("Ошибка опроса файла:", e)
        finally:
            self.after(POLL_INTERVAL_MS, self.poll_file_changes)

    def show_file_info(self):
        if os.path.exists(self.data_file):
            st = os.stat(self.data_file)
            msg = f"Файл: {self.data_file}\nРазмер: {st.st_size} байт\nПоследняя модификация: {time.ctime(st.st_mtime)}"
        else:
            msg = f"Файл {self.data_file} не найден."
        messagebox.showinfo("Информация о файле", msg)


if __name__ == "__main__":
    app = UserApp()
    app.mainloop()
