from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QStackedWidget, QToolBar, QStatusBar, 
                            QPushButton, QSizePolicy, QMessageBox, QSplitter, 
                            QListWidget, QListWidgetItem, QFrame, QToolButton)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon, QPixmap
from ..models import User
from .screens.dashboard import DashboardScreen
from .screens.products import ProductsScreen
from .screens.sales import SalesScreen
from .screens.customers import CustomersScreen
from .screens.reports import ReportsScreen
from .screens.settings import SettingsScreen
from ..utils.helpers import get_icon_path, load_icon

class MainWindow(QMainWindow):
    """Main application window that contains the main interface."""
    
    def __init__(self):
        super().__init__()
        self.current_user = None
        self._logging_out = False
        self._sidebar_collapsed = False
        self._sidebar_expanded_width = 260
        self._sidebar_collapsed_width = 72
        self.setWindowTitle("POS System")
        self.setMinimumSize(1024, 720)
        
        # Initialize UI components
        self.init_ui()
    
    def set_user(self, user):
        """Set the current user and update UI accordingly."""
        self.current_user = user
        self._logging_out = False
        self.update_ui_for_user()
    
    def init_ui(self):
        """Initialize the main UI components."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(1)

        self.sidebar = self.create_sidebar()
        self.splitter.addWidget(self.sidebar)

        content_widget = QWidget()
        content_widget.setObjectName("content")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_widget.setStyleSheet("""
            QWidget#content {
                background-color: #ffffff;
            }
            QTableWidget {
                background-color: #ffffff;
                color: #000000;
                alternate-background-color: rgba(0, 176, 80, 0.06);
                gridline-color: #00b050;
                selection-background-color: #00b050;
                selection-color: #ffffff;
            }
            QHeaderView::section {
                background-color: #000000;
                color: #ffffff;
                border: 1px solid #00b050;
            }
            QPushButton {
                font-size: 13px;
            }
        """)
        
        # Create toolbar
        self.toolbar = self.create_toolbar()
        content_layout.addWidget(self.toolbar)
        
        # Create stacked widget for different screens
        self.stacked_widget = QStackedWidget()
        
        # Add screens to stacked widget
        self.dashboard_screen = DashboardScreen()
        self.products_screen = ProductsScreen()
        self.sales_screen = SalesScreen()
        self.customers_screen = CustomersScreen()
        self.reports_screen = ReportsScreen()
        self.settings_screen = SettingsScreen()
        
        self.stacked_widget.addWidget(self.dashboard_screen)
        self.stacked_widget.addWidget(self.products_screen)
        self.stacked_widget.addWidget(self.sales_screen)
        self.stacked_widget.addWidget(self.customers_screen)
        self.stacked_widget.addWidget(self.reports_screen)
        self.stacked_widget.addWidget(self.settings_screen)
        
        content_layout.addWidget(self.stacked_widget)

        self.splitter.addWidget(content_widget)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([self._sidebar_expanded_width, 1000])

        root_layout.addWidget(self.splitter)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.status_user_label = QLabel("")
        self.status_bar.addPermanentWidget(self.status_user_label)
        self.setStatusBar(self.status_bar)

        self.setStyleSheet(
            """
            QToolBar {
                background: #ffffff;
                border: none;
                border-bottom: 1px solid #00b050;
                padding: 6px;
                spacing: 6px;
            }
            QToolBar QToolButton {
                color: #000000;
                padding: 6px 10px;
                border-radius: 6px;
            }
            QToolBar QToolButton:hover {
                background: #00b050;
                color: #ffffff;
            }
            QStatusBar {
                background: #ffffff;
                border-top: 1px solid #00b050;
                padding: 6px;
            }
            QStatusBar QLabel {
                color: #000000;
            }
            QSplitter::handle {
                background: #00b050;
            }
            """
        )
        
        # Set window icon if available
        icon = load_icon("app_icon.png")
        if icon is not None and not icon.isNull():
            self.setWindowIcon(icon)
    
    def create_sidebar(self):
        """Create a modern sidebar navigation."""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setStyleSheet(
            """
            QFrame#sidebar {
                background-color: #000000;
                color: #ffffff;
            }
            QLabel#app_name {
                font-size: 18px;
                font-weight: bold;
                padding: 8px 0px;
                color: #00b050;
            }
            QLabel#user_info {
                padding: 12px;
                border-radius: 6px;
                background: rgba(0, 176, 80, 0.15);
                font-size: 11px;
                color: #e0e0e0;
                border: 1px solid rgba(0, 176, 80, 0.25);
            }
            QListWidget#nav_list {
                background: transparent;
                border: none;
                outline: none;
            }
            QListWidget#nav_list::item {
                padding: 12px 10px;
                margin: 4px 0px;
                border-radius: 6px;
                color: #cccccc;
                icon-size: 18px;
            }
            QListWidget#nav_list::item:hover {
                background: rgba(0, 176, 80, 0.2);
                color: #ffffff;
            }
            QListWidget#nav_list::item:selected {
                background: #00b050;
                color: #000000;
                font-weight: bold;
            }
            QToolButton#logout_btn {
                padding: 10px 10px;
                border-radius: 6px;
                text-align: left;
                color: #ffffff;
                background: transparent;
                border: 1px solid rgba(0, 176, 80, 0.2);
            }
            QToolButton#logout_btn:hover {
                background: rgba(0, 176, 80, 0.25);
                border: 1px solid rgba(0, 176, 80, 0.4);
            }
            """
        )

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # App name with logo
        header = QHBoxLayout()
        self.app_name_label = QLabel("🟢 POS")
        self.app_name_label.setObjectName("app_name")
        header.addWidget(self.app_name_label)
        header.addStretch()
        layout.addLayout(header)

        # User info card
        self.user_info_label = QLabel("Not logged in")
        self.user_info_label.setObjectName("user_info")
        self.user_info_label.setWordWrap(True)
        layout.addWidget(self.user_info_label)

        # Navigation list
        self.nav_list = QListWidget()
        self.nav_list.setObjectName("nav_list")
        self.nav_list.setIconSize(QSize(18, 18))
        self.nav_list.setFrameShape(QFrame.Shape.NoFrame)
        self.nav_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.nav_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.nav_list.currentItemChanged.connect(self.on_nav_item_changed)
        layout.addWidget(self.nav_list, stretch=1)

        nav_items = [
            ("dashboard", "📊 Dashboard", "dashboard.png"),
            ("products", "📦 Products", "products.png"),
            ("sales", "🛒 Sales", "sales.png"),
            ("customers", "👥 Customers", "customers.png"),
            ("reports", "📈 Reports", "reports.png"),
            ("settings", "⚙️  Settings", "settings.png"),
        ]

        for key, text, icon_name in nav_items:
            item = QListWidgetItem(load_icon(icon_name), text)
            item.setData(Qt.ItemDataRole.UserRole, key)
            item.setToolTip(text.split(" ", 1)[1])  # Extract without emoji
            self.nav_list.addItem(item)

        # Logout button
        self.logout_btn = QToolButton()
        self.logout_btn.setObjectName("logout_btn")
        self.logout_btn.setText("🚪 Logout")
        self.logout_btn.setIcon(load_icon("logout.png"))
        self.logout_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.logout_btn.setIconSize(QSize(16, 16))
        self.logout_btn.clicked.connect(self.logout)
        layout.addWidget(self.logout_btn)

        return sidebar

    def create_toolbar(self):
        """Create a modern top toolbar."""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(18, 18))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        toolbar.setObjectName("main_toolbar")

        toggle_sidebar_action = QAction("☰ Menu", self)
        toggle_sidebar_action.setIcon(load_icon("menu.png"))
        toggle_sidebar_action.triggered.connect(self.toggle_sidebar)

        # Top-level actions (removed: New Sale, Add Product, Settings)

        self.page_title_label = QLabel("Dashboard")
        title_font = self.page_title_label.font()
        title_font.setPointSize(13)
        title_font.setBold(True)
        self.page_title_label.setFont(title_font)
        self.page_title_label.setStyleSheet("color: #00b050; padding-left: 6px;")

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        toolbar.addAction(toggle_sidebar_action)
        toolbar.addSeparator()
        toolbar.addWidget(self.page_title_label)
        toolbar.addWidget(spacer)

        return toolbar

    def update_ui_for_user(self):
        """Update UI based on the current user's role and information."""
        if not self.current_user:
            return

        self.user_info_label.setText(f"{self.current_user.username}\n{self.current_user.role.upper()}")
        if hasattr(self, 'status_user_label'):
            self.status_user_label.setText(f"{self.current_user.username} ({self.current_user.role.upper()})")

        for screen in (
            self.dashboard_screen,
            self.products_screen,
            self.sales_screen,
            self.customers_screen,
            self.reports_screen,
            self.settings_screen,
        ):
            if hasattr(screen, 'set_user'):
                screen.set_user(self.current_user)

        self.show_dashboard()

    def on_nav_item_changed(self, current, previous):
        if current is None:
            return

        key = current.data(Qt.ItemDataRole.UserRole)
        if key:
            self.navigate_to(str(key))

    def navigate_to(self, key):
        mapping = {
            'dashboard': (self.dashboard_screen, 'Dashboard'),
            'products': (self.products_screen, 'Products'),
            'sales': (self.sales_screen, 'Sales'),
            'customers': (self.customers_screen, 'Customers'),
            'reports': (self.reports_screen, 'Reports'),
            'settings': (self.settings_screen, 'Settings'),
        }
        if key not in mapping:
            return

        widget, title = mapping[key]
        self.stacked_widget.setCurrentWidget(widget)
        self.set_active_nav_button(key)
        if hasattr(self, 'page_title_label'):
            self.page_title_label.setText(title)
        if hasattr(self, 'status_bar') and self.status_bar is not None:
            self.status_bar.showMessage(title)

    # Navigation methods
    def show_dashboard(self):
        self.navigate_to('dashboard')

    def show_products(self):
        self.navigate_to('products')

    def show_sales(self):
        self.navigate_to('sales')

    def show_customers(self):
        self.navigate_to('customers')

    def show_reports(self):
        self.navigate_to('reports')

    def show_settings(self):
        self.navigate_to('settings')

    def set_active_nav_button(self, button_name):
        """Set the active navigation button and uncheck others."""
        if not hasattr(self, 'nav_list'):
            return

        for row in range(self.nav_list.count()):
            item = self.nav_list.item(row)
            if item is None:
                continue
            if item.data(Qt.ItemDataRole.UserRole) == button_name:
                self.nav_list.blockSignals(True)
                self.nav_list.setCurrentRow(row)
                self.nav_list.blockSignals(False)
                break

    def toggle_sidebar(self):
        self._sidebar_collapsed = not getattr(self, '_sidebar_collapsed', False)
        self.apply_sidebar_state()

    def apply_sidebar_state(self):
        if not hasattr(self, 'splitter'):
            return

        if getattr(self, '_sidebar_collapsed', False):
            self.splitter.setSizes([self._sidebar_collapsed_width, max(1, self.width() - self._sidebar_collapsed_width)])
            if hasattr(self, 'user_info_label'):
                self.user_info_label.setVisible(False)
            if hasattr(self, 'logout_btn'):
                self.logout_btn.setText("")
                self.logout_btn.setToolTip("Logout")
                self.logout_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
            if hasattr(self, 'nav_list'):
                for row in range(self.nav_list.count()):
                    item = self.nav_list.item(row)
                    if item is not None:
                        item.setText("")
        else:
            self.splitter.setSizes([self._sidebar_expanded_width, max(1, self.width() - self._sidebar_expanded_width)])
            if hasattr(self, 'user_info_label'):
                self.user_info_label.setVisible(True)
            if hasattr(self, 'logout_btn'):
                self.logout_btn.setText("Logout")
                self.logout_btn.setToolTip("")
                self.logout_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            if hasattr(self, 'nav_list'):
                for row in range(self.nav_list.count()):
                    item = self.nav_list.item(row)
                    if item is not None:
                        item.setText(item.toolTip())

    # Action handlers
    def new_sale(self):
        """Handle new sale action."""
        self.show_sales()

    def add_product(self):
        """Handle add product action."""
        self.show_products()

    def logout(self):
        """Handle logout action."""
        reply = QMessageBox.question(
            self, 'Logout', 'Are you sure you want to logout?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.current_user = None
            self._logging_out = True
            self.hide()
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            if app is not None and hasattr(app, 'show_login'):
                app.show_login()
            self.close()

    def closeEvent(self, event):
        """Handle window close event."""
        if getattr(self, '_logging_out', False):
            event.accept()
            return

        reply = QMessageBox.question(
            self, 'Exit Application', 'Are you sure you want to exit?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
