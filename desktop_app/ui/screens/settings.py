from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox,
    QInputDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from sqlalchemy import desc

from ...database import db_session
from ...models import User, StockChange
from ...utils.helpers import load_icon
from ..widgets import (
    ModernTable, ActionButton, SectionHeader, IconButton, ModernDialog
)


class SettingsScreen(QWidget):
    """Settings screen with employees and stock logs management."""
    
    def __init__(self):
        super().__init__()
        self.current_user = None
        self._build_ui()

    def set_user(self, user):
        self.current_user = user
        self._apply_permissions()
        self.refresh_all()

    def _build_ui(self):
        """Set up the settings UI with modern design."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QHBoxLayout()
        title = QLabel("Settings & Management")
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

        # Unauthorized message
        self.unauthorized_label = QLabel("⚠️  Admin access required to manage settings")
        self.unauthorized_label.setStyleSheet("""
            color: #f44336;
            font-weight: bold;
            padding: 12px;
            background-color: #ffebee;
            border-radius: 4px;
        """)
        self.unauthorized_label.setVisible(False)
        layout.addWidget(self.unauthorized_label)

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

        # === Employees Tab ===
        emp_tab = QWidget()
        emp_layout = QVBoxLayout(emp_tab)
        emp_layout.setContentsMargins(0, 15, 0, 0)
        emp_layout.setSpacing(12)

        emp_header = SectionHeader("Employees")
        emp_layout.addWidget(emp_header)

        # Action buttons
        btn_row = QHBoxLayout()
        self.add_emp_btn = ActionButton("Add Employee", "add.png", "#00b050")
        self.add_emp_btn.clicked.connect(self.add_employee)
        btn_row.addWidget(self.add_emp_btn)

        self.reset_pw_btn = ActionButton("Reset Password", "edit.png", "#2196f3")
        self.reset_pw_btn.clicked.connect(self.reset_password)
        btn_row.addWidget(self.reset_pw_btn)

        self.delete_emp_btn = ActionButton("Delete", "delete.png", "#f44336")
        self.delete_emp_btn.clicked.connect(self.delete_employee)
        btn_row.addWidget(self.delete_emp_btn)

        btn_row.addStretch()
        emp_layout.addLayout(btn_row)

        # Employees table
        self.emp_table = ModernTable()
        self.emp_table.setColumnCount(4)
        self.emp_table.setHorizontalHeaderLabels(["ID", "Username", "Role", "Created"])
        
        header = self.emp_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        emp_layout.addWidget(self.emp_table, 1)
        self.tabs.addTab(emp_tab, "Employees")

        # === Stock Logs Tab ===
        logs_tab = QWidget()
        logs_layout = QVBoxLayout(logs_tab)
        logs_layout.setContentsMargins(0, 15, 0, 0)
        logs_layout.setSpacing(12)

        logs_header = SectionHeader("Stock Changes")
        logs_layout.addWidget(logs_header)

        # Stock logs table
        self.logs_table = ModernTable()
        self.logs_table.setColumnCount(5)
        self.logs_table.setHorizontalHeaderLabels(["Date", "Product", "User", "Qty Change", "Note"])
        
        header = self.logs_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        
        logs_layout.addWidget(self.logs_table, 1)
        self.tabs.addTab(logs_tab, "Stock Logs")

    def _is_admin(self) -> bool:
        return bool(self.current_user and getattr(self.current_user, 'role', None) == 'admin')

    def _apply_permissions(self):
        admin = self._is_admin()
        self.unauthorized_label.setVisible(not admin)
        self.tabs.setEnabled(admin)

    def refresh_all(self):
        if not self._is_admin():
            return
        self.load_users()
        self.load_stock_logs()

    def load_users(self):
        users = db_session.query(User).order_by(User.username).all()
        self.emp_table.setRowCount(len(users))
        for row, u in enumerate(users):
            self.emp_table.setItem(row, 0, QTableWidgetItem(str(u.id)))
            self.emp_table.setItem(row, 1, QTableWidgetItem(u.username))
            self.emp_table.setItem(row, 2, QTableWidgetItem(u.role))
            self.emp_table.setItem(row, 3, QTableWidgetItem(u.created_at.strftime('%Y-%m-%d %H:%M')))
        self.emp_table.resizeRowsToContents()

    def selected_user(self):
        row = self.emp_table.currentRow()
        if row < 0:
            return None
        try:
            uid = int(self.emp_table.item(row, 0).text())
        except Exception:
            return None
        return db_session.get(User, uid)

    def add_employee(self):
        if not self._is_admin():
            return
        dlg = AddEmployeeDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.load_users()

    def reset_password(self):
        if not self._is_admin():
            return
        u = self.selected_user()
        if not u:
            return
        new_pw, ok = QInputDialog.getText(self, "Reset Password", f"New password for {u.username}:", QLineEdit.EchoMode.Password)
        if not ok:
            return
        new_pw = (new_pw or "").strip()
        if not new_pw:
            return
        u.set_password(new_pw)
        db_session.commit()
        QMessageBox.information(self, "Updated", "Password updated.")

    def delete_employee(self):
        if not self._is_admin():
            return
        u = self.selected_user()
        if not u:
            return
        if self.current_user and u.id == self.current_user.id:
            QMessageBox.warning(self, "Error", "You cannot delete the currently logged in user.")
            return
        reply = QMessageBox.question(
            self,
            'Delete Employee',
            f'Delete user "{u.username}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        db_session.delete(u)
        db_session.commit()
        self.load_users()

    def load_stock_logs(self):
        logs = (
            db_session.query(StockChange)
            .order_by(StockChange.created_at.desc())
            .limit(200)
            .all()
        )
        self.logs_table.setRowCount(len(logs))
        for row, l in enumerate(logs):
            self.logs_table.setItem(row, 0, QTableWidgetItem(l.created_at.strftime('%Y-%m-%d %H:%M')))
            product_name = l.product.name if l.product else f"#{l.product_id}"
            user_name = l.user.username if l.user else f"#{l.user_id}"
            self.logs_table.setItem(row, 1, QTableWidgetItem(product_name))
            self.logs_table.setItem(row, 2, QTableWidgetItem(user_name))
            self.logs_table.setItem(row, 3, QTableWidgetItem(str(l.qty_change)))
            self.logs_table.setItem(row, 4, QTableWidgetItem(l.note or ""))
        self.logs_table.resizeRowsToContents()


class AddEmployeeDialog(ModernDialog):
    """Modern dialog for adding new employees."""
    
    def __init__(self, parent=None):
        super().__init__("Add New Employee", parent)
        self.setMinimumWidth(400)
        self.setup_form()

    def setup_form(self):
        """Set up the form fields."""
        self.username = QLineEdit()
        self.username.setPlaceholderText("Enter username")
        
        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.role = QComboBox()
        self.role.addItem("Employee", "employee")
        self.role.addItem("Admin", "admin")

        fields = [
            ("Username*", self.username),
            ("Password*", self.password),
            ("Role*", self.role),
        ]
        
        self.add_form_fields(fields)
        self.add_buttons("Create Employee", "Cancel")

    def accept(self):
        """Validate and save employee."""
        username = (self.username.text() or "").strip()
        password = (self.password.text() or "").strip()
        role = self.role.currentData()

        if not username or not password:
            QMessageBox.warning(self, "Validation Error", "Username and password are required.")
            return

        if db_session.query(User).filter(User.username == username).first():
            QMessageBox.warning(self, "Error", "Username already exists.")
            return

        try:
            user = User(username=username, role=role)
            user.set_password(password)
            db_session.add(user)
            db_session.commit()
            super().accept()
        except Exception as e:
            db_session.rollback()
            QMessageBox.critical(self, "Error", f"Failed to create employee: {str(e)}")
