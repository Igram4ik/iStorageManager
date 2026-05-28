import tkinter as tk
from tkinter import messagebox
from database import authenticate, register_user
from widgets import ModernButton   # импорт из widgets

class AuthWindow:
    def __init__(self, on_success):
        self.on_success = on_success
        self.root = tk.Tk()
        self.root.title("Авторизация")
        self.root.geometry("400x480")
        self.root.resizable(False, False)

        # Градиентный фон
        self.canvas = tk.Canvas(self.root, width=400, height=480, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.draw_gradient()

        # Контейнер
        self.frame = tk.Frame(self.root, bg='#f0f4fa', bd=0)
        self.frame.place(relx=0.5, rely=0.5, anchor="center", width=320, height=400)

        # Заголовок
        tk.Label(self.frame, text="Добро пожаловать", font=('Arial', 18, 'bold'),
                 bg='#f0f4fa', fg='#003366').pack(pady=(25, 10))

        # Поля
        tk.Label(self.frame, text="Логин", font=('Arial', 10), bg='#f0f4fa').pack(anchor='w', padx=20)
        self.entry_login = tk.Entry(self.frame, font=('Arial', 11), bd=2, relief='flat',
                                    bg='white', fg='#333', insertbackground='#003366')
        self.entry_login.pack(padx=20, pady=(0,10), ipady=3, fill='x')
        self.entry_login.focus_set()

        tk.Label(self.frame, text="Пароль", font=('Arial', 10), bg='#f0f4fa').pack(anchor='w', padx=20)
        self.entry_pass = tk.Entry(self.frame, font=('Arial', 11), bd=2, relief='flat',
                                   show="*", bg='white', fg='#333', insertbackground='#003366')
        self.entry_pass.pack(padx=20, pady=(0,15), ipady=3, fill='x')

        # Кнопка Войти
        btn_login = ModernButton(self.frame, text="Войти", command=self.do_login, width=200, height=35)
        btn_login.pack(pady=5)

        # Разделитель
        ttk_sep = tk.Frame(self.frame, height=1, bg='#cccccc')
        ttk_sep.pack(fill='x', padx=30, pady=10)

        # Кнопка Регистрация (с другими цветами)
        btn_reg = ModernButton(self.frame, text="Регистрация", command=self.open_register,
                               width=200, height=35, bg="#6c757d", bg_hover="#5a6268")
        btn_reg.pack(pady=5)

        self.root.mainloop()

    def draw_gradient(self):
        h = 480
        for i in range(h):
            r1, g1, b1 = 0x4a, 0x90, 0xd9
            r2, g2, b2 = 0xe8, 0xf0, 0xf8
            ratio = i / h
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.canvas.create_line(0, i, 400, i, fill=color)

    def do_login(self):
        login = self.entry_login.get().strip()
        password = self.entry_pass.get().strip()
        if not login or not password:
            messagebox.showwarning("Ошибка", "Введите логин и пароль")
            return
        user = authenticate(login, password)
        if user:
            self.root.destroy()
            self.on_success(user)
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

    def open_register(self):
        RegisterWindow(self.root)

class RegisterWindow:
    def __init__(self, parent):
        self.win = tk.Toplevel(parent)
        self.win.title("Регистрация")
        self.win.geometry("340x300")
        self.win.resizable(False, False)
        self.win.grab_set()

        canvas = tk.Canvas(self.win, width=340, height=300, highlightthickness=0)
        canvas.pack()
        for i in range(300):
            r, g, b = 0xe8, 0xf0, 0xf8
            color = f'#{r:02x}{g:02x}{b:02x}'
            canvas.create_line(0, i, 340, i, fill=color)

        frame = tk.Frame(self.win, bg='#f0f4fa')
        frame.place(relx=0.5, rely=0.5, anchor="center", width=300, height=260)

        tk.Label(frame, text="Новый пользователь", font=('Arial', 14, 'bold'),
                 bg='#f0f4fa', fg='#003366').pack(pady=(15,10))

        tk.Label(frame, text="Логин", bg='#f0f4fa').pack(anchor='w', padx=20)
        self.entry_login = tk.Entry(frame, font=('Arial', 10), relief='flat', bd=2)
        self.entry_login.pack(padx=20, pady=(0,8), ipady=2, fill='x')

        tk.Label(frame, text="Пароль", bg='#f0f4fa').pack(anchor='w', padx=20)
        self.entry_pass = tk.Entry(frame, font=('Arial', 10), relief='flat', bd=2, show="*")
        self.entry_pass.pack(padx=20, pady=(0,15), ipady=2, fill='x')

        btn = ModernButton(frame, text="Зарегистрироваться", command=self.do_register,
                           width=180, height=30)
        btn.pack(pady=5)

    def do_register(self):
        login = self.entry_login.get().strip()
        password = self.entry_pass.get().strip()
        if len(login) < 3 or len(password) < 3:
            messagebox.showwarning("Ошибка", "Логин и пароль должны содержать минимум 3 символа")
            return
        if register_user(login, password):
            messagebox.showinfo("Успех", "Регистрация прошла успешно. Теперь войдите.")
            self.win.destroy()
        else:
            messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует")