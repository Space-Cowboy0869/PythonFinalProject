from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTabWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from sqlalchemy import func, desc

from ...controllers import db_session
from ...models import Transaction
from ...utils.helpers import format_currency, load_icon
from ..dialogs.receipt_dialog import ReceiptDialog
from ..widgets import ModernTable, SearchBar, ActionButton, SectionHeader, IconButton


class CustomersScreen(QWidget):
    """Customers and transactions screen with modern design."""
    
    def __init__(self):
        super().__init__()
        self.current_user = None
        self._build_ui()
        self.refresh_all()

    def set_user(self, user):
        self.current_user = user

    def _build_ui(self):
        """Set up the UI with modern design."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QHBoxLayout()
        title = QLabel("Customers & Transactions")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #00b050;")
        header.addWidget(title)
        header.addStretch()

        refresh_btn = ActionButton("Refresh", "refresh.png", "#000000")
        refresh_btn.clicked.connect(self.refresh_all)
        header.addWidget(refresh_btn)

        layout.addLayout(header)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                background-color: #f5f5f5;
                color: #333333;
                padding: 8px 16px;
                border: none;
                border-bottom: 2px solid transparent;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #00b050;
            }
        """)
        layout.addWidget(self.tabs, 1)

        # === Customers Tab ===
        customers_tab = QWidget()
        customers_layout = QVBoxLayout(customers_tab)
        customers_layout.setContentsMargins(0, 15, 0, 0)
        customers_layout.setSpacing(12)

        customers_header = SectionHeader("Customers")
        customers_layout.addWidget(customers_header)

        self.customer_search = SearchBar("Search by name or phone...")
        self.customer_search.textChanged.connect(self.refresh_customers)
        customers_layout.addWidget(self.customer_search)

        self.customers_table = ModernTable()
        self.customers_table.setColumnCount(4)
        self.customers_table.setHorizontalHeaderLabels(["Name", "Phone", "Orders", "Total Spent"])
        
        header = self.customers_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        customers_layout.addWidget(self.customers_table, 1)
        self.tabs.addTab(customers_tab, "Customers")

        # === Transactions Tab ===
        tx_tab = QWidget()
        tx_layout = QVBoxLayout(tx_tab)
        tx_layout.setContentsMargins(0, 15, 0, 0)
        tx_layout.setSpacing(12)

        tx_header = SectionHeader("Transaction History")
        tx_layout.addWidget(tx_header)

        self.tx_search = SearchBar("Search by receipt #, customer, or phone...")
        self.tx_search.textChanged.connect(self.refresh_transactions)
        tx_layout.addWidget(self.tx_search)

        self.tx_table = ModernTable()
        self.tx_table.setColumnCount(7)
        self.tx_table.setHorizontalHeaderLabels(["ID", "Date", "Customer", "Phone", "Total", "Payment", ""])
        
        header = self.tx_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        self.tx_table.cellDoubleClicked.connect(self._open_selected_receipt)
        tx_layout.addWidget(self.tx_table, 1)
        self.tabs.addTab(tx_tab, "Transactions")

    def refresh_all(self):
        self.refresh_customers()
        self.refresh_transactions()

    def refresh_customers(self, *_):
        search = (self.customer_search.text() or "").strip().lower()
        try:
            q = (
                db_session.query(
                    Transaction.customer_name,
                    Transaction.customer_phone,
                    func.count(Transaction.id).label("orders"),
                    func.sum(Transaction.total).label("spent"),
                )
                .filter(Transaction.customer_name.isnot(None))
                .filter(Transaction.customer_name != "")
                .group_by(Transaction.customer_name, Transaction.customer_phone)
                .order_by(desc(func.sum(Transaction.total)))
            )

            rows = q.all()
            if search:
                rows = [
                    r
                    for r in rows
                    if search in (r.customer_name or "").lower()
                    or search in (r.customer_phone or "").lower()
                ]

            self.customers_table.setRowCount(len(rows))
            for i, r in enumerate(rows):
                self.customers_table.setItem(i, 0, QTableWidgetItem(r.customer_name or ""))
                self.customers_table.setItem(i, 1, QTableWidgetItem(r.customer_phone or ""))
                self.customers_table.setItem(i, 2, QTableWidgetItem(str(r.orders or 0)))
                self.customers_table.setItem(i, 3, QTableWidgetItem(format_currency(r.spent or 0)))

            self.customers_table.resizeRowsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def refresh_transactions(self, *_):
        search = (self.tx_search.text() or "").strip().lower()
        try:
            txs = (
                db_session.query(Transaction)
                .order_by(Transaction.created_at.desc())
                .limit(200)
                .all()
            )

            if search:
                filtered = []
                for t in txs:
                    hay = " ".join(
                        [
                            str(t.id),
                            (t.customer_name or ""),
                            (t.customer_phone or ""),
                            (t.payment_method or ""),
                        ]
                    ).lower()
                    if search in hay:
                        filtered.append(t)
                txs = filtered

            self.tx_table.setRowCount(len(txs))
            for row, t in enumerate(txs):
                self.tx_table.setItem(row, 0, QTableWidgetItem(str(t.id)))
                self.tx_table.setItem(row, 1, QTableWidgetItem(t.created_at.strftime('%Y-%m-%d %H:%M')))
                self.tx_table.setItem(row, 2, QTableWidgetItem(t.customer_name or ""))
                self.tx_table.setItem(row, 3, QTableWidgetItem(t.customer_phone or ""))
                self.tx_table.setItem(row, 4, QTableWidgetItem(format_currency(t.total)))
                self.tx_table.setItem(row, 5, QTableWidgetItem(t.payment_method or ""))

                btn = IconButton("receipt.png", "View receipt", 32)
                btn.clicked.connect(lambda _, tid=t.id: self.open_receipt(tid))
                self.tx_table.setCellWidget(row, 6, btn)

            self.tx_table.resizeRowsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def open_receipt(self, transaction_id: int):
        ReceiptDialog(transaction_id, self).exec()

    def _open_selected_receipt(self, row, col):
        try:
            tid = int(self.tx_table.item(row, 0).text())
        except Exception:
            return
        self.open_receipt(tid)
