import tkinter as tk
from tkinter import ttk
from database import get_stock
from datetime import datetime

class ReportWindow:
    def __init__(self, parent):
        self.win = tk.Toplevel(parent)
        self.win.title("Отчёт по остаткам")
        self.win.geometry("650x450")
        self.win.grab_set()

        # Фон градиент
        canvas = tk.Canvas(self.win, width=650, height=450, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        for i in range(450):
            color = f'#{"%02x"%int(0xe8 + (0xee-0xe8)*(i/450))}{"%02x"%int(0xf0 + (0xf4-0xf0)*(i/450))}{"%02x"%int(0xf8 + (0xfc-0xf8)*(i/450))}'
            canvas.create_line(0, i, 650, i, fill=color)

        frame = tk.Frame(self.win, bg='#f4f8fc')
        frame.place(relx=0.5, rely=0.5, anchor="center", width=600, height=400)

        # Заголовок
        report_date = datetime.now().strftime("%d.%m.%Y %H:%M")
        tk.Label(frame, text=f"Отчёт по остаткам на {report_date}",
                 font=('Arial', 13, 'bold'), bg='#f4f8fc', fg='#003366').pack(pady=15)

        # Таблица
        tree_frame = tk.Frame(frame, bg='#f4f8fc')
        tree_frame.pack(expand=True, fill='both', padx=15, pady=10)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Report.Treeview', font=('Arial', 10), rowheight=25)
        style.configure('Report.Treeview.Heading', font=('Arial', 10, 'bold'))

        columns = ('name', 'unit', 'qty')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                                 style='Report.Treeview', height=12)
        self.tree.heading('name', text='Наименование')
        self.tree.heading('unit', text='Ед. изм.')
        self.tree.heading('qty', text='Остаток')
        self.tree.column('name', width=300)
        self.tree.column('unit', width=100, anchor='center')
        self.tree.column('qty', width=100, anchor='center')
        self.tree.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        self.load_data()

        tk.Button(frame, text="Закрыть", font=('Arial', 10, 'bold'),
                  bg='#2a6cb6', fg='white', activebackground='#4a90d9',
                  relief='flat', bd=0, padx=20, pady=8, cursor='hand2',
                  command=self.win.destroy).pack(pady=15)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = get_stock()
        for r in rows:
            self.tree.insert('', 'end', values=(r['name'], r['unit'], r['qty']))