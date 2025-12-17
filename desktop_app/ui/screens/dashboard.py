from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QGridLayout, QSizePolicy, 
                            QScrollArea, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont
from ...models import Transaction, Product
from ...database import db_session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from ...utils.helpers import format_currency, load_icon

class DashboardScreen(QWidget):
    """Dashboard screen showing key metrics and quick actions."""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Set up the dashboard UI components."""
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: #f5f5f5; border: none; }")
        
        # Container widget
        container = QWidget()
        scroll.setWidget(container)
        
        # Main layout
        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Header section
        header_layout = QHBoxLayout()
        
        # Title
        title = QLabel("Dashboard")
        title.setStyleSheet("""
            font-size: 32px; 
            font-weight: 700; 
            color: #00b050;
            letter-spacing: -0.5px;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Date/Time
        current_time = datetime.now().strftime("%B %d, %Y • %I:%M %p")
        date_label = QLabel(current_time)
        date_label.setStyleSheet("""
            font-size: 14px; 
            color: #666666;
            font-weight: 500;
        """)
        header_layout.addWidget(date_label)
        
        layout.addLayout(header_layout)
        layout.addSpacing(10)
        
        # Metrics cards section
        metrics_container = QFrame()
        metrics_container.setStyleSheet("QFrame { background: transparent; }")
        self.metrics_layout = QHBoxLayout(metrics_container)
        self.metrics_layout.setSpacing(20)
        
        # Create metric cards
        self.sales_card = self.create_metric_card(
            "Total Sales", "0.00", "sales.png", "#00b050", "↑ 12.5%"
        )
        self.orders_card = self.create_metric_card(
            "Orders", "0", "orders.png", "#00b050", "↑ 8.2%"
        )
        self.products_card = self.create_metric_card(
            "Products", "0", "products.png", "#00b050", "5 low stock"
        )
        self.customers_card = self.create_metric_card(
            "Customers", "0", "customers.png", "#00b050", "↑ 15.3%"
        )
        
        # Add cards to layout
        self.metrics_layout.addWidget(self.sales_card)
        self.metrics_layout.addWidget(self.orders_card)
        self.metrics_layout.addWidget(self.products_card)
        self.metrics_layout.addWidget(self.customers_card)
        
        layout.addWidget(metrics_container)
        layout.addSpacing(10)
        
        # Quick Actions section
        actions_header = self.create_section_header("Quick Actions")
        layout.addWidget(actions_header)
        layout.addSpacing(5)
        
        # Quick action buttons in a grid (2x2)
        actions_grid = QGridLayout()
        actions_grid.setSpacing(20)
        
        # Create action cards
        new_sale_card = self.create_quick_action_card("New Sale", "new_sale.png", "#00b050", "Create a new sale transaction")
        add_product_card = self.create_quick_action_card("Add Product", "add_product.png", "#00b050", "Add new product to inventory")
        view_inventory_card = self.create_quick_action_card("View Inventory", "inventory.png", "#00b050", "Check stock levels and products")
        generate_report_card = self.create_quick_action_card("Generate Report", "report.png", "#00b050", "Create sales and analytics reports")
        
        # Add to grid (2x2 layout)
        actions_grid.addWidget(new_sale_card, 0, 0)
        actions_grid.addWidget(add_product_card, 0, 1)
        actions_grid.addWidget(view_inventory_card, 1, 0)
        actions_grid.addWidget(generate_report_card, 1, 1)
        
        layout.addLayout(actions_grid)
        layout.addStretch()
        
        # Set main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def create_metric_card(self, title, value, icon_name, color, subtitle=""):
        """Create a metric card widget with modern design."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 12px;
                padding: 0px;
            }}
        """)
        card.setMinimumHeight(140)
        self.add_shadow(card)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Icon and color bar
        top_layout = QHBoxLayout()
        
        # Color indicator
        color_bar = QFrame()
        color_bar.setFixedSize(4, 40)
        color_bar.setStyleSheet(f"background-color: {color}; border-radius: 2px;")
        top_layout.addWidget(color_bar)
        top_layout.addSpacing(12)
        
        # Icon
        icon_label = QLabel()
        icon_label.setFixedSize(40, 40)
        icon_label.setStyleSheet(f"""
            background-color: {color};
            border-radius: 8px;
            padding: 8px;
        """)
        icon = load_icon(icon_name)
        if icon is not None and not icon.isNull():
            icon_label.setPixmap(icon.pixmap(24, 24))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_layout.addWidget(icon_label)
        
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: #666666;
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """)
        layout.addWidget(title_label)
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("""
            font-size: 28px;
            font-weight: 700;
            color: #1a1a1a;
        """)
        layout.addWidget(self.value_label)
        
        # Subtitle/Change indicator
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("""
                color: #00b050;
                font-size: 12px;
                font-weight: 600;
            """)
            layout.addWidget(subtitle_label)
        
        layout.addStretch()
        
        # Store reference to update later
        setattr(self, f"{title.lower().replace(' ', '_')}_value", self.value_label)
        
        return card
    
    def create_section_header(self, title):
        """Create a modern section header."""
        header = QLabel(title)
        header.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: 700;
                color: #00b050;
                padding-bottom: 8px;
            }
        """)
        return header
    
    def create_quick_action_card(self, text, icon_name, color, description):
        """Create a modern quick action card."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                padding: 20px;
            }
            QFrame:hover {
                background: #f8f9fa;
            }
        """)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setMinimumHeight(120)
        self.add_shadow(card)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(12)
        
        # Icon
        icon_label = QLabel()
        icon_label.setFixedSize(48, 48)
        icon_label.setStyleSheet(f"""
            background-color: {color};
            border-radius: 10px;
            padding: 10px;
        """)
        icon = load_icon(icon_name)
        if icon is not None and not icon.isNull():
            icon_label.setPixmap(icon.pixmap(28, 28))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(text)
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #1a1a1a;
        """)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            font-size: 13px;
            color: #666666;
        """)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addStretch()
        
        # Make it clickable
        card.mousePressEvent = lambda e: self.handle_quick_action(text)
        
        return card
    
    def add_shadow(self, widget):
        """Add drop shadow effect to a widget."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(Qt.GlobalColor.gray)
        widget.setGraphicsEffect(shadow)
    
    def handle_quick_action(self, action_name):
        """Handle quick action clicks."""
        if action_name == "New Sale":
            self.on_new_sale()
        elif action_name == "Add Product":
            self.on_add_product()
        elif action_name == "View Inventory":
            self.on_view_inventory()
        elif action_name == "Generate Report":
            self.on_generate_report()
    
    def load_data(self):
        """Load data for the dashboard."""
        try:
            # Calculate date ranges
            today = datetime.utcnow().date()
            last_month = today - timedelta(days=30)
            
            # Get total sales for the last 30 days
            total_sales = db_session.query(
                func.sum(Transaction.total)
            ).filter(
                Transaction.created_at >= last_month
            ).scalar() or 0
            
            # Get total orders for the last 30 days
            total_orders = db_session.query(
                func.count(Transaction.id)
            ).filter(
                Transaction.created_at >= last_month
            ).scalar() or 0
            
            # Get total number of products
            total_products = db_session.query(
                func.count(Product.id)
            ).scalar() or 0
            
            # Get total unique customers (approximate)
            total_customers = db_session.query(
                func.count(func.distinct(Transaction.customer_name))
            ).scalar() or 0
            
            # Update UI with the data
            self.total_sales_value.setText(format_currency(total_sales))
            self.orders_value.setText(str(total_orders))
            self.products_value.setText(str(total_products))
            self.customers_value.setText(str(total_customers))
                
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
            import traceback
            traceback.print_exc()
    
    # Quick action handlers
    def on_new_sale(self):
        """Handle new sale action."""
        win = self.window()
        if hasattr(win, 'show_sales'):
            win.show_sales()
    
    def on_add_product(self):
        """Handle add product action."""
        win = self.window()
        if hasattr(win, 'show_products'):
            win.show_products()
    
    def on_view_inventory(self):
        """Handle view inventory action."""
        win = self.window()
        if hasattr(win, 'show_products'):
            win.show_products()
    
    def on_generate_report(self):
        """Handle generate report action."""
        win = self.window()
        if hasattr(win, 'show_reports'):
            win.show_reports()