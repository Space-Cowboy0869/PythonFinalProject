from datetime import datetime, timedelta, time
import csv

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QMessageBox,
    QDateEdit,
    QFileDialog,
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QIcon
from sqlalchemy import func, desc

from ...database import db_session
from ...models import Product, Transaction, TransactionItem
from ...utils.helpers import format_currency, get_icon_path, load_icon


class ReportsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.current_user = None
        self._build_ui()
        self._set_default_dates()

    def set_user(self, user):
        self.current_user = user
        self._apply_permissions()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Reports")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        self.unauthorized_label = QLabel("Not authorized")
        self.unauthorized_label.setStyleSheet("color: #00b050; font-weight: bold;")
        self.unauthorized_label.setVisible(False)
        layout.addWidget(self.unauthorized_label)

        controls = QHBoxLayout()
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setIcon(load_icon("refresh.png"))
        self.refresh_btn.clicked.connect(self.refresh)

        self.export_btn = QPushButton("Export")
        self.export_btn.setIcon(load_icon("export.png"))
        self.export_btn.clicked.connect(self.export_report)

        controls.addWidget(QLabel("From:"))
        controls.addWidget(self.from_date)
        controls.addWidget(QLabel("To:"))
        controls.addWidget(self.to_date)
        controls.addStretch()
        controls.addWidget(self.refresh_btn)
        controls.addWidget(self.export_btn)
        layout.addLayout(controls)

        metrics = QHBoxLayout()
        self.total_sales_label = QLabel("Total Sales: $0.00")
        self.total_orders_label = QLabel("Orders: 0")
        self.avg_order_label = QLabel("Avg Order: $0.00")
        self.total_profit_label = QLabel("Profit: $0.00")
        for w in (self.total_sales_label, self.total_orders_label, self.avg_order_label, self.total_profit_label):
            w.setStyleSheet("font-size: 16px; font-weight: bold;")
            metrics.addWidget(w)
        metrics.addStretch()
        layout.addLayout(metrics)

        tables_row = QHBoxLayout()

        # Sales by day
        left = QVBoxLayout()
        left.addWidget(QLabel("Sales by Day"))
        self.sales_by_day = QTableWidget()
        self.sales_by_day.setColumnCount(4)
        self.sales_by_day.setHorizontalHeaderLabels(["Date", "Sales", "Cost", "Profit"])
        self.sales_by_day.verticalHeader().setVisible(False)
        self.sales_by_day.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.sales_by_day.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.sales_by_day.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.sales_by_day.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.sales_by_day.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.sales_by_day.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.sales_by_day.setAlternatingRowColors(True)
        left.addWidget(self.sales_by_day, 1)

        # Top products
        mid = QVBoxLayout()
        mid.addWidget(QLabel("Top Products"))
        self.top_products = QTableWidget()
        self.top_products.setColumnCount(5)
        self.top_products.setHorizontalHeaderLabels(["Product", "Qty", "Sales", "Cost", "Profit"])
        self.top_products.verticalHeader().setVisible(False)
        self.top_products.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.top_products.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.top_products.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.top_products.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.top_products.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.top_products.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.top_products.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.top_products.setAlternatingRowColors(True)
        mid.addWidget(self.top_products, 1)

        # Low stock
        right = QVBoxLayout()
        right.addWidget(QLabel("Low Stock"))
        self.low_stock = QTableWidget()
        self.low_stock.setColumnCount(2)
        self.low_stock.setHorizontalHeaderLabels(["Product", "Stock"])
        self.low_stock.verticalHeader().setVisible(False)
        self.low_stock.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.low_stock.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.low_stock.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.low_stock.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.low_stock.setAlternatingRowColors(True)
        right.addWidget(self.low_stock, 1)

        tables_row.addLayout(left, 2)
        tables_row.addSpacing(12)
        tables_row.addLayout(mid, 2)
        tables_row.addSpacing(12)
        tables_row.addLayout(right, 1)

        layout.addLayout(tables_row, 1)

    def _apply_permissions(self):
        is_admin = bool(self.current_user and getattr(self.current_user, 'role', None) == 'admin')
        self.unauthorized_label.setVisible(not is_admin)
        self.from_date.setEnabled(is_admin)
        self.to_date.setEnabled(is_admin)
        self.refresh_btn.setEnabled(is_admin)
        self.export_btn.setEnabled(is_admin)
        self.sales_by_day.setEnabled(is_admin)
        self.top_products.setEnabled(is_admin)
        self.low_stock.setEnabled(is_admin)

    def _set_default_dates(self):
        today = QDate.currentDate()
        self.to_date.setDate(today)
        self.from_date.setDate(today.addDays(-30))

    def refresh(self):
        if not (self.current_user and getattr(self.current_user, 'role', None) == 'admin'):
            return

        try:
            start = self.from_date.date().toPyDate()
            end = self.to_date.date().toPyDate()
            start_dt = datetime.combine(start, time.min)
            end_dt = datetime.combine(end, time.min) + timedelta(days=1)

            totals_row = (
                db_session.query(
                    func.sum(TransactionItem.qty * TransactionItem.price).label('sales'),
                    func.sum(TransactionItem.qty * TransactionItem.cost_price).label('cost'),
                )
                .join(Transaction, Transaction.id == TransactionItem.transaction_id)
                .filter(Transaction.created_at >= start_dt, Transaction.created_at < end_dt)
                .one()
            )

            total_sales = float(totals_row.sales or 0)
            total_cost = float(totals_row.cost or 0)
            total_profit = total_sales - total_cost
            total_orders = (
                db_session.query(func.count(Transaction.id))
                .filter(Transaction.created_at >= start_dt, Transaction.created_at < end_dt)
                .scalar()
                or 0
            )
            avg_order = float(total_sales) / float(total_orders) if total_orders else 0

            self.total_sales_label.setText(f"Total Sales: {format_currency(total_sales)}")
            self.total_orders_label.setText(f"Orders: {total_orders}")
            self.avg_order_label.setText(f"Avg Order: {format_currency(avg_order)}")
            self.total_profit_label.setText(f"Profit: {format_currency(total_profit)}")

            # Sales by day
            by_day = (
                db_session.query(
                    func.date(Transaction.created_at).label('d'),
                    func.sum(TransactionItem.qty * TransactionItem.price).label('sales'),
                    func.sum(TransactionItem.qty * TransactionItem.cost_price).label('cost'),
                )
                .join(TransactionItem, TransactionItem.transaction_id == Transaction.id)
                .filter(Transaction.created_at >= start_dt, Transaction.created_at < end_dt)
                .group_by(func.date(Transaction.created_at))
                .order_by(func.date(Transaction.created_at))
                .all()
            )
            self.sales_by_day.setRowCount(len(by_day))
            for row, r in enumerate(by_day):
                sales = float(r.sales or 0)
                cost = float(r.cost or 0)
                profit = sales - cost
                self.sales_by_day.setItem(row, 0, QTableWidgetItem(str(r.d)))
                self.sales_by_day.setItem(row, 1, QTableWidgetItem(format_currency(sales)))
                self.sales_by_day.setItem(row, 2, QTableWidgetItem(format_currency(cost)))
                self.sales_by_day.setItem(row, 3, QTableWidgetItem(format_currency(profit)))
            self.sales_by_day.resizeRowsToContents()

            # Top products
            top = (
                db_session.query(
                    Product.name,
                    func.sum(TransactionItem.qty).label('qty'),
                    func.sum(TransactionItem.qty * TransactionItem.price).label('sales'),
                    func.sum(TransactionItem.qty * TransactionItem.cost_price).label('cost'),
                )
                .join(TransactionItem, TransactionItem.product_id == Product.id)
                .join(Transaction, Transaction.id == TransactionItem.transaction_id)
                .filter(Transaction.created_at >= start_dt, Transaction.created_at < end_dt)
                .group_by(Product.id, Product.name)
                .order_by(desc(func.sum(TransactionItem.qty)))
                .limit(15)
                .all()
            )
            self.top_products.setRowCount(len(top))
            for row, r in enumerate(top):
                sales = float(r.sales or 0)
                cost = float(r.cost or 0)
                profit = sales - cost
                self.top_products.setItem(row, 0, QTableWidgetItem(r.name or ""))
                self.top_products.setItem(row, 1, QTableWidgetItem(str(int(r.qty or 0))))
                self.top_products.setItem(row, 2, QTableWidgetItem(format_currency(sales)))
                self.top_products.setItem(row, 3, QTableWidgetItem(format_currency(cost)))
                self.top_products.setItem(row, 4, QTableWidgetItem(format_currency(profit)))
            self.top_products.resizeRowsToContents()

            # Low stock
            low = (
                db_session.query(Product)
                .filter(Product.is_service == False)
                .order_by(Product.stock.asc())
                .limit(25)
                .all()
            )
            low = [p for p in low if int(p.stock or 0) <= 10]
            self.low_stock.setRowCount(len(low))
            for row, p in enumerate(low):
                self.low_stock.setItem(row, 0, QTableWidgetItem(p.name))
                self.low_stock.setItem(row, 1, QTableWidgetItem(str(p.stock)))
            self.low_stock.resizeRowsToContents()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def export_report(self):
        if not (self.current_user and getattr(self.current_user, 'role', None) == 'admin'):
            return

        try:
            start = self.from_date.date().toPyDate()
            end = self.to_date.date().toPyDate()
            start_dt = datetime.combine(start, time.min)
            end_dt = datetime.combine(end, time.min) + timedelta(days=1)

            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Export Sales Report",
                "",
                "CSV Files (*.csv);;All Files (*)",
            )
            if not filename:
                return

            rows = (
                db_session.query(
                    Product.sku,
                    Product.name,
                    func.sum(TransactionItem.qty).label('qty'),
                    func.sum(TransactionItem.qty * TransactionItem.price).label('sales'),
                    func.sum(TransactionItem.qty * TransactionItem.cost_price).label('cost'),
                )
                .join(TransactionItem, TransactionItem.product_id == Product.id)
                .join(Transaction, Transaction.id == TransactionItem.transaction_id)
                .filter(Transaction.created_at >= start_dt, Transaction.created_at < end_dt)
                .group_by(Product.id, Product.sku, Product.name)
                .order_by(Product.name)
                .all()
            )

            if not rows:
                QMessageBox.information(self, "Export Sales Report", "No sales found for the selected period.")
                return

            if not filename.lower().endswith(".csv"):
                filename += ".csv"

            total_sales = 0.0
            total_cost = 0.0

            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["SKU", "Product", "Quantity", "Sales", "Cost", "Profit", "Margin %"])

                for r in rows:
                    sales = float(r.sales or 0)
                    cost = float(r.cost or 0)
                    profit = sales - cost
                    margin = (profit / sales * 100.0) if sales else 0.0

                    total_sales += sales
                    total_cost += cost

                    writer.writerow([
                        r.sku or "",
                        r.name or "",
                        int(r.qty or 0),
                        f"{sales:.2f}",
                        f"{cost:.2f}",
                        f"{profit:.2f}",
                        f"{margin:.2f}",
                    ])

                total_profit = total_sales - total_cost
                writer.writerow([])
                writer.writerow([
                    "TOTAL",
                    "",
                    "",
                    f"{total_sales:.2f}",
                    f"{total_cost:.2f}",
                    f"{total_profit:.2f}",
                    "",
                ])

            QMessageBox.information(self, "Export Sales Report", "Sales report exported successfully.")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
