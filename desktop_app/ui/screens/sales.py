from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QMessageBox,
    QSpinBox,
    QDialog,
    QDialogButtonBox,
    QInputDialog,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
from sqlalchemy import func
import os
from decimal import Decimal

from ...database import db_session
from ...models import Category, Product, Transaction, TransactionItem, StockChange
from ...utils.helpers import (
    format_currency,
    get_icon_path,
    uploads_path,
    load_icon,
    compute_ph_vat_breakdown,
    PH_VAT_RATE,
)
from ..dialogs.receipt_dialog import ReceiptDialog


class SalesScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.cart = {}
        self._build_ui()
        self._load_categories()
        self._load_products()
        self._update_totals()

    def set_user(self, user):
        self.current_user = user

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Sales (POS)")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()

        self.new_sale_btn = QPushButton("New Sale")
        self.new_sale_btn.setIcon(load_icon("new_sale.png"))
        self.new_sale_btn.clicked.connect(self.new_sale)
        header.addWidget(self.new_sale_btn)

        layout.addLayout(header)

        filter_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products (name or SKU)...")
        self.search_input.textChanged.connect(self._load_products)

        self.category_filter = QComboBox()
        self.category_filter.currentIndexChanged.connect(self._load_products)

        filter_row.addWidget(QLabel("Search:"))
        filter_row.addWidget(self.search_input, 1)
        filter_row.addWidget(QLabel("Category:"))
        filter_row.addWidget(self.category_filter)
        layout.addLayout(filter_row)

        tables_row = QHBoxLayout()

        left = QVBoxLayout()
        products_label = QLabel("Products")
        products_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        left.addWidget(products_label)
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(6)
        self.products_table.setHorizontalHeaderLabels(["ID", "Name", "Type", "Price", "Stock", "Add"])
        self.products_table.verticalHeader().setVisible(False)
        self.products_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.products_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.products_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.products_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.products_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.products_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.products_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.products_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.products_table.setAlternatingRowColors(True)
        self.products_table.cellDoubleClicked.connect(self._add_selected_product)
        left.addWidget(self.products_table, 1)

        right = QVBoxLayout()
        cart_label = QLabel("Cart")
        cart_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        right.addWidget(cart_label)
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(["Product", "Price", "Qty", "Total", "Remove"])
        self.cart_table.verticalHeader().setVisible(False)
        self.cart_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.cart_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.cart_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.cart_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.cart_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.cart_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.cart_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.cart_table.setAlternatingRowColors(True)
        right.addWidget(self.cart_table, 1)

        self.vatable_sales_label = QLabel("VATable Sales: $0.00")
        self.vat_amount_label = QLabel(f"VAT ({int(PH_VAT_RATE * 100)}%): $0.00")
        self.vatable_sales_label.setStyleSheet("font-size: 12px;")
        self.vat_amount_label.setStyleSheet("font-size: 12px;")

        vatable_row = QHBoxLayout()
        vatable_row.addStretch()
        vatable_row.addWidget(self.vatable_sales_label)
        right.addLayout(vatable_row)

        vat_row = QHBoxLayout()
        vat_row.addStretch()
        vat_row.addWidget(self.vat_amount_label)
        right.addLayout(vat_row)

        totals_row = QHBoxLayout()
        totals_row.addStretch()
        self.total_label = QLabel("Total: $0.00")
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        totals_row.addWidget(self.total_label)
        right.addLayout(totals_row)

        customer_row = QHBoxLayout()
        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("Customer name (optional)")
        self.customer_phone = QLineEdit()
        self.customer_phone.setPlaceholderText("Phone (optional)")
        customer_row.addWidget(self.customer_name, 2)
        customer_row.addWidget(self.customer_phone, 1)
        right.addLayout(customer_row)

        payment_row = QHBoxLayout()
        self.payment_method = QComboBox()
        self.payment_method.addItem("Cash", "cash")
        self.payment_method.addItem("GCash", "gcash")
        self.payment_method.addItem("Card", "card")
        self.payment_method.addItem("Check", "check")
        payment_row.addWidget(QLabel("Payment:"))
        payment_row.addWidget(self.payment_method)
        payment_row.addStretch()

        self.checkout_btn = QPushButton("Checkout")
        self.checkout_btn.setIcon(load_icon("payment.png"))
        self.checkout_btn.setStyleSheet("background-color: #00b050; color: white; font-weight: bold; padding: 8px 18px; border-radius: 4px;")
        self.checkout_btn.clicked.connect(self.checkout)
        payment_row.addWidget(self.checkout_btn)

        right.addLayout(payment_row)

        tables_row.addLayout(left, 3)
        tables_row.addSpacing(12)
        tables_row.addLayout(right, 2)
        layout.addLayout(tables_row)

    def _load_categories(self):
        self.category_filter.blockSignals(True)
        self.category_filter.clear()
        self.category_filter.addItem("All Categories", None)
        categories = db_session.query(Category).order_by(Category.name).all()
        for c in categories:
            self.category_filter.addItem(c.name, c.id)
        self.category_filter.blockSignals(False)

    def _load_products(self, *_):
        search = (self.search_input.text() or "").strip()
        category_id = self.category_filter.currentData()

        query = db_session.query(Product)
        if category_id:
            query = query.filter(Product.category_id == category_id)
        if search:
            like = f"%{search}%"
            query = query.filter(func.lower(Product.name).like(func.lower(like)) | func.lower(Product.sku).like(func.lower(like)))

        products = query.order_by(Product.name).all()

        self.products_table.setRowCount(len(products))
        for row, p in enumerate(products):
            self.products_table.setItem(row, 0, QTableWidgetItem(str(p.id)))
            name_item = QTableWidgetItem(p.name)
            icon = None
            if not p.is_service and getattr(p, "image_filename", None):
                image_path = uploads_path(p.image_filename)
                if image_path and os.path.exists(image_path):
                    pixmap = QPixmap(image_path)
                    if not pixmap.isNull():
                        icon = QIcon(pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            elif p.is_service:
                icon = load_icon("service.png")

            if icon:
                name_item.setIcon(icon)

            self.products_table.setItem(row, 1, name_item)
            self.products_table.setItem(row, 2, QTableWidgetItem("Service" if p.is_service else "Product"))
            self.products_table.setItem(row, 3, QTableWidgetItem(format_currency(p.price)))
            self.products_table.setItem(row, 4, QTableWidgetItem("N/A" if p.is_service else str(p.stock)))

            add_btn = QPushButton("+")
            add_btn.setFixedWidth(32)
            add_btn.clicked.connect(lambda _, pid=p.id: self.add_to_cart(pid))
            self.products_table.setCellWidget(row, 5, add_btn)

        self.products_table.resizeRowsToContents()

    def _add_selected_product(self, row, col):
        try:
            pid = int(self.products_table.item(row, 0).text())
        except Exception:
            return
        self.add_to_cart(pid)

    def add_to_cart(self, product_id: int):
        product = db_session.get(Product, product_id)
        if not product:
            return

        qty = self.cart.get(product_id, 0) + 1

        if not product.is_service:
            if product.stock <= 0:
                QMessageBox.warning(self, "Out of Stock", f"{product.name} is out of stock")
                return
            if qty > product.stock:
                QMessageBox.warning(self, "Insufficient Stock", f"Only {product.stock} units available")
                return

        self.cart[product_id] = qty
        self._refresh_cart_table()

    def _refresh_cart_table(self):
        items = []
        for pid, qty in self.cart.items():
            p = db_session.get(Product, pid)
            if p:
                items.append((p, qty))

        self.cart_table.setRowCount(len(items))

        for row, (p, qty) in enumerate(items):
            price = float(p.price)
            total = price * qty

            self.cart_table.setItem(row, 0, QTableWidgetItem(p.name))
            self.cart_table.setItem(row, 1, QTableWidgetItem(format_currency(price)))

            qty_widget = QSpinBox()
            qty_widget.setMinimum(1)
            qty_widget.setMaximum(9999)
            qty_widget.setValue(qty)
            qty_widget.valueChanged.connect(lambda v, pid=p.id: self._set_qty(pid, v))
            self.cart_table.setCellWidget(row, 2, qty_widget)

            self.cart_table.setItem(row, 3, QTableWidgetItem(format_currency(total)))

            rm_btn = QPushButton("X")
            rm_btn.setFixedWidth(32)
            rm_btn.setStyleSheet("background-color: #000000; color: white;")
            rm_btn.clicked.connect(lambda _, pid=p.id: self._remove_item(pid))
            self.cart_table.setCellWidget(row, 4, rm_btn)

        self.cart_table.resizeRowsToContents()
        self._update_totals()

    def _set_qty(self, product_id: int, qty: int):
        product = db_session.get(Product, product_id)
        if not product:
            return

        if not product.is_service and qty > product.stock:
            QMessageBox.warning(self, "Insufficient Stock", f"Only {product.stock} units available")
            self._refresh_cart_table()
            return

        self.cart[product_id] = qty
        self._refresh_cart_table()

    def _remove_item(self, product_id: int):
        if product_id in self.cart:
            del self.cart[product_id]
        self._refresh_cart_table()

    def _update_totals(self):
        gross_total = Decimal("0")
        for pid, qty in self.cart.items():
            p = db_session.get(Product, pid)
            if p:
                gross_total += Decimal(str(p.price)) * int(qty)

        vatable_sales, vat_amount, total = compute_ph_vat_breakdown(gross_total, prices_include_vat=True)
        self.vatable_sales_label.setText(f"VATable Sales: {format_currency(vatable_sales)}")
        self.vat_amount_label.setText(f"VAT ({int(PH_VAT_RATE * 100)}%): {format_currency(vat_amount)}")
        self.total_label.setText(f"Total: {format_currency(total)}")

    def new_sale(self):
        if self.cart:
            reply = QMessageBox.question(
                self,
                'New Sale',
                'Clear the current cart?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        self.cart = {}
        self.customer_name.clear()
        self.customer_phone.clear()
        self._refresh_cart_table()

    def checkout(self):
        if not self.current_user:
            QMessageBox.warning(self, "Not logged in", "Please login again.")
            return

        if not self.cart:
            QMessageBox.warning(self, "Empty cart", "Add items before checkout.")
            return

        try:
            gross_total = Decimal("0")
            items = []
            for pid, qty in self.cart.items():
                p = db_session.get(Product, pid)
                if not p:
                    continue
                if not p.is_service and qty > p.stock:
                    raise Exception(f"Insufficient stock for {p.name}")
                price = Decimal(str(p.price))
                gross_total += price * int(qty)
                items.append((p, qty, price))

            _, _, total = compute_ph_vat_breakdown(gross_total, prices_include_vat=True)

            pm = self.payment_method.currentData()

            cash_received = None
            change_amount = None
            gcash_ref = None

            # Prompt for payment-specific details
            if pm == 'cash':
                ok = False
                # ask for cash given
                cash, ok = QInputDialog.getDouble(self, 'Cash Received', 'Enter cash handed by customer:', float(total), 0, 1000000, 2)
                if not ok:
                    return
                cash_received = cash
                change_amount = float(Decimal(str(cash)) - Decimal(str(total)))
            elif pm == 'gcash':
                text, ok = QInputDialog.getText(self, 'GCash Reference', 'Enter GCash reference / transaction ID:')
                if not ok:
                    return
                gcash_ref = text.strip() or None

            tx = Transaction(
                employee_id=self.current_user.id,
                total=total,
                payment_method=pm,
                cash_received=cash_received,
                change_amount=change_amount,
                gcash_ref=gcash_ref,
                customer_name=(self.customer_name.text() or "").strip() or None,
                customer_phone=(self.customer_phone.text() or "").strip() or None,
            )
            db_session.add(tx)
            db_session.flush()

            for p, qty, price in items:
                db_session.add(
                    TransactionItem(
                        transaction_id=tx.id,
                        product_id=p.id,
                        qty=qty,
                        price=price,
                        cost_price=float(getattr(p, "cost_price", 0.0) or 0.0),
                    )
                )

                if not p.is_service:
                    p.stock = max(0, int(p.stock) - int(qty))
                    db_session.add(
                        StockChange(
                            product_id=p.id,
                            user_id=self.current_user.id,
                            qty_change=-int(qty),
                            note=f"Sold in transaction #{tx.id}",
                        )
                    )

            db_session.commit()

            reply = QMessageBox.question(
                self,
                "Checkout Complete",
                f"Transaction #{tx.id} saved. Print/View receipt?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes,
            )
            if reply == QMessageBox.StandardButton.Yes:
                ReceiptDialog(tx.id, self).exec()

            self.new_sale()
            self._load_products()

        except Exception as e:
            db_session.rollback()
            QMessageBox.critical(self, "Error", str(e))
