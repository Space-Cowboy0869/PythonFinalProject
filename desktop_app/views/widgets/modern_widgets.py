"""Modern widget components for POS UI."""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QWidget, QDialog, QDialogButtonBox,
    QGraphicsDropShadowEffect, QAbstractItemView
)
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QIcon
from ...utils.helpers import load_icon


class ModernCard(QFrame):
    """Modern card widget with shadow effect."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        self.add_shadow()
    
    def add_shadow(self):
        """Add drop shadow effect."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)


class MetricCard(QFrame):
    """Metric card widget for displaying KPIs."""
    
    def __init__(self, title="", value="0", color="#00b050", parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 8px;
                border-left: 4px solid """ + color + """;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #666666; font-size: 12px; font-weight: 600;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("color: #1a1a1a; font-size: 24px; font-weight: 700;")
        layout.addWidget(value_label)
        
        self.add_shadow()
    
    def add_shadow(self):
        """Add drop shadow effect."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)


class ActionButton(QPushButton):
    """Modern action button with icon and color."""
    
    def __init__(self, text="", icon_name="", color="#00b050", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {self._shade_color(color, -10)};
            }}
            QPushButton:pressed {{
                background-color: {self._shade_color(color, -20)};
            }}
        """)
        
        if icon_name:
            icon = load_icon(icon_name)
            if icon:
                self.setIcon(icon)
                self.setIconSize(QSize(18, 18))
    
    @staticmethod
    def _shade_color(hex_color, percent):
        """Shade a hex color by percent."""
        try:
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            r = max(0, min(255, int(rgb[0] * (1 + percent / 100))))
            g = max(0, min(255, int(rgb[1] * (1 + percent / 100))))
            b = max(0, min(255, int(rgb[2] * (1 + percent / 100))))
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return hex_color


class IconButton(QPushButton):
    """Icon-only button with optional text tooltip."""
    
    def __init__(self, icon_name="", tooltip="", size=24, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border: 1px solid #00b050;
            }
        """)
        
        if tooltip:
            self.setToolTip(tooltip)
        
        if icon_name:
            icon = load_icon(icon_name)
            if icon:
                self.setIcon(icon)
                self.setIconSize(QSize(size - 8, size - 8))


class ModernTable(QTableWidget):
    """Modern styled table widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTableWidget {
                background-color: white;
                color: #1a1a1a;
                alternate-background-color: #f5f5f5;
                gridline-color: #e0e0e0;
                selection-background-color: #00b050;
            }
            QTableWidget::item {
                padding: 4px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #00b050;
                color: white;
            }
            QHeaderView::section {
                background-color: #000000;
                color: white;
                padding: 6px;
                border: none;
                font-weight: 600;
                font-size: 12px;
            }
            QTableWidget::horizontalHeader {
                border-top: 1px solid #e0e0e0;
            }
        """)
        
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(False)


class SearchBar(QLineEdit):
    """Modern search input with styling."""
    
    def __init__(self, placeholder="Search...", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #00b050;
            }
        """)
        self.setMinimumHeight(36)


class FilterComboBox(QComboBox):
    """Modern combo box for filtering."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QComboBox {
                padding: 6px 10px;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                background-color: white;
                font-size: 13px;
            }
            QComboBox:focus {
                border: 2px solid #00b050;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
            }
        """)
        self.setMinimumHeight(34)


class ModernDialog(QDialog):
    """Modern dialog with custom layout."""
    
    def __init__(self, title="Dialog", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                padding: 8px 10px;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                background-color: white;
                font-size: 13px;
                min-height: 28px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border: 2px solid #00b050;
            }
            QLabel {
                color: #333333;
                font-size: 12px;
                font-weight: 500;
            }
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(12)
        
        self.form_layout = QVBoxLayout()
        self.form_layout.setSpacing(12)
        self.layout.addLayout(self.form_layout)
    
    def add_form_fields(self, fields):
        """Add form fields from list of (label, widget) tuples."""
        for label_text, widget in fields:
            field_layout = QVBoxLayout()
            field_layout.setSpacing(4)
            
            if label_text:
                label = QLabel(label_text)
                label.setStyleSheet("font-weight: 600;")
                field_layout.addWidget(label)
            
            field_layout.addWidget(widget)
            self.form_layout.addLayout(field_layout)
    
    def add_buttons(self, ok_text="OK", cancel_text="Cancel"):
        """Add OK and Cancel buttons."""
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_btn = ActionButton(ok_text, color="#00b050")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = ActionButton(cancel_text, color="#f44336")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        self.layout.addLayout(button_layout)


class StatusBadge(QLabel):
    """Status badge widget."""
    
    def __init__(self, text="", status="info", parent=None):
        super().__init__(text, parent)
        self.set_status(status)
        self.setStyleSheet("""
            QLabel {
                padding: 4px 10px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 600;
            }
        """)
    
    def set_status(self, status):
        """Set status color."""
        colors = {
            "success": ("#00b050", "#e8f5e9"),
            "warning": ("#ff9800", "#fff3e0"),
            "error": ("#f44336", "#ffebee"),
            "info": ("#2196f3", "#e3f2fd"),
        }
        
        if status in colors:
            fg, bg = colors[status]
            self.setStyleSheet(f"""
                QLabel {{
                    color: {fg};
                    background-color: {bg};
                    border: 1px solid {fg};
                    padding: 4px 10px;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: 600;
                }}
            """)


class SectionHeader(QLabel):
    """Section header widget."""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 700;
                color: #00b050;
                padding: 8px 0px;
                border-bottom: 2px solid #00b050;
            }
        """)
        self.setMinimumHeight(32)


class QuickActionCard(QFrame):
    """Quick action card widget."""
    
    def __init__(self, title="", icon_name="", color="#00b050", parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
            QFrame:hover {
                border: 1px solid """ + color + """;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Icon
        icon_label = QLabel()
        icon_label.setFixedSize(40, 40)
        icon_label.setStyleSheet(f"""
            background-color: {color};
            border-radius: 8px;
        """)
        if icon_name:
            icon = load_icon(icon_name)
            if icon:
                icon_label.setPixmap(icon.pixmap(28, 28))
                icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #1a1a1a;")
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        self.add_shadow()
    
    def add_shadow(self):
        """Add drop shadow effect."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)


class ProductCard(QFrame):
    """Product card widget for product grid view."""
    
    def __init__(self, product_name="", price="$0.00", image_pixmap=None, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
            QFrame:hover {
                border: 2px solid #00b050;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Product image
        if image_pixmap:
            image_label = QLabel()
            image_label.setPixmap(image_pixmap)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(image_label)
        
        # Product name
        name_label = QLabel(product_name)
        name_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #1a1a1a;")
        name_label.setWordWrap(True)
        layout.addWidget(name_label)
        
        # Price
        price_label = QLabel(price)
        price_label.setStyleSheet("font-size: 14px; font-weight: 700; color: #00b050;")
        layout.addWidget(price_label)
        
        layout.addStretch()
        
        self.add_shadow()
    
    def add_shadow(self):
        """Add drop shadow effect."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)


class LoadingSpinner(QFrame):
    """Loading spinner animation widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent; border: none;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel("Loading...")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-size: 13px;
            color: #666666;
            font-weight: 600;
        """)
        layout.addWidget(self.label)
        
        self.animation = None
    
    def start_animation(self):
        """Start loading animation."""
        if not self.animation:
            self.animation = QPropertyAnimation(self, b"opacity")
            self.animation.setDuration(800)
            self.animation.setStartValue(0.3)
            self.animation.setEndValue(1.0)
            self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.animation.start()
    
    def stop_animation(self):
        """Stop loading animation."""
        if self.animation:
            self.animation.stop()
