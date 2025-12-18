import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QIcon

# Import application modules
from .controllers import init_db, db_session
from .views.login import LoginWindow
from .views.main_window import MainWindow
from .utils.helpers import get_icon_path, load_icon

class POSApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName("POS Desktop")
        self.setApplicationDisplayName("Point of Sale System")
        self.setApplicationVersion("1.0.0")
        
        # Initialize settings
        self.settings = QSettings("POS", "POS Desktop")
        
        # Initialize database
        try:
            init_db()
        except Exception as e:
            QMessageBox.critical(
                None,
                "Database Error",
                "Failed to connect/initialize the database.\n\n"
                "Check your .env settings (DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME).\n\n"
                f"Error: {e}",
            )
            raise SystemExit(1)
        
        # Create main window
        self.main_window = MainWindow()
        
        # Show login window first
        self.show_login()
    
    def show_login(self):
        self.login_window = LoginWindow()
        self.login_window.login_successful.connect(self.on_login_success)
        self.login_window.show()
    
    def on_login_success(self, user):
        self.current_user = user
        # Prevent the login window close from quitting the whole app.
        if hasattr(self.login_window, 'quit_on_close'):
            self.login_window.quit_on_close = False
        self.login_window.close()
        self.main_window.set_user(user)
        self.main_window.show()

def main():
    # Set up high DPI scaling
    # Qt6 enables high-DPI scaling by default; some attributes were removed.
    if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    # Create and run application
    app = POSApp(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')  # Modern look
    
    # Set application icon if available
    icon = load_icon("app_icon.png")
    if icon is not None and not icon.isNull():
        app.setWindowIcon(icon)
    
    # Run the application
    ret = app.exec()
    
    # Clean up database session when app exits
    db_session.remove()
    
    sys.exit(ret)

if __name__ == '__main__':
    main()
