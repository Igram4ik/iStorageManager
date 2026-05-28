import tkinter as tk
from tkinter import ttk, messagebox
from database import get_products, get_stock, add_transaction
from widgets import ModernButton   # импорт из widgets

class ReceiptWindow:
    def __init__(self, parent, user):
        self.user = user
        self.win = tk.Toplevel(parent)
        self.win.title("Поступление товара")
        self.win.geometry("450x320")
        self.win.resizable(False, False)
        self.win.grab_set()

        # Градиентный фон
        canvas = tk.Canvas(self.win, width=450, height=320, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        for i in range(320):
            color = f'#{"%02x"%int(0xe8 + (0xee-0xe8)*(i/320))}{"%02x"%int(0xf0 + (0xf4-0xf0)*(i/320))}{"%02x"%int(0xf8 + (0xfc-0xf8)*(i/320))}'
            canvas.create_line(0, i, 450, i, fill=color)

        frame = tk.Frame(self.win, bg='#f4f8fc')
        frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=270)

        tk.Label(frame, text="Поступление товара", font=('Arial', 14, 'bold'),
                 bg='#f4f8fc', fg='#003366').pack(pady=(15,10))

        tk.Label(frame, text="Товар", bg='#f4f8fc').pack(anchor='w', padx=20)
        self.product_var = tk.StringVar()
        self.products = get_products()
        self.product_choices = [f"{p['name']} ({p['unit']})" for p in self.products]
        self.product_cb = ttk.Combobox(frame, textvariable=self.product_var,
                                       values=self.product_choices, state='readonly',
                                       font=('Arial', 10), width=35)
        self.product_cb.pack(padx=20, pady=(0,10), ipady=2)
        if self.product_choices:
            self.product_cb.current(0)

        tk.Label(frame, text="Количество", bg='#f4f8fc').pack(anchor='w', padx=20)
        self.qty_var = tk.StringVar()
        self.qty_entry = tk.Entry(frame, textvariable=self.qty_var, font=('Arial', 11),
                                  relief='flat', bd=2, bg='white')
        self.qty_entry.pack(padx=20, pady=(0,15), ipady=3, fill='x')

        btn = ModernButton(frame, text="Оприходовать", command=self.do_receipt,
                           width=180, height=35)
        btn.pack(pady=5)

    def do_receipt(self):
        sel = self.product_cb.current()
        if sel < 0:
            messagebox.showwarning("Ошибка", "Выберите товар")
            return
        product_id = self.products[sel]['id']
        try:
            qty = float(self.qty_var.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Ошибка", "Введите положительное число")
            return
        if add_transaction('IN', product_id, qty, self.user['id']):
            messagebox.showinfo("Успех", "Товар оприходован")
            self.win.destroy()
        else:
            messagebox.showerror("Ошибка", "Не удалось выполнить операцию")

class SaleWindow:
    def __init__(self, parent, user):
        self.user = user
        self.win = tk.Toplevel(parent)
        self.win.title("Продажа товара")
        self.win.geometry("450x370")
        self.win.resizable(False, False)
        self.win.grab_set()

        canvas = tk.Canvas(self.win, width=450, height=370, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        for i in range(370):
            color = f'#{"%02x"%int(0xe8 + (0xee-0xe8)*(i/370))}{"%02x"%int(0xf0 + (0xf4-0xf0)*(i/370))}{"%02x"%int(0xf8 + (0xfc-0xf8)*(i/370))}'
            canvas.create_line(0, i, 450, i, fill=color)

        frame = tk.Frame(self.win, bg='#f4f8fc')
        frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=320)

        tk.Label(frame, text="Продажа товара", font=('Arial', 14, 'bold'),
                 bg='#f4f8fc', fg='#003366').pack(pady=(15,10))

        tk.Label(frame, text="Товар", bg='#f4f8fc').pack(anchor='w', padx=20)
        self.product_var = tk.StringVar()
        self.products = get_products()
        self.product_choices = [f"{p['name']} ({p['unit']})" for p in self.products]
        self.product_cb = ttk.Combobox(frame, textvariable=self.product_var,
                                       values=self.product_choices, state='readonly',
                                       font=('Arial', 10), width=35)
        self.product_cb.pack(padx=20, pady=(0,10), ipady=2)
        if self.product_choices:
            self.product_cb.current(0)

        tk.Label(frame, text="Остаток на складе:", bg='#f4f8fc').pack(anchor='w', padx=20)
        self.stock_label = tk.Label(frame, text="0", font=('Arial', 11, 'bold'),
                                    bg='#f4f8fc', fg='#cc0000')
        self.stock_label.pack(anchor='w', padx=20, pady=(0,10))
        self.product_cb.bind('<<ComboboxSelected>>', self.update_stock)

        tk.Label(frame, text="Количество", bg='#f4f8fc').pack(anchor='w', padx=20)
        self.qty_var = tk.StringVar()
        self.qty_entry = tk.Entry(frame, textvariable=self.qty_var, font=('Arial', 11),
                                  relief='flat', bd=2, bg='white')
        self.qty_entry.pack(padx=20, pady=(0,15), ipady=3, fill='x')

        btn = ModernButton(frame, text="Продать", command=self.do_sale,
                           width=180, height=35)
        btn.pack(pady=5)

        self.update_stock()

    def update_stock(self, event=None):
        sel = self.product_cb.current()
        if sel >= 0:
            pid = self.products[sel]['id']
            stock = get_stock(pid)
            self.stock_label.config(text=str(stock))
        else:
            self.stock_label.config(text="0")

    def do_sale(self):
        sel = self.product_cb.current()
        if sel < 0:
            messagebox.showwarning("Ошибка", "Выберите товар")
            return
        product_id = self.products[sel]['id']
        try:
            qty = float(self.qty_var.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Ошибка", "Введите положительное число")
            return
        current_stock = get_stock(product_id)
        if qty > current_stock:
            messagebox.showwarning("Ошибка", "Недостаточно товара на складе")
            return
        if add_transaction('OUT', product_id, qty, self.user['id']):
            messagebox.showinfo("Успех", "Продажа оформлена")
            self.win.destroy()
        else:
            messagebox.showerror("Ошибка", "Не удалось выполнить операцию")