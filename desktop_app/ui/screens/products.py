from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QMessageBox, QInputDialog, QFileDialog, QComboBox, QLineEdit,
    QFormLayout, QDialog, QDialogButtonBox, QSpinBox, QDoubleSpinBox,
    QCheckBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap, QFont, QColor
from ...models import Product, Category
from ...database import db_session
from ...utils.helpers import get_icon_path, format_currency, uploads_path, copy_image_to_uploads, load_icon
import os
from datetime import datetime
from decimal import Decimal
from ..widgets import (
    ModernTable, SearchBar, FilterComboBox, ActionButton,
    IconButton, SectionHeader, ModernDialog, StatusBadge
)


class ProductsScreen(QWidget):
    """Products management screen with modern design."""
    
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.setup_ui()
        self.load_products()
        self.load_categories()

    def set_user(self, user):
        self.current_user = user
        self.apply_permissions()

    def apply_permissions(self):
        is_admin = bool(self.current_user and getattr(self.current_user, 'role', None) == 'admin')
        self.add_btn.setEnabled(is_admin)
        self.categories_btn.setEnabled(is_admin)
        self.load_products()
    
    def setup_ui(self):
        """Set up the products UI with modern design."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header with title and action buttons
        header_layout = QHBoxLayout()
        
        title = QLabel("Products & Inventory")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #00b050;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.categories_btn = ActionButton("Manage Categories", "categories.png", "#000000")
        self.categories_btn.clicked.connect(self.manage_categories)
        header_layout.addWidget(self.categories_btn)

        self.add_btn = ActionButton("Add New Product", "add.png", "#00b050")
        self.add_btn.clicked.connect(self.show_add_product_dialog)
        header_layout.addWidget(self.add_btn)
        
        layout.addLayout(header_layout)
        
        # Search and filter section
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(12)
        
        self.search_input = SearchBar("Search by name, SKU, or category...")
        self.search_input.textChanged.connect(self.filter_products)
        filter_layout.addWidget(self.search_input, 2)
        
        self.category_filter = FilterComboBox()
        self.category_filter.currentIndexChanged.connect(self.filter_products)
        filter_layout.addWidget(self.category_filter, 1)
        
        layout.addLayout(filter_layout)
        
        # Section header
        products_header = SectionHeader("Product Inventory")
        layout.addWidget(products_header)
        
        # Products table
        self.products_table = ModernTable()
        self.products_table.setColumnCount(6)
        self.products_table.setHorizontalHeaderLabels([
            "ID", "Name", "Category", "Price", "Stock", "Actions"
        ])
        
        header = self.products_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.products_table, 1)
    
    def load_products(self, category_id=None, search_text=""):
        """Load products with filtering."""
        try:
            is_admin = bool(self.current_user and getattr(self.current_user, 'role', None) == 'admin')
            query = db_session.query(Product)
            
            if category_id:
                query = query.filter(Product.category_id == category_id)
            
            if search_text:
                search = f"%{search_text}%"
                query = query.filter(Product.name.ilike(search))
            
            products = query.order_by(Product.name).all()
            
            self.products_table.setRowCount(len(products))
            
            for row, product in enumerate(products):
                self.products_table.setItem(row, 0, QTableWidgetItem(str(product.id)))
                
                name_item = QTableWidgetItem(product.name)
                if product.is_service:
                    name_item.setText(f"{product.name} (Service)")
                self.products_table.setItem(row, 1, name_item)
                
                category_text = product.category.name if product.category else "—"
                self.products_table.setItem(row, 2, QTableWidgetItem(category_text))
                
                self.products_table.setItem(row, 3, QTableWidgetItem(format_currency(product.price)))
                
                stock_item = QTableWidgetItem()
                if product.is_service:
                    stock_item.setText("N/A")
                else:
                    stock_text = str(product.stock)
                    stock_item.setText(stock_text)
                    if product.stock <= 5:
                        stock_item.setForeground(QColor("#f44336"))
                        font = QFont()
                        font.setBold(True)
                        stock_item.setFont(font)
                    elif product.stock <= 15:
                        stock_item.setForeground(QColor("#ff9800"))
                        font = QFont()
                        font.setBold(True)
                        stock_item.setFont(font)
                
                self.products_table.setItem(row, 4, stock_item)
                
                if is_admin:
                    actions_widget = QWidget()
                    actions_layout = QHBoxLayout(actions_widget)
                    actions_layout.setContentsMargins(4, 2, 4, 2)
                    actions_layout.setSpacing(4)
                    
                    edit_btn = IconButton("edit.png", "Edit", 30)
                    edit_btn.clicked.connect(lambda _, p=product: self.edit_product(p))
                    actions_layout.addWidget(edit_btn)
                    
                    if not product.is_service:
                        stock_btn = IconButton("inventory.png", "Stock", 30)
                        stock_btn.clicked.connect(lambda _, p=product: self.adjust_stock(p))
                        actions_layout.addWidget(stock_btn)
                    
                    delete_btn = IconButton("delete.png", "Delete", 30)
                    delete_btn.clicked.connect(lambda _, p=product: self.delete_product(p))
                    actions_layout.addWidget(delete_btn)
                    actions_layout.addStretch()
                    
                    self.products_table.setCellWidget(row, 5, actions_widget)
            
            self.products_table.resizeRowsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load products: {str(e)}")
    
    def load_categories(self):
        """Load categories into filter."""
        try:
            self.category_filter.blockSignals(True)
            self.category_filter.clear()
            self.category_filter.addItem("All Categories", None)
            
            categories = db_session.query(Category).order_by(Category.name).all()
            for category in categories:
                self.category_filter.addItem(category.name, category.id)
            
            self.category_filter.blockSignals(False)
        except Exception as e:
            print(f"Error loading categories: {e}")
    
    def filter_products(self, *_):
        """Filter products."""
        search_text = self.search_input.text().strip()
        category_id = self.category_filter.currentData()
        self.load_products(category_id, search_text)
    
    def show_add_product_dialog(self, product=None):
        """Show product dialog."""
        if not (self.current_user and getattr(self.current_user, 'role', None) == 'admin'):
            QMessageBox.warning(self, "Not Authorized", "Only admins can manage products.")
            return
        
        dialog = ProductDialog(self, product)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_products()
            self.load_categories()
    
    def edit_product(self, product):
        """Edit product."""
        self.show_add_product_dialog(product)
    
    def delete_product(self, product):
        """Delete product."""
        if not (self.current_user and getattr(self.current_user, 'role', None) == 'admin'):
            QMessageBox.warning(self, "Not Authorized", "Only admins can delete products.")
            return
        
        reply = QMessageBox.question(
            self, "Delete Product",
            f'Delete "{product.name}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if product.image_filename:
                    image_path = uploads_path(product.image_filename)
                    if image_path and os.path.exists(image_path):
                        os.remove(image_path)
                
                db_session.delete(product)
                db_session.commit()
                
                self.load_products()
                QMessageBox.information(self, "Success", "Product deleted.")
            except Exception as e:
                db_session.rollback()
                QMessageBox.critical(self, "Error", f"Failed to delete: {str(e)}")
    
    def adjust_stock(self, product):
        """Adjust stock."""
        if not (self.current_user and getattr(self.current_user, 'role', None) == 'admin'):
            QMessageBox.warning(self, "Not Authorized", "Only admins can adjust stock.")
            return
        
        if product.is_service:
            QMessageBox.information(self, "Info", "Services don't have stock.")
            return
        
        dialog = StockAdjustDialog(product, self.current_user, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_products()
    
    def manage_categories(self):
        """Manage categories."""
        if not (self.current_user and getattr(self.current_user, 'role', None) == 'admin'):
            QMessageBox.warning(self, "Not Authorized", "Only admins can manage categories.")
            return
        
        dialog = CategoryManagerDialog(self)
        dialog.exec()
        self.load_categories()
        self.load_products()


class ProductDialog(ModernDialog):
    """Dialog for adding/editing products."""
    
    def __init__(self, parent=None, product=None):
        super().__init__("Add Product" if not product else f"Edit {product.name}", parent)
        self.product = product
        self.image_data = None
        self.image_removed = False
        self.original_image = None
        
        self.setup_form()
        if product:
            self.load_product_data()
    
    def setup_form(self):
        """Set up form."""
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Product name")
        
        self.sku_input = QLineEdit()
        self.sku_input.setPlaceholderText("SKU (optional)")
        
        self.category_combo = FilterComboBox()
        self.load_categories()
        
        self.price_input = QDoubleSpinBox()
        self.price_input.setPrefix("₱ ")
        self.price_input.setMinimum(0)
        self.price_input.setMaximum(999999.99)
        self.price_input.setDecimals(2)
        
        self.stock_input = QSpinBox()
        self.stock_input.setMinimum(0)
        self.stock_input.setMaximum(9999)
        
        self.is_service_check = QCheckBox("Service (no inventory)")
        self.is_service_check.stateChanged.connect(self.toggle_service_fields)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setFixedSize(200, 200)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                border: 2px dashed #00b050;
                border-radius: 6px;
            }
        """)
        self.image_label.setText("Click to select")
        self.image_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.image_label.mousePressEvent = lambda e: self.select_image()
        
        self.remove_image_btn = QPushButton("Remove Image")
        self.remove_image_btn.setEnabled(False)
        self.remove_image_btn.clicked.connect(self.remove_image)
        
        fields = [
            ("Name*", self.name_input),
            ("SKU", self.sku_input),
            ("Category", self.category_combo),
            ("Price*", self.price_input),
            ("Stock", self.stock_input),
        ]
        
        self.add_form_fields(fields)
        self.layout.addWidget(self.is_service_check)
        self.layout.addWidget(QLabel("Image:"))
        self.layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.remove_image_btn)
        
        self.add_buttons("Save", "Cancel")
    
    def load_categories(self):
        """Load categories."""
        self.category_combo.clear()
        self.category_combo.addItem("Select category", None)
        
        categories = db_session.query(Category).order_by(Category.name).all()
        for cat in categories:
            self.category_combo.addItem(cat.name, cat.id)
    
    def load_product_data(self):
        """Load product data."""
        if not self.product:
            return
        
        self.name_input.setText(self.product.name)
        self.sku_input.setText(self.product.sku or "")
        
        if self.product.category_id:
            idx = self.category_combo.findData(self.product.category_id)
            if idx >= 0:
                self.category_combo.setCurrentIndex(idx)
        
        self.price_input.setValue(float(self.product.price))
        self.stock_input.setValue(self.product.stock)
        self.is_service_check.setChecked(self.product.is_service)
        
        if self.product.image_filename:
            self.original_image = self.product.image_filename
            self.load_image(self.product.image_filename)
    
    def load_image(self, filename):
        """Load image."""
        try:
            path = uploads_path(filename)
            if path and os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    self.image_label.setPixmap(pixmap)
                    self.remove_image_btn.setEnabled(True)
        except Exception as e:
            print(f"Error loading image: {e}")
    
    def select_image(self):
        """Select image."""
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.gif *.bmp)")
        
        if dialog.exec():
            try:
                file_path = dialog.selectedFiles()[0]
                copied = copy_image_to_uploads(file_path)
                if not copied:
                    QMessageBox.critical(self, "Error", "Failed to copy image.")
                    return
                self.image_data = copied
                self.image_removed = False
                self.load_image(copied)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
    
    def remove_image(self):
        """Remove image."""
        self.image_data = None
        self.image_removed = True
        self.image_label.setPixmap(QPixmap())
        self.image_label.setText("Click to select")
        self.remove_image_btn.setEnabled(False)
    
    def toggle_service_fields(self, state):
        """Toggle service fields."""
        is_service = state == Qt.CheckState.Checked.value
        self.stock_input.setEnabled(not is_service)
    
    def accept(self):
        """Save product."""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Product name is required.")
            return
        
        price = self.price_input.value()
        if price <= 0:
            QMessageBox.warning(self, "Error", "Price must be greater than 0.")
            return
        
        try:
            if not self.product:
                self.product = Product()
                db_session.add(self.product)
            
            self.product.name = name
            self.product.sku = self.sku_input.text().strip() or None
            self.product.category_id = self.category_combo.currentData()
            self.product.price = price
            self.product.is_service = self.is_service_check.isChecked()
            
            if not self.product.is_service:
                self.product.stock = self.stock_input.value()
            else:
                self.product.stock = 0
            
            if self.image_data:
                if self.original_image and self.original_image != self.image_data:
                    old_path = uploads_path(self.original_image)
                    if old_path and os.path.exists(old_path):
                        os.remove(old_path)
                self.product.image_filename = self.image_data
            elif self.image_removed and self.original_image:
                old_path = uploads_path(self.original_image)
                if old_path and os.path.exists(old_path):
                    os.remove(old_path)
                self.product.image_filename = None
            
            db_session.commit()
            super().accept()
            
        except Exception as e:
            db_session.rollback()
            QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")


class StockAdjustDialog(ModernDialog):
    """Dialog for stock adjustment."""
    
    def __init__(self, product, user, parent=None):
        super().__init__(f"Adjust Stock - {product.name}", parent)
        self.product = product
        self.user = user
        
        self.setup_form()
    
    def setup_form(self):
        """Set up form."""
        current_label = QLabel(f"Current: {self.product.stock} units")
        current_label.setStyleSheet("font-weight: bold; color: #00b050;")
        self.layout.addWidget(current_label)
        
        self.adjust_type = FilterComboBox()
        self.adjust_type.addItem("Add", "add")
        self.adjust_type.addItem("Remove", "remove")
        self.adjust_type.addItem("Set to", "set")
        self.adjust_type.currentIndexChanged.connect(self.update_form)
        
        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(1)
        self.quantity_input.setMaximum(9999)
        
        self.unit_cost_input = QDoubleSpinBox()
        self.unit_cost_input.setPrefix("₱ ")
        self.unit_cost_input.setMinimum(0)
        self.unit_cost_input.setMaximum(999999.99)
        self.unit_cost_input.setDecimals(2)
        
        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText("Note")
        
        fields = [
            ("Action*", self.adjust_type),
            ("Quantity*", self.quantity_input),
            ("Unit Cost", self.unit_cost_input),
            ("Note", self.note_input),
        ]
        
        self.add_form_fields(fields)
        self.add_buttons("Apply", "Cancel")
        self.update_form()
    
    def update_form(self):
        """Update form."""
        self.unit_cost_input.setEnabled(self.adjust_type.currentData() == "add")
    
    def accept(self):
        """Apply adjustment."""
        try:
            qty = self.quantity_input.value()
            note = self.note_input.text().strip()
            action = self.adjust_type.currentData()
            
            if action == "add":
                new_stock = self.product.stock + qty
                if self.unit_cost_input.value() <= 0:
                    QMessageBox.warning(self, "Error", "Unit cost required.")
                    return
            elif action == "remove":
                new_stock = max(0, self.product.stock - qty)
            else:
                new_stock = qty
            
            old_stock = self.product.stock
            self.product.stock = new_stock
            
            from ...models import StockChange
            change = StockChange(
                product_id=self.product.id,
                user_id=self.user.id,
                qty_change=new_stock - old_stock,
                unit_cost=Decimal(str(self.unit_cost_input.value())) if action == "add" else None,
                note=note or f"Stock: {action}"
            )
            db_session.add(change)
            db_session.commit()
            
            QMessageBox.information(self, "Success", f"Stock: {new_stock}")
            super().accept()
            
        except Exception as e:
            db_session.rollback()
            QMessageBox.critical(self, "Error", str(e))


class CategoryManagerDialog(ModernDialog):
    """Dialog for managing categories."""
    
    def __init__(self, parent=None):
        super().__init__("Manage Categories", parent)
        self.setMinimumSize(500, 400)
        self.setup_ui()
        self.load_categories()
    
    def setup_ui(self):
        """Set up UI."""
        button_layout = QHBoxLayout()
        
        add_btn = ActionButton("Add", "add.png", "#00b050")
        add_btn.clicked.connect(self.add_category)
        button_layout.addWidget(add_btn)
        
        edit_btn = ActionButton("Edit", "edit.png", "#2196f3")
        edit_btn.clicked.connect(self.edit_category)
        button_layout.addWidget(edit_btn)
        
        delete_btn = ActionButton("Delete", "delete.png", "#f44336")
        delete_btn.clicked.connect(self.delete_category)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        self.layout.addLayout(button_layout)
        
        self.table = ModernTable()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["ID", "Name"])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        self.layout.addWidget(self.table)
        self.add_buttons("Done", "Close")
    
    def load_categories(self):
        """Load categories."""
        cats = db_session.query(Category).order_by(Category.name).all()
        self.table.setRowCount(len(cats))
        
        for row, cat in enumerate(cats):
            self.table.setItem(row, 0, QTableWidgetItem(str(cat.id)))
            self.table.setItem(row, 1, QTableWidgetItem(cat.name or ""))
        
        self.table.resizeRowsToContents()
    
    def selected_category(self):
        """Get selected."""
        row = self.table.currentRow()
        if row < 0:
            return None
        
        try:
            cat_id = int(self.table.item(row, 0).text())
            return db_session.get(Category, cat_id)
        except:
            return None
    
    def add_category(self):
        """Add category."""
        text, ok = QInputDialog.getText(self, "Add", "Name:")
        if ok and text.strip():
            name = text.strip()
            if db_session.query(Category).filter(Category.name == name).first():
                QMessageBox.warning(self, "Error", "Exists.")
                return
            
            try:
                cat = Category(name=name)
                db_session.add(cat)
                db_session.commit()
                self.load_categories()
            except Exception as e:
                db_session.rollback()
                QMessageBox.critical(self, "Error", str(e))
    
    def edit_category(self):
        """Edit category."""
        cat = self.selected_category()
        if not cat:
            QMessageBox.warning(self, "Error", "Select one.")
            return
        
        text, ok = QInputDialog.getText(self, "Edit", "Name:", text=cat.name)
        if ok and text.strip():
            name = text.strip()
            if db_session.query(Category).filter(Category.name == name, Category.id != cat.id).first():
                QMessageBox.warning(self, "Error", "Exists.")
                return
            
            try:
                cat.name = name
                db_session.commit()
                self.load_categories()
            except Exception as e:
                db_session.rollback()
                QMessageBox.critical(self, "Error", str(e))
    
    def delete_category(self):
        """Delete category."""
        cat = self.selected_category()
        if not cat:
            QMessageBox.warning(self, "Error", "Select one.")
            return
        
        reply = QMessageBox.question(
            self, "Delete",
            f'Delete "{cat.name}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                products = db_session.query(Product).filter(Product.category_id == cat.id).all()
                for p in products:
                    p.category_id = None
                
                db_session.delete(cat)
                db_session.commit()
                self.load_categories()
            except Exception as e:
                db_session.rollback()
                QMessageBox.critical(self, "Error", str(e))
