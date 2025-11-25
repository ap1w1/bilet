import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime


class TicketSale:
    """Класс, описывающий одну продажу билета."""

    def __init__(self, event_name, customer_name, phone, count, price, sale_datetime=None):
        self.event_name = event_name
        self.customer_name = customer_name
        self.phone = phone
        self.count = count
        self.price = price
        self.sale_datetime = sale_datetime or datetime.now()

    @property
    def total(self):
        return self.count * self.price

    def __str__(self):
        dt = self.sale_datetime.strftime("%d.%m.%Y %H:%M")
        return f"{dt} | {self.event_name} | {self.customer_name} | {self.count} шт. | {self.total:.2f} руб."


class AdminWindow(tk.Toplevel):
    """Окно администратора (отдельное от клиентского)."""

    def __init__(self, master, sales):
        super().__init__(master)
        self.sales = sales

        self.title("Панель администратора — продажи билетов")
        self.geometry("800x400")
        self.resizable(True, True)
        self.configure(bg="#222831")  # тёмная тема

        self._create_widgets()
        self.refresh()

    def _create_widgets(self):
        # Заголовок
        title = tk.Label(
            self,
            text="Сводка по продажам",
            font=("Segoe UI", 14, "bold"),
            bg="#222831",
            fg="#eeeeee",
            pady=10
        )
        title.pack(side=tk.TOP, fill=tk.X)

        # Рамка для таблицы
        table_frame = tk.Frame(self, bg="#222831", padx=10, pady=5)
        table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        columns = ("datetime", "event", "customer", "phone", "count", "price", "total")

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=10
        )

        # Заголовки
        self.tree.heading("datetime", text="Дата и время")
        self.tree.heading("event", text="Мероприятие")
        self.tree.heading("customer", text="Покупатель")
        self.tree.heading("phone", text="Телефон")
        self.tree.heading("count", text="Кол-во")
        self.tree.heading("price", text="Цена, руб.")
        self.tree.heading("total", text="Сумма, руб.")

        # Ширина столбцов
        self.tree.column("datetime", width=130, anchor="center")
        self.tree.column("event", width=170, anchor="w")
        self.tree.column("customer", width=140, anchor="w")
        self.tree.column("phone", width=110, anchor="center")
        self.tree.column("count", width=60, anchor="center")
        self.tree.column("price", width=80, anchor="e")
        self.tree.column("total", width=90, anchor="e")

        # Скроллбар
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        # Панель снизу — статистика + кнопки
        bottom_frame = tk.Frame(self, bg="#222831", padx=10, pady=10)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.label_stats = tk.Label(
            bottom_frame,
            text="Продаж: 0 | Билетов: 0 | Выручка: 0.00 руб.",
            font=("Segoe UI", 10, "bold"),
            bg="#222831",
            fg="#00adb5"
        )
        self.label_stats.pack(side=tk.LEFT)

        btn_refresh = ttk.Button(bottom_frame, text="Обновить", command=self.refresh)
        btn_refresh.pack(side=tk.RIGHT, padx=5)

    def refresh(self):
        """Обновить таблицу и статистику."""
        # Очистка таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)

        total_sales = len(self.sales)
        total_tickets = 0
        total_amount = 0.0

        for sale in self.sales:
            dt_str = sale.sale_datetime.strftime("%d.%m.%Y %H:%M")
            self.tree.insert(
                "",
                tk.END,
                values=(
                    dt_str,
                    sale.event_name,
                    sale.customer_name,
                    sale.phone,
                    sale.count,
                    f"{sale.price:.2f}",
                    f"{sale.total:.2f}"
                )
            )
            total_tickets += sale.count
            total_amount += sale.total

        self.label_stats.config(
            text=f"Продаж: {total_sales} | Билетов: {total_tickets} | Выручка: {total_amount:.2f} руб."
        )


class TicketApp(tk.Tk):
    """Основной класс приложения (окно клиента)."""

    ADMIN_PASSWORD = "admin" 

    def __init__(self):
        super().__init__()

        self.title("Продажа билетов на мероприятия — Клиент")
        self.geometry("780x480")
        self.resizable(False, False)
        self.configure(bg="#f4f6fb")

        # список всех продаж
        self.sales = []

        # ссылка на окно администратора
        self.admin_window = None

        # настраиваем стили ttk
        self._setup_styles()

        # создаём элементы интерфейса
        self._create_menu()
        self._create_widgets()

    def _setup_styles(self):
        style = ttk.Style(self)
        # Включаем тему (обычно 'clam' смотрится нормально)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))

    def _create_menu(self):
        menubar = tk.Menu(self)
        admin_menu = tk.Menu(menubar, tearoff=0)
        admin_menu.add_command(label="Открыть панель администратора", command=self.open_admin_panel)
        menubar.add_cascade(label="Администратор", menu=admin_menu)

        self.config(menu=menubar)

    def _create_widgets(self):
        default_font = ("Segoe UI", 10)

        # Верхняя панель с заголовком
        header_frame = tk.Frame(self, bg="#283593", padx=10, pady=10)
        header_frame.pack(side=tk.TOP, fill=tk.X)

        lbl_title = tk.Label(
            header_frame,
            text="Продажа билетов на мероприятия",
            font=("Segoe UI", 14, "bold"),
            fg="white",
            bg="#283593"
        )
        lbl_title.pack(side=tk.LEFT)

        lbl_sub = tk.Label(
            header_frame,
            text="Клиентское окно",
            font=("Segoe UI", 10),
            fg="#c5cae9",
            bg="#283593"
        )
        lbl_sub.pack(side=tk.LEFT, padx=10)

        # Основной фрейм
        main_frame = tk.Frame(self, bg="#f4f6fb", padx=10, pady=10)
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Левая часть — форма
        form_card = tk.LabelFrame(
            main_frame,
            text=" Оформление продажи ",
            font=("Segoe UI", 10, "bold"),
            bg="#f4f6fb",
            padx=10,
            pady=10
        )
        form_card.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Мероприятие
        tk.Label(form_card, text="Мероприятие:", font=default_font, bg="#f4f6fb").grid(
            row=0, column=0, sticky="e", pady=3
        )
        self.entry_event = ttk.Entry(form_card, width=30)
        self.entry_event.grid(row=0, column=1, padx=5, pady=3, sticky="w")
        self.entry_event.insert(0, "Концерт группы X")

        # ФИО покупателя
        tk.Label(form_card, text="ФИО покупателя:", font=default_font, bg="#f4f6fb").grid(
            row=1, column=0, sticky="e", pady=3
        )
        self.entry_customer = ttk.Entry(form_card, width=30)
        self.entry_customer.grid(row=1, column=1, padx=5, pady=3, sticky="w")

        # Телефон
        tk.Label(form_card, text="Телефон:", font=default_font, bg="#f4f6fb").grid(
            row=2, column=0, sticky="e", pady=3
        )
        self.entry_phone = ttk.Entry(form_card, width=20)
        self.entry_phone.grid(row=2, column=1, padx=5, pady=3, sticky="w")

        # Количество билетов
        tk.Label(form_card, text="Кол-во билетов:", font=default_font, bg="#f4f6fb").grid(
            row=3, column=0, sticky="e", pady=3
        )
        self.entry_count = ttk.Entry(form_card, width=8)
        self.entry_count.grid(row=3, column=1, padx=5, pady=3, sticky="w")
        self.entry_count.insert(0, "1")

        # Цена за билет
        tk.Label(form_card, text="Цена за билет, руб.:", font=default_font, bg="#f4f6fb").grid(
            row=4, column=0, sticky="e", pady=3
        )
        self.entry_price = ttk.Entry(form_card, width=8)
        self.entry_price.grid(row=4, column=1, padx=5, pady=3, sticky="w")
        self.entry_price.insert(0, "1000")

        # Итоговая сумма
        tk.Label(form_card, text="Итоговая сумма:", font=default_font, bg="#f4f6fb").grid(
            row=5, column=0, sticky="e", pady=(10, 3)
        )
        self.label_total = tk.Label(
            form_card,
            text="0 руб.",
            font=("Segoe UI", 11, "bold"),
            fg="#1b5e20",
            bg="#f4f6fb"
        )
        self.label_total.grid(row=5, column=1, sticky="w", pady=(10, 3))

        # Кнопки
        btn_frame = tk.Frame(form_card, bg="#f4f6fb")
        btn_frame.grid(row=6, column=0, columnspan=2, pady=(10, 0), sticky="w")

        self.button_calc = ttk.Button(
            btn_frame,
            text="Рассчитать сумму",
            style="TButton",
            command=self.calculate_total
        )
        self.button_calc.pack(side=tk.LEFT, padx=(0, 5))

        self.button_sell = ttk.Button(
            btn_frame,
            text="Продать билет",
            style="Accent.TButton",
            command=self.sell_ticket
        )
        self.button_sell.pack(side=tk.LEFT, padx=(5, 0))

        # Правая часть — список оформленных продаж
        list_card = tk.LabelFrame(
            main_frame,
            text=" Последние оформленные продажи ",
            font=("Segoe UI", 10, "bold"),
            bg="#f4f6fb",
            padx=5,
            pady=5
        )
        list_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.listbox_sales = tk.Listbox(
            list_card,
            font=default_font,
            bg="white",
            activestyle="none"
        )
        self.listbox_sales.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_card, orient=tk.VERTICAL, command=self.listbox_sales.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox_sales.config(yscrollcommand=scrollbar.set)

    def calculate_total(self):
        """Расчет итоговой суммы без записи продажи."""
        try:
            count = int(self.entry_count.get())
            price = float(self.entry_price.get().replace(",", "."))
            if count <= 0 or price <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Ошибка ввода", "Количество и цена должны быть положительными числами.")
            return

        total = count * price
        self.label_total.config(text=f"{total:.2f} руб.")

    def sell_ticket(self):
        """Оформление продажи билета (клиентское окно)."""
        event_name = self.entry_event.get().strip()
        customer_name = self.entry_customer.get().strip()
        phone = self.entry_phone.get().strip()

        if not event_name or not customer_name or not phone:
            messagebox.showwarning("Ошибка ввода", "Заполните все поля: мероприятие, ФИО, телефон.")
            return

        try:
            count = int(self.entry_count.get())
            price = float(self.entry_price.get().replace(",", "."))
            if count <= 0 or price <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Ошибка ввода", "Количество и цена должны быть положительными числами.")
            return

        sale = TicketSale(event_name, customer_name, phone, count, price)
        self.sales.append(sale)

        # добавляем строку в список на форме
        self.listbox_sales.insert(tk.END, str(sale))

        # обновляем текст итоговой суммы и очищаем некоторые поля
        self.label_total.config(text=f"{sale.total:.2f} руб.")
        self.entry_customer.delete(0, tk.END)
        self.entry_phone.delete(0, tk.END)

        # если окно админа открыто — обновить
        if self.admin_window is not None and self.admin_window.winfo_exists():
            self.admin_window.refresh()

        messagebox.showinfo("Успех", "Продажа успешно оформлена!")

    def open_admin_panel(self):
        """Открытие отдельного окна администратора с паролем."""
        # если уже открыто — просто фокус
        if self.admin_window is not None and self.admin_window.winfo_exists():
            self.admin_window.focus()
            return

        password = simpledialog.askstring(
            "Вход администратора",
            "Введите пароль:",
            show="*",
            parent=self
        )
        if password != self.ADMIN_PASSWORD:
            if password is not None:  # если не нажали Cancel
                messagebox.showerror("Ошибка", "Неверный пароль администратора!")
            return

        # создаём окно администратора
        self.admin_window = AdminWindow(self, self.sales)


if __name__ == "__main__":
    app = TicketApp()
    app.mainloop()
