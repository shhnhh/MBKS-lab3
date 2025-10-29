import os
import json
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from widgets.matrix import Matrix
from style import Style
from string import ascii_letters

DATA_FILE = "access_matrix.json"
MAX_SUBJECT_LEN = 256

# Настройка внешнего вида Custom Tkinter
ctk.set_appearance_mode("System")  # "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

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
        CTkMessagebox(
            title="Ошибка загрузки", 
            message=f"Не удалось загрузить {path}:\n{e}", 
            icon="cancel"
        )
        return {"objects": [], "subjects": {}}


def save_matrix(data, path=DATA_FILE):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Матрица сохранена.")
    except Exception as e:
        CTkMessagebox(
            title="Ошибка сохранения", 
            message=f"Не удалось сохранить {path}:\n{e}", 
            icon="cancel"
        )

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


class AdminApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("🔧 Администратор - Управление доступом")
        self.geometry("1200x700")
        
        # Создаем основную сетку
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Главный фрейм
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=3)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Левая панель для матрицы
        self.left_frame = ctk.CTkFrame(main_frame)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)
        
        # Правая панель для управления
        self.right_frame = ctk.CTkFrame(main_frame, width=350)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)
        self.right_frame.grid_propagate(False)
        
        # Инициализация матрицы
        self.matrix = Matrix(self.left_frame, load_matrix())
        self.matrix.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.build_controls()
        
        # Привязка события изменения матрицы
        self.matrix.bind('<<MatrixChanged>>', lambda event: save_matrix(self.data))

    @property
    def data(self):
        return self.matrix.data

    def build_controls(self):
        # Заголовок
        title_label = ctk.CTkLabel(
            self.right_frame, 
            text="⚙️ Управление доступом", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=15)
        
        # Фрейм для полей ввода и кнопок
        cmd_frame = ctk.CTkFrame(self.right_frame)
        cmd_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Секция субъектов
        subjects_frame = ctk.CTkFrame(cmd_frame)
        subjects_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            subjects_frame, 
            text="👥 Субъекты:", 
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(5, 0))
        
        self.cmd_subjects = ctk.CTkEntry(
            subjects_frame, 
            placeholder_text="Введите имена через пробел или запятую..."
        )
        self.cmd_subjects.pack(fill="x", pady=5)
        
        # Секция объектов
        objects_frame = ctk.CTkFrame(cmd_frame)
        objects_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            objects_frame, 
            text="📁 Объекты:", 
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(5, 0))
        
        self.cmd_objects = ctk.CTkEntry(
            objects_frame, 
            placeholder_text="Латинские буквы (A, B, C...)"
        )
        self.cmd_objects.pack(fill="x", pady=5)
        
        # Фрейм для кнопок команд
        button_frame = ctk.CTkFrame(cmd_frame)
        button_frame.pack(fill="x", pady=20)
        
        # Кнопки команд с иконками и цветами
        ctk.CTkButton(
            button_frame, 
            text="🎯 Grant - Выдать права",
            command=self.on_grant,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        ).pack(fill="x", pady=3)
        
        ctk.CTkButton(
            button_frame, 
            text="➕ Create - Создать субъекта",
            command=self.on_create,
            fg_color="#3498db",
            hover_color="#2980b9"
        ).pack(fill="x", pady=3)
        
        ctk.CTkButton(
            button_frame, 
            text="🗑️ Remove - Удалить права",
            command=self.on_remove,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        ).pack(fill="x", pady=3)
        
        ctk.CTkButton(
            button_frame, 
            text="✅ Grant All - Все права",
            command=self.on_grant_all,
            fg_color="#9b59b6",
            hover_color="#8e44ad"
        ).pack(fill="x", pady=3)
        
        ctk.CTkButton(
            button_frame, 
            text="❌ Remove All - Удалить все",
            command=self.on_remove_all,
            fg_color="#e67e22",
            hover_color="#d35400"
        ).pack(fill="x", pady=3)
        
        # Информационная панель
        info_frame = ctk.CTkFrame(cmd_frame, fg_color="#2c3e50")
        info_frame.pack(fill="x", pady=10)
        
        info_label = ctk.CTkLabel(
            info_frame,
            text="💡 Справка:\n"
                 "• Субъекты: пользователи/группы\n"
                 "• Объекты: ресурсы (A-Z, a-z)\n"
                 "• Права: доступ к объектам",
            font=ctk.CTkFont(size=11),
            justify="left",
            text_color="#ecf0f1"
        )
        info_label.pack(padx=10, pady=10)
        
        # Статусная строка
        status_frame = ctk.CTkFrame(self.right_frame)
        status_frame.pack(fill="x", side="bottom", padx=15, pady=10)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="✅ Система готова к работе",
            font=ctk.CTkFont(size=10),
            text_color="#27ae60"
        )
        self.status_label.pack()

    def show_success(self, message):
        self.status_label.configure(text=f"✅ {message}", text_color="#27ae60")
        CTkMessagebox(title="Успех", message=message, icon="check")

    def show_error(self, message):
        self.status_label.configure(text=f"❌ {message}", text_color="#e74c3c")
        CTkMessagebox(title="Ошибка", message=message, icon="cancel")

    def show_warning(self, message):
        self.status_label.configure(text=f"⚠️ {message}", text_color="#f39c12")
        CTkMessagebox(title="Внимание", message=message, icon="warning")

    def on_grant(self):
        try:
            subs = parse_subjects(self.cmd_subjects.get())
            objs = parse_objects(self.cmd_objects.get())
            if not subs or not objs:
                self.show_warning("Заполните поля субъектов и объектов")
                return
            grant(self.data, subs, objs)
            self.matrix.redraw()
            self.show_success(f"Права выданы: {', '.join(subs)} → {', '.join(objs)}")
        except Exception as e:
            self.show_error(f"Ошибка grant: {str(e)}")

    def on_create(self):
        try:
            subs = parse_subjects(self.cmd_subjects.get()) if self.cmd_subjects.get().strip() else []
            objs = parse_objects(self.cmd_objects.get()) if self.cmd_objects.get().strip() else []
            
            if not subs:
                self.show_warning("Введите хотя бы одного субъекта")
                return
                
            created_count = 0
            existing_count = 0
            
            for subj in subs:
                status = create(self.data, subj, objs)
                if status == "created":
                    created_count += 1
                else:
                    existing_count += 1
            
            self.matrix.redraw()
            
            message = []
            if created_count > 0:
                message.append(f"Создано: {created_count}")
            if existing_count > 0:
                message.append(f"Обновлено: {existing_count}")
                
            self.show_success("; ".join(message))
            
        except Exception as e:
            self.show_error(f"Ошибка create: {str(e)}")

    def on_remove(self):
        try:
            subs = parse_subjects(self.cmd_subjects.get())
            objs = parse_objects(self.cmd_objects.get())
            if not subs or not objs:
                self.show_warning("Заполните поля субъектов и объектов")
                return
            remove(self.data, subs, objs)
            self.matrix.redraw()
            self.show_success(f"Права удалены: {', '.join(subs)} → {', '.join(objs)}")
        except Exception as e:
            self.show_error(f"Ошибка remove: {str(e)}")

    def on_grant_all(self):
        try:
            subs = parse_subjects(self.cmd_subjects.get())
            if not subs:
                self.show_warning("Введите субъектов")
                return
            grant_all(self.data, subs)
            self.matrix.redraw()
            self.show_success(f"Все права выданы: {', '.join(subs)}")
        except Exception as e:
            self.show_error(f"Ошибка grant_all: {str(e)}")

    def on_remove_all(self):
        try:
            subs = parse_subjects(self.cmd_subjects.get())
            if not subs:
                self.show_warning("Введите субъектов")
                return
            remove_all(self.data, subs)
            self.matrix.redraw()
            self.show_success(f"Все права удалены: {', '.join(subs)}")
        except Exception as e:
            self.show_error(f"Ошибка remove_all: {str(e)}")


if __name__ == "__main__":
    app = AdminApp()
    Style()
    app.mainloop()