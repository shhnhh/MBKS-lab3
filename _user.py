#!/usr/bin/env python3
# user.py — приложение пользователя для авторизации и фильтрации строк по матрице доступа
import json
import os
import time
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

# Настройка внешнего вида Custom Tkinter
ctk.set_appearance_mode("Dark")  # "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

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
        CTkMessagebox(title="Ошибка загрузки", message=f"Не удалось загрузить матрицу:\n{e}", icon="cancel")
        return {"objects": [], "subjects": {}}

class ModernUserApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🔐 User Access Filter")
        self.geometry("800x600")
        self.minsize(700, 500)
        
        self.data_file = DATA_FILE
        self.data = load_matrix(self.data_file)
        self.last_mtime = os.path.getmtime(self.data_file) if os.path.exists(self.data_file) else None
        self.current_user = None
        self.allowed_set = set()
        self.is_authorized = False

        self.build_ui()
        # Start periodic check for file changes
        self.after(POLL_INTERVAL_MS, self.poll_file_changes)

    def build_ui(self):
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(self, height=80)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame, 
            text="🔐 User Access Filter", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # Status indicator
        self.status_label = ctk.CTkLabel(
            header_frame,
            text="● Не авторизован",
            text_color="#ff6b6b",
            font=ctk.CTkFont(weight="bold")
        )
        self.status_label.grid(row=0, column=1, padx=20, pady=15, sticky="e")
        
        # Main content area
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Login section
        login_section = ctk.CTkFrame(main_frame)
        login_section.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        login_section.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            login_section, 
            text="👤 Авторизация", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Login inputs
        input_frame = ctk.CTkFrame(login_section)
        input_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        input_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(input_frame, text="Пользователь:").grid(row=0, column=0, padx=(10, 5), pady=5, sticky="w")
        self.user_entry = ctk.CTkEntry(input_frame, placeholder_text="Введите имя пользователя...")
        self.user_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.user_entry.bind("<Return>", lambda e: self.on_login())
        
        login_btn = ctk.CTkButton(
            input_frame, 
            text="Войти в систему", 
            command=self.on_login,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        login_btn.grid(row=0, column=2, padx=(5, 10), pady=5)
        
        # Rights display
        self.rights_frame = ctk.CTkFrame(login_section)
        self.rights_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=(5, 10))
        
        self.rights_label = ctk.CTkLabel(
            self.rights_frame, 
            text="Текущие права доступа: (не авторизован)",
            font=ctk.CTkFont(size=12)
        )
        self.rights_label.pack(padx=10, pady=8)
        
        # Filter section
        filter_section = ctk.CTkFrame(main_frame)
        filter_section.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        filter_section.grid_columnconfigure(0, weight=1)
        filter_section.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            filter_section, 
            text="🔧 Фильтрация текста", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Input area
        ctk.CTkLabel(filter_section, text="Исходный текст:").grid(row=1, column=0, padx=10, pady=(10, 5), sticky="w")
        self.input_text = ctk.CTkTextbox(filter_section, height=100)
        self.input_text.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        self.input_text.bind("<KeyRelease>", lambda e: self.after(100, self.on_filter))
        
        # Output area
        ctk.CTkLabel(filter_section, text="Результат фильтрации:").grid(row=3, column=0, padx=10, pady=(20, 5), sticky="w")
        
        output_frame = ctk.CTkFrame(filter_section, fg_color="#2d3436")
        output_frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=5)
        output_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_rowconfigure(0, weight=1)
        
        self.output_text = ctk.CTkTextbox(
            output_frame, 
            height=100,
            fg_color="#2d3436",
            text_color="#ffffff",
            font=ctk.CTkFont(family="Courier", size=13)
        )
        self.output_text.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.output_text.configure(state="disabled")
        
        # Footer with controls
        footer_frame = ctk.CTkFrame(self)
        footer_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        
        # Left side buttons
        left_btn_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
        left_btn_frame.pack(side="left", padx=10)
        
        ctk.CTkButton(
            left_btn_frame,
            text="🔄 Обновить матрицу",
            command=self.reload_matrix,
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            left_btn_frame,
            text="ℹ️ Информация о системе",
            command=self.show_system_info,
            width=150
        ).pack(side="left", padx=5)
        
        # Right side - file status
        self.file_status_label = ctk.CTkLabel(
            footer_frame,
            text=f"Файл матрицы: {self.get_file_status()}",
            font=ctk.CTkFont(size=11)
        )
        self.file_status_label.pack(side="right", padx=10)

    def get_file_status(self):
        if os.path.exists(self.data_file):
            st = os.stat(self.data_file)
            size_kb = st.st_size / 1024
            return f"✓ {os.path.basename(self.data_file)} ({size_kb:.1f} KB)"
        else:
            return f"✗ {self.data_file} (не найден)"

    def on_login(self):
        name = self.user_entry.get().strip()
        if not name:
            CTkMessagebox(title="Внимание", 
                         message="Пожалуйста, введите имя пользователя для авторизации.", 
                         icon="warning")
            return
        
        # Reload matrix to ensure fresh data
        self.data = load_matrix(self.data_file)
        if name not in self.data.get("subjects", {}):
            CTkMessagebox(title="Ошибка авторизации", 
                         message=f"Пользователь '{name}' не найден в системе доступа.\n\n"
                                "Возможные причины:\n"
                                "• Пользователь не существует\n"
                                "• Отсутствуют права доступа\n"
                                "• Файл матрицы поврежден", 
                         icon="cancel")
            return
        
        self.current_user = name
        self.is_authorized = True
        self.allowed_set = set(self.data["subjects"].get(name, []))
        
        # Update UI
        rights_text = f"Текущие права доступа: {''.join(sorted(self.allowed_set)) if self.allowed_set else '(нет прав)'}"
        self.rights_label.configure(text=rights_text)
        self.status_label.configure(text="● Авторизован", text_color="#2ecc71")
        
        CTkMessagebox(title="Успешная авторизация", 
                     message=f"Добро пожаловать, {name}!\n\n"
                            f"Ваши права доступа: {', '.join(sorted(self.allowed_set)) if self.allowed_set else 'отсутствуют'}",
                     icon="check")
        
        self.on_filter()

    def on_filter(self):
        if not self.is_authorized:
            self.output_text.configure(state="normal")
            self.output_text.delete("1.0", "end")
            self.output_text.insert("end", "⚠️ Для использования фильтрации необходимо авторизоваться")
            self.output_text.configure(state="disabled")
            return
        
        input_content = self.input_text.get("1.0", "end-1c")
        
        # Filter: keep only символы, которые есть в allowed_set
        res_chars = sorted({ch for ch in input_content if ch in self.allowed_set})
        result = ''.join(res_chars)
        
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        
        if result:
            self.output_text.insert("end", result)
            # Подсветка количества символов
            char_count = len(result)
            self.output_text.insert("end", f"\n\n---\nОтфильтровано символов: {char_count}")
        else:
            self.output_text.insert("end", "❌ Нет доступных символов для отображения\n\n---\nРезультат фильтрации пуст")
        
        self.output_text.configure(state="disabled")

    def reload_matrix(self):
        self.data = load_matrix(self.data_file)
        self.last_mtime = os.path.getmtime(self.data_file) if os.path.exists(self.data_file) else None
        
        # Update file status
        self.file_status_label.configure(text=f"Файл матрицы: {self.get_file_status()}")
        
        if self.is_authorized:
            self.allowed_set = set(self.data["subjects"].get(self.current_user, []))
            rights_text = f"Текущие права доступа: {''.join(sorted(self.allowed_set)) if self.allowed_set else '(нет прав)'}"
            self.rights_label.configure(text=rights_text)
            self.on_filter()
        
        CTkMessagebox(title="Обновление завершено", 
                     message="Матрица доступа успешно загружена заново.", 
                     icon="info")

    def show_system_info(self):
        if os.path.exists(self.data_file):
            st = os.stat(self.data_file)
            file_info = (f"Файл матрицы: {self.data_file}\n"
                        f"Размер: {st.st_size} байт ({st.st_size/1024:.1f} KB)\n"
                        f"Последняя модификация: {time.ctime(st.st_mtime)}\n"
                        f"Создан: {time.ctime(st.st_ctime)}")
        else:
            file_info = f"Файл {self.data_file} не найден."
        
        system_info = (f"Статус системы:\n"
                      f"• Пользователь: {self.current_user if self.is_authorized else 'Не авторизован'}\n"
                      f"• Всего субъектов: {len(self.data.get('subjects', {}))}\n"
                      f"• Всего объектов: {len(self.data.get('objects', []))}\n"
                      f"• Авторизован: {'Да' if self.is_authorized else 'Нет'}")
        
        full_message = f"{system_info}\n\n{file_info}"
        
        CTkMessagebox(title="Информация о системе", 
                     message=full_message, 
                     icon="info")

    def poll_file_changes(self):
        try:
            if os.path.exists(self.data_file):
                m = os.path.getmtime(self.data_file)
                if self.last_mtime is None or m != self.last_mtime:
                    # File changed -> reload
                    self.data = load_matrix(self.data_file)
                    self.last_mtime = m
                    
                    # Update file status
                    self.file_status_label.configure(text=f"Файл матрицы: {self.get_file_status()}")
                    
                    if self.is_authorized:
                        self.allowed_set = set(self.data["subjects"].get(self.current_user, []))
                        rights_text = f"Текущие права доступа: {''.join(sorted(self.allowed_set)) if self.allowed_set else '(нет прав)'}"
                        self.rights_label.configure(text=rights_text)
                        self.on_filter()
                        
                        # Show notification about changes
                        CTkMessagebox(title="Обновление данных", 
                                     message="Матрица доступа была обновлена.\nВаши права перезагружены.", 
                                     icon="info")
        except Exception as e:
            # Non-fatal error
            print("Ошибка опроса файла:", e)
        finally:
            self.after(POLL_INTERVAL_MS, self.poll_file_changes)


if __name__ == "__main__":
    app = ModernUserApp()
    app.mainloop()