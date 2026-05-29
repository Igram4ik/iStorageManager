import tkinter as tk
from tkinter import ttk, messagebox
from database import get_products, add_product, update_product, delete_product, get_stock, set_stock_quantity
from widgets import ModernButton

class ManageProductsWindow:
    def __init__(self, parent):
        self.win = tk.Toplevel(parent)
        self.win.title("Управление товарами – Администратор")
        self.win.geometry("750x550")
        self.win.grab_set()
        self.win.resizable(True, True)

        # Фон (светлый градиент)
        canvas = tk.Canvas(self.win, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        self._draw_gradient(canvas)

        main_frame = tk.Frame(self.win, bg='#f4f8fc')
        main_frame.place(relx=0.5, rely=0.5, anchor="center", width=700, height=500)

        # Заголовок
        tk.Label(main_frame, text="Управление номенклатурой", font=('Arial', 16, 'bold'),
                 bg='#f4f8fc', fg='#003366').pack(pady=10)

        # Левая часть: список товаров
        left_frame = tk.Frame(main_frame, bg='#f4f8fc')
        left_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        tk.Label(left_frame, text="Список товаров", font=('Arial', 11, 'bold'),
                 bg='#f4f8fc').pack(anchor='w')

        tree_frame = tk.Frame(left_frame, bg='#f4f8fc')
        tree_frame.pack(fill='both', expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=('id', 'name', 'unit', 'stock'),
                                 show='headings', height=15)
        self.tree.heading('id', text='ID')
        self.tree.heading('name', text='Наименование')
        self.tree.heading('unit', text='Ед. изм.')
        self.tree.heading('stock', text='Остаток')
        self.tree.column('id', width=40, anchor='center')
        self.tree.column('name', width=250)
        self.tree.column('unit', width=80, anchor='center')
        self.tree.column('stock', width=80, anchor='center')
        self.tree.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        # Правая часть: редактирование / добавление
        right_frame = tk.Frame(main_frame, bg='#f4f8fc', relief='groove', bd=1)
        right_frame.pack(side='right', fill='y', padx=10, pady=10, ipadx=10, ipady=10)

        tk.Label(right_frame, text="Редактирование", font=('Arial', 11, 'bold'),
                 bg='#f4f8fc').pack(pady=(0,10))

        # Поля для редактирования
        tk.Label(right_frame, text="ID товара:", bg='#f4f8fc', anchor='w').pack(fill='x')
        self.edit_id = tk.Entry(right_frame, font=('Arial', 10), state='readonly', relief='flat')
        self.edit_id.pack(fill='x', pady=(0,5))

        tk.Label(right_frame, text="Название:", bg='#f4f8fc', anchor='w').pack(fill='x')
        self.edit_name = tk.Entry(right_frame, font=('Arial', 10), relief='flat')
        self.edit_name.pack(fill='x', pady=(0,5))

        tk.Label(right_frame, text="Единица измерения:", bg='#f4f8fc', anchor='w').pack(fill='x')
        self.edit_unit = tk.Entry(right_frame, font=('Arial', 10), relief='flat')
        self.edit_unit.pack(fill='x', pady=(0,5))

        tk.Label(right_frame, text="Количество (новое значение):", bg='#f4f8fc', anchor='w').pack(fill='x')
        self.edit_qty = tk.Entry(right_frame, font=('Arial', 10), relief='flat')
        self.edit_qty.pack(fill='x', pady=(0,10))

        # Кнопки
        btn_update = ModernButton(right_frame, text="Сохранить изменения", command=self.update_product,
                                  width=180, height=30)
        btn_update.pack(pady=5)

        btn_set_qty = ModernButton(right_frame, text="Установить количество", command=self.set_quantity,
                                   width=180, height=30, bg="#28a745", bg_hover="#218838")
        btn_set_qty.pack(pady=5)

        btn_delete = ModernButton(right_frame, text="Удалить товар", command=self.delete_product,
                                  width=180, height=30, bg="#dc3545", bg_hover="#c82333")
        btn_delete.pack(pady=5)

        tk.Label(right_frame, text="Добавление нового товара", font=('Arial', 10, 'bold'),
                 bg='#f4f8fc').pack(pady=(15,5))

        tk.Label(right_frame, text="Название:", bg='#f4f8fc', anchor='w').pack(fill='x')
        self.new_name = tk.Entry(right_frame, font=('Arial', 10), relief='flat')
        self.new_name.pack(fill='x', pady=(0,5))

        tk.Label(right_frame, text="Единица измерения:", bg='#f4f8fc', anchor='w').pack(fill='x')
        self.new_unit = tk.Entry(right_frame, font=('Arial', 10), relief='flat')
        self.new_unit.pack(fill='x', pady=(0,10))

        btn_add = ModernButton(right_frame, text="Добавить товар", command=self.add_product,
                               width=180, height=30, bg="#17a2b8", bg_hover="#138496")
        btn_add.pack(pady=5)

        # Загрузка данных
        self.load_products()
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

    def _draw_gradient(self, canvas):
        w = 750
        h = 550
        canvas.config(width=w, height=h)
        for i in range(h):
            r = int(0xe8 + (0xee - 0xe8) * (i / h))
            g = int(0xf0 + (0xf4 - 0xf0) * (i / h))
            b = int(0xf8 + (0xfc - 0xf8) * (i / h))
            color = f'#{r:02x}{g:02x}{b:02x}'
            canvas.create_line(0, i, w, i, fill=color)

    def load_products(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = get_products()  # возвращает список с полями id, name, unit
        for p in rows:
            stock = get_stock(p['id'])
            self.tree.insert('', 'end', values=(p['id'], p['name'], p['unit'], stock))

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        values = item['values']
        if values:
            self.edit_id.config(state='normal')
            self.edit_id.delete(0, tk.END)
            self.edit_id.insert(0, values[0])
            self.edit_id.config(state='readonly')
            self.edit_name.delete(0, tk.END)
            self.edit_name.insert(0, values[1])
            self.edit_unit.delete(0, tk.END)
            self.edit_unit.insert(0, values[2])
            self.edit_qty.delete(0, tk.END)
            self.edit_qty.insert(0, values[3])

    def update_product(self):
        try:
            prod_id = int(self.edit_id.get())
        except:
            messagebox.showerror("Ошибка", "Выберите товар")
            return
        new_name = self.edit_name.get().strip()
        new_unit = self.edit_unit.get().strip()
        if not new_name or not new_unit:
            messagebox.showwarning("Ошибка", "Название и единица измерения не могут быть пустыми")
            return
        if update_product(prod_id, new_name, new_unit):
            messagebox.showinfo("Успех", "Товар обновлён")
            self.load_products()
        else:
            messagebox.showerror("Ошибка", "Товар с таким названием уже существует")

    def set_quantity(self):
        try:
            prod_id = int(self.edit_id.get())
            new_qty = float(self.edit_qty.get())
            if new_qty < 0:
                raise ValueError
        except:
            messagebox.showerror("Ошибка", "Введите корректное положительное количество")
            return
        if set_stock_quantity(prod_id, new_qty):
            messagebox.showinfo("Успех", f"Количество товара установлено: {new_qty}")
            self.load_products()
        else:
            messagebox.showerror("Ошибка", "Не удалось обновить количество")

    def delete_product(self):
        try:
            prod_id = int(self.edit_id.get())
        except:
            messagebox.showerror("Ошибка", "Выберите товар")
            return
        if messagebox.askyesno("Подтверждение", f"Удалить товар? Все связанные операции будут потеряны."):
            if delete_product(prod_id):
                messagebox.showinfo("Успех", "Товар удалён")
                self.load_products()
                # Очистить поля
                self.edit_id.config(state='normal')
                self.edit_id.delete(0, tk.END)
                self.edit_id.config(state='readonly')
                self.edit_name.delete(0, tk.END)
                self.edit_unit.delete(0, tk.END)
                self.edit_qty.delete(0, tk.END)
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить товар")

    def add_product(self):
        name = self.new_name.get().strip()
        unit = self.new_unit.get().strip()
        if not name or not unit:
            messagebox.showwarning("Ошибка", "Заполните название и единицу измерения")
            return
        product_id = add_product(name, unit)
        if product_id:
            messagebox.showinfo("Успех", f"Товар '{name}' добавлен")
            self.new_name.delete(0, tk.END)
            self.new_unit.delete(0, tk.END)
            self.load_products()
        else:
            messagebox.showerror("Ошибка", "Товар с таким названием уже существует")