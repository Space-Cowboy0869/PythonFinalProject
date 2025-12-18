from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox,
    QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QPixmap
from ..models import User
from ..controllers import db_session
from ..utils.helpers import get_icon_path, load_icon


class LoginWindow(QWidget):
    login_successful = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.quit_on_close = True
        self.setWindowTitle("POS System ΓÇô Login")
        self.setFixedSize(720, 420)

        self.setup_ui()

    def setup_ui(self):
        # =======================
        # GLOBAL STYLES
        # =======================
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }

            QFrame#LeftPanel {
                background-color: #1677ff;
            }

            QLabel#SystemTitle {
                color: white;
                font-size: 26px;
                font-weight: 700;
            }

            QLabel#SystemSubtitle {
                color: rgba(255,255,255,0.85);
                font-size: 13px;
            }

            QLabel#FooterText {
                color: rgba(255,255,255,0.6);
                font-size: 11px;
            }

            QFrame#RightPanel {
                background-color: white;
            }

            QLabel#LoginTitle {
                font-size: 22px;
                font-weight: 700;
                color: #111827;
            }

            QLabel#LoginSubtitle {
                font-size: 13px;
                color: #6b7280;
            }

            QLineEdit {
                height: 42px;
                border-radius: 6px;
                border: 1px solid #d1d5db;
                padding-left: 14px;
                font-size: 14px;
            }

            QLineEdit:focus {
                border: 1px solid #1677ff;
            }

            QPushButton#LoginButton {
                height: 44px;
                border-radius: 6px;
                background-color: #1677ff;
                color: white;
                font-size: 14px;
                font-weight: 600;
                border: none;
            }

            QPushButton#LoginButton:hover {
                background-color: #0f63d1;
            }

            QPushButton#LinkButton {
                background: transparent;
                border: none;
                color: #1677ff;
                font-size: 12px;
            }

            QPushButton#LinkButton:hover {
                text-decoration: underline;
            }
        """)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # =======================
        # LEFT PANEL
        # =======================
        left_panel = QFrame()
        left_panel.setObjectName("LeftPanel")
        left_panel.setFixedWidth(280)

        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(30, 40, 30, 40)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # BIG LOGO
        logo_path = get_icon_path("logoo.png")
        if logo_path:
            pixmap = QPixmap(logo_path).scaled(
                140, 140,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            logo = QLabel()
            logo.setPixmap(pixmap)
            logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            left_layout.addWidget(logo)

        left_layout.addSpacing(20)

        system_title = QLabel("POS System")
        system_title.setObjectName("SystemTitle")
        system_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(system_title)

        left_layout.addSpacing(6)

        system_subtitle = QLabel(
            "GREEN-GOBLIN COMPUTER PARTS\nAND SERVICES"
        )
        system_subtitle.setObjectName("SystemSubtitle")
        system_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        system_subtitle.setWordWrap(True)
        left_layout.addWidget(system_subtitle)

        left_layout.addStretch()

        footer = QLabel()
        footer.setObjectName("FooterText")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(footer)

        # =======================
        # RIGHT PANEL
        # =======================
        right_panel = QFrame()
        right_panel.setObjectName("RightPanel")

        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(60, 40, 60, 40)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        login_title = QLabel("Sign In")
        login_title.setObjectName("LoginTitle")
        login_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(login_title)

        right_layout.addSpacing(6)

        login_subtitle = QLabel("Enter your credentials to continue")
        login_subtitle.setObjectName("LoginSubtitle")
        login_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(login_subtitle)

        right_layout.addSpacing(26)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        right_layout.addWidget(self.username_input)

        right_layout.addSpacing(14)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        right_layout.addWidget(self.password_input)

        right_layout.addSpacing(22)

        login_btn = QPushButton("Sign In")
        login_btn.setObjectName("LoginButton")
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.clicked.connect(self.handle_login)
        self.password_input.returnPressed.connect(login_btn.click)
        right_layout.addWidget(login_btn)

        right_layout.addSpacing(14)

        contact_btn = QPushButton("Forgot Password?")
        contact_btn.setObjectName("LinkButton")
        contact_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        contact_btn.clicked.connect(self.handle_forgot_password)
        right_layout.addWidget(contact_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)

        # Window icon
        icon = load_icon("app_icon.png")
        if icon and not icon.isNull():
            self.setWindowIcon(icon)

    # =======================
    # LOGIN LOGIC
    # =======================
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self.show_error("Please enter both username and password.")
            return

        user = db_session.query(User).filter(User.username == username).first()

        if user and user.check_password(password):
            self.login_successful.emit(user)
        else:
            self.show_error("Invalid username or password.")
            self.password_input.clear()
            self.shake_animation()

    def handle_forgot_password(self):
        QMessageBox.information(
            self,
            "Password Recovery",
            "Please contact your system administrator to reset your password."
        )

    def show_error(self, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Authentication Error")
        msg.setText(message)
        msg.exec()

    def shake_animation(self):
        animation = QPropertyAnimation(self, b"pos")
        animation.setDuration(450)
        animation.setEasingCurve(QEasingCurve.Type.OutBounce)

        pos = self.pos()
        animation.setStartValue(pos)
        animation.setKeyValueAt(0.25, pos + QPoint(10, 0))
        animation.setKeyValueAt(0.5, pos - QPoint(10, 0))
        animation.setKeyValueAt(0.75, pos + QPoint(5, 0))
        animation.setEndValue(pos)

        animation.start()

    def closeEvent(self, event):
        if getattr(self, "quit_on_close", True):
            from PyQt6.QtWidgets import QApplication
            QApplication.quit()
        else:
            event.accept()
