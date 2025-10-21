import sys
from PyQt6.QtWidgets import QApplication
from LoginWindow import LoginWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    with open("style.qss", "r") as f:
        app.setStyleSheet(f.read())
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
