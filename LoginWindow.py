import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QFormLayout, QMessageBox, QDialog,
    QHBoxLayout, QSpacerItem, QSizePolicy, QToolButton, QComboBox,


)
from PyQt6.QtGui import (QPixmap, QFont, QPalette, QColor, QIcon)
from PyQt6.QtCore import QFileInfo
from PyQt6.QtCore import Qt
from Database import verify_user, register_pending_employee, create_database_and_tables


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PayRight - Login")
        icon_path = r"C:\\Users\\User\\Downloads\\PayRights.png"
        if QFileInfo(icon_path).exists():
            self.setWindowIcon(QIcon(icon_path))
        else:
            print("⚠️ PayRight logo not found — skipping icon.")

        self.setFixedSize(800, 600)
        create_database_and_tables()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo = QLabel()
        pixmap = QPixmap(r"C:\\Users\\User\\Downloads\\PayRights.png")
        if not pixmap.isNull():
            pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("PayRight")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 50, QFont.Weight.Bold))
        title.setObjectName("titleLabel")

        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addSpacing(20)

        form = QFormLayout()
        form.setFormAlignment(Qt.AlignmentFlag.AlignCenter)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setSpacing(15)

        label_font = QFont("Segoe UI", 12, QFont.Weight.Bold)
        label_palette = QPalette()
        label_palette.setColor(QPalette.ColorRole.WindowText, QColor("#333333"))

        user_label = QLabel("Username:")
        user_label.setFont(label_font)
        user_label.setPalette(label_palette)

        pass_label = QLabel("Password:")
        pass_label.setFont(label_font)
        pass_label.setPalette(label_palette)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Enter Username")
        self.user_input.setFont(QFont("Segoe UI", 12))
        self.user_input.setFixedWidth(400)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Enter Password")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setFont(QFont("Segoe UI", 12))
        self.pass_input.setFixedWidth(400)

        self.toggle_btn = QToolButton(self.pass_input)
        self.toggle_btn.setText("👁️")
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setStyleSheet("border: none; background: transparent; font-size: 14pt;")
        self.toggle_btn.clicked.connect(self.toggle_password_visibility)
        self.toggle_btn.setFixedSize(28, 28)

        frame_width = self.pass_input.style().pixelMetric(self.pass_input.style().PixelMetric.PM_DefaultFrameWidth)
        self.pass_input.setTextMargins(0, 0, self.toggle_btn.width() + frame_width, 0)
        self.pass_input.textChanged.connect(self.adjust_toggle_position)
        self.pass_input.resizeEvent = lambda event: self.adjust_toggle_position()

        form.addRow(user_label, self.user_input)
        form.addRow(pass_label, self.pass_input)

        layout.addLayout(form)
        layout.addSpacing(25)

        login_btn = QPushButton("Login")
        register_btn = QPushButton("Register")

        login_btn.setObjectName("loginButton")
        register_btn.setObjectName("registerButton")

        login_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        register_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.setFixedHeight(50)
        register_btn.setFixedHeight(50)
        login_btn.setFixedWidth(220)
        register_btn.setFixedWidth(220)

        layout.addWidget(login_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(register_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.setLayout(layout)

        login_btn.clicked.connect(self.login_action)
        register_btn.clicked.connect(self.register_action)

    def adjust_toggle_position(self, *args):
        frame_width = self.pass_input.style().pixelMetric(self.pass_input.style().PixelMetric.PM_DefaultFrameWidth)
        self.toggle_btn.move(
            self.pass_input.width() - self.toggle_btn.width() - frame_width - 3,
            (self.pass_input.height() - self.toggle_btn.height()) // 2
        )

    def toggle_password_visibility(self):
        if self.pass_input.echoMode() == QLineEdit.EchoMode.Password:
            self.pass_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_btn.setText("🙈")
        else:
            self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_btn.setText("👁️")

    def login_action(self):
        from Database import get_connection
        username = self.user_input.text().strip()
        password = self.pass_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Missing", "Please fill in your account.")
            return

        role = verify_user(username, password)

        if role:
            # ✅ Show success message before opening the dashboard
            QMessageBox.information(
                self,
                "Login Successful",
                f"Welcome, {username.title()}!\nYou have successfully logged in."
            )
            self.hide()
            self.open_dashboard(role, username)
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM pending_employees WHERE username=%s", (username,))
            pending = cur.fetchone()
            conn.close()

            if pending:
                QMessageBox.information(self, "Under Review", "Your registration is under review by the admin.")
            else:
                QMessageBox.warning(self, "Invalid", "Incorrect username or password.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Database error:\n{e}")

    def open_dashboard(self, role, username):
        from DashboardWindow import DashboardWindow
        self.dashboard = DashboardWindow(role, username)
        self.dashboard.login_window = self
        self.dashboard.show()

    def register_action(self):
        dialog = RegisterDialog(self)
        dialog.exec()

    def clear_credentials(self):
        self.user_input.clear()
        self.pass_input.clear()


class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register New Employee")
        self.setFixedSize(500, 500)
        layout = QVBoxLayout(self)

        title = QLabel("🧾 Employee Registration")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(15)
        font = QFont("Segoe UI", 12)
        label_font = QFont("Segoe UI", 12, QFont.Weight.Bold)

        self.username = QLineEdit()
        self.username.setFont(font)
        self.username.setPlaceholderText("Enter your username")

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setFont(font)
        self.password.setPlaceholderText("Enter your password")

        self.name = QLineEdit()
        self.name.setFont(font)
        self.name.setPlaceholderText("Enter your full name")

        self.position = QComboBox()
        self.position.setFont(font)
        self.position.addItems([
            "Select Position",
            "Manager",
            "Supervisor",
            "Accountant",
            "HR Officer",
            "IT Specialist",
            "Sales Executive",
            "Marketing Coordinator",
            "Engineer",
            "Technician",
            "Customer Service Representative"
        ])
        self.position.setCurrentIndex(0)

        self.department = QComboBox()
        self.department.setFont(font)
        self.department.addItems([
            "Select Department",
            "Human Resources",
            "Finance",
            "IT Department",
            "Sales",
            "Marketing",
            "Engineering",
            "Operations",
            "Customer Support"
        ])
        self.department.setCurrentIndex(0)

        self.salary = QLineEdit()
        self.salary.setFont(font)
        self.salary.setPlaceholderText("Enter salary amount (₱)")
        self.salary.setMaxLength(15)
        self.salary.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.salary.textChanged.connect(self.live_format_salary)

        form.addRow(QLabel("Username:", font=label_font), self.username)
        form.addRow(QLabel("Password:", font=label_font), self.password)
        form.addRow(QLabel("Full Name:", font=label_font), self.name)
        form.addRow(QLabel("Position:", font=label_font), self.position)
        form.addRow(QLabel("Department:", font=label_font), self.department)
        form.addRow(QLabel("Salary:", font=label_font), self.salary)

        layout.addLayout(form)
        layout.addSpacing(20)

        btn_layout = QHBoxLayout()
        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setFixedHeight(50)
        self.submit_btn.setFixedWidth(180)
        self.submit_btn.setObjectName("submitButton")

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedHeight(50)
        self.cancel_btn.setFixedWidth(180)
        self.cancel_btn.setObjectName("cancelButton")

        btn_layout.addWidget(self.submit_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.submit_btn.clicked.connect(self.submit)
        self.cancel_btn.clicked.connect(self.reject)

    def live_format_salary(self):
        """Format salary input naturally as ₱ while typing."""
        text = self.salary.text()
        clean = text.replace("₱", "").replace(",", "").strip()
        clean = ''.join(ch for ch in clean if ch.isdigit() or ch == '.')

        if clean.count('.') > 1:
            parts = clean.split('.')
            clean = parts[0] + '.' + ''.join(parts[1:])

        if clean == "":
            self.salary.blockSignals(True)
            self.salary.setText("")
            self.salary.blockSignals(False)
            return

        if '.' in clean:
            integer_part, decimal_part = clean.split('.', 1)
            integer_part = integer_part or "0"
            formatted_int = f"{int(integer_part):,}"
            formatted = f"₱{formatted_int}.{decimal_part}"
        else:
            try:
                formatted_int = f"{int(clean):,}"
                formatted = f"₱{formatted_int}"
            except ValueError:
                formatted = "₱"

        cursor_pos = self.salary.cursorPosition()
        self.salary.blockSignals(True)
        self.salary.setText(formatted)
        self.salary.blockSignals(False)
        self.salary.setCursorPosition(len(formatted))

    def submit(self):
        username = self.username.text().strip()
        password = self.password.text().strip()
        name = self.name.text().strip()
        position = self.position.currentText()
        department = self.department.currentText()
        salary = self.salary.text().replace("₱", "").replace(",", "").strip()

        if not all([username, password, name]) or position == "Select Position" or department == "Select Department" or not salary:
            QMessageBox.warning(self, "Incomplete", "Please fill in all fields.")
            return

        try:
            salary_val = float(salary)
        except ValueError:
            QMessageBox.warning(self, "Invalid", "Salary must be a valid number.")
            return

        if register_pending_employee(username, password, name, position, department, salary_val):
            QMessageBox.information(self, "Registered", "Your registration is pending admin approval.")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Registration failed.")