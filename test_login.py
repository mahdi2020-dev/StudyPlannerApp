from app.ui.login_window import LoginWindow
from PyQt6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
window = LoginWindow()
print("Login window created successfully!")
