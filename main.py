import tkinter as tk
from database import init_db
from auth import AuthWindow
from widgets import ModernButton
from stock_operations import ReceiptWindow, SaleWindow
from report import ReportWindow

class MainMenu:
    def __init__(self, user):
        self.user = user
        self.root = tk.Tk()
        self.root.title("Складской учёт – Главное меню")
        self.root.geometry("550x450")
        self.root.resizable(False, False)

        # Градиентный фон
        canvas = tk.Canvas(self.root, width=550, height=450, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        for i in range(450):
            color = f'#{"%02x"%int(0x2a + (0x4a-0x2a)*(i/450))}{"%02x"%int(0x6c + (0x90-0x6c)*(i/450))}{"%02x"%int(0xb6 + (0xd9-0xb6)*(i/450))}'
            canvas.create_line(0, i, 550, i, fill=color)

        frame = tk.Frame(self.root, bg='#f0f4fa')
        frame.place(relx=0.5, rely=0.5, anchor="center", width=450, height=420)  # чуть выше, чтобы поместилась кнопка

        tk.Label(frame, text="Складской учёт", font=('Arial', 20, 'bold'),
                 bg='#f0f4fa', fg='#003366').pack(pady=(30, 5))
        tk.Label(frame, text=f"Пользователь: {user['login']}",
                 font=('Arial', 9), bg='#f0f4fa', fg='#666').pack()

        btn_frame = tk.Frame(frame, bg='#f0f4fa')
        btn_frame.pack(expand=True, pady=20)

        btn_receipt = ModernButton(btn_frame, text="📦  Поступление товара",
                                   command=self.open_receipt,
                                   width=260, height=45)
        btn_receipt.pack(pady=8)

        btn_sale = ModernButton(btn_frame, text="💰  Продажа товара",
                                command=self.open_sale,
                                width=260, height=45)
        btn_sale.pack(pady=8)

        # Если пользователь admin – добавить кнопку управления товарами
        if user.get('role') == 'admin':
            btn_manage = ModernButton(btn_frame, text="⚙️  Управление товарами",
                                      command=self.open_manage_products,
                                      width=260, height=45,
                                      bg="#6c757d", bg_hover="#5a6268")
            btn_manage.pack(pady=8)

        btn_report = ModernButton(btn_frame, text="📊  Отчёт по остаткам",
                                  command=self.open_report,
                                  width=260, height=45)
        btn_report.pack(pady=8)

        btn_exit = ModernButton(btn_frame, text="🚪  Выход",
                                command=self.root.destroy,
                                width=260, height=45,
                                bg="#dc3545", bg_hover="#c82333")
        btn_exit.pack(pady=8)

        self.root.mainloop()

    def open_receipt(self):
        ReceiptWindow(self.root, self.user)

    def open_sale(self):
        SaleWindow(self.root, self.user)

    def open_report(self):
        ReportWindow(self.root)

    def open_manage_products(self):
        from admin_products import ManageProductsWindow
        ManageProductsWindow(self.root)


if __name__ == "__main__":
    init_db()
    def start_main(user):
        MainMenu(user)
    AuthWindow(on_success=start_main)