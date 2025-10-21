import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget,
    QFrame, QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox, QFormLayout,
    QDialog, QDialogButtonBox, QDateEdit, QComboBox, QApplication,  QGridLayout
)
from PyQt6.QtCore import Qt, QDate, QTimer, QTime
from PyQt6.QtGui import QFont, QPixmap, QDoubleValidator, QIcon
from PyQt6.QtCore import QFileInfo
from Database import get_connection, fetch_pending_employees, approve_employee, is_employee_approved


class DashboardWindow(QWidget):
    def __init__(self, role, username):
        super().__init__()
        self.role = role
        self.username = username
        self.setWindowTitle(f"{role.title()} Dashboard")
        self.setFixedSize(1200, 700)

        icon_path = r"C:\\Users\\User\\Downloads\\PayRights.png"
        if QFileInfo(icon_path).exists():
            self.setWindowIcon(QIcon(icon_path))
        else:
            print("⚠️ PayRight logo not found — skipping icon.")

        self.init_ui()
        self.load_tables()
        QTimer.singleShot(0, self.apply_role_restrictions)

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        sidebar = QFrame()
        sidebar.setFixedWidth(230)
        sidebar.setObjectName("sidebar")


        sidebar = QFrame()
        sidebar.setFixedWidth(230)
        sidebar.setObjectName("sidebar")

        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        sb_layout.setSpacing(15)

        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pixmap = QPixmap(r"C:\\Users\\User\\Downloads\\PayRights.png")
        if not pixmap.isNull():
            pixmap = pixmap.scaled(140, 140, Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(pixmap)
        else:
            logo_label.setText("PayRight")
            logo_label.setFont(QFont("Arial", 22, QFont.Weight.Bold))
            logo_label.setStyleSheet("color: black;")

        self.btn_dashboard = QPushButton("🏠 Dashboard")
        self.btn_payroll = QPushButton("💰 Payroll")
        self.btn_record = QPushButton("📁 Records")
        self.btn_attendance = QPushButton("📋 Attendance")
        self.btn_pending = QPushButton("🧾 Approvals")
        self.btn_logout = QPushButton("🚪 Logout")

        for b in [self.btn_dashboard, self.btn_payroll, self.btn_record, self.btn_attendance, self.btn_pending,
                  self.btn_logout]:
            b.setObjectName("sideButton")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setFixedHeight(50)
            b.setFixedWidth(180)
            b.setStyleSheet("""
                QPushButton#sideButton {
                    text-align: left;
                    padding-left: 25px;
                    font-size: 13pt;
                    font-weight: bold
                    color: #222;
                    border: none;
                    border-radius: 8px;
                }
                QPushButton#sideButton:hover {
                    background-color: #f3f3f3;
                }
                QPushButton#sideButton:pressed {
                    background-color: #e0e0e0;
                }
            """)

        sb_layout.addWidget(logo_label)
        sb_layout.addSpacing(15)
        sb_layout.addWidget(self.btn_dashboard)
        sb_layout.addWidget(self.btn_payroll)
        sb_layout.addWidget(self.btn_record)
        sb_layout.addWidget(self.btn_attendance)
        sb_layout.addWidget(self.btn_pending)
        sb_layout.addStretch()
        sb_layout.addWidget(self.btn_logout)

        self.stack = QStackedWidget()

        dash_page = QWidget()
        dash_layout = QVBoxLayout(dash_page)
        dash_layout.setContentsMargins(20, 20, 20, 20)

        top_bar = QHBoxLayout()
        top_bar.setAlignment(Qt.AlignmentFlag.AlignRight)
        top_bar.setSpacing(10)

        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.time_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        logo = QLabel()
        pixmap = QPixmap("assets/PayRight.png")
        if not pixmap.isNull():
            pixmap = pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
            logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        top_bar.addWidget(self.time_label)
        top_bar.addWidget(logo)
        dash_layout.addLayout(top_bar)

        self.welcome_label = QLabel(f"👋 Welcome, {self.username.title()}!")
        self.welcome_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.welcome_label.setStyleSheet("color: #222; margin-top: 10px; margin-bottom: 15px;")
        dash_layout.addWidget(self.welcome_label)

        #Dashboard Section
        stats_container = QFrame()
        stats_layout = QGridLayout(stats_container)
        stats_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_layout.setHorizontalSpacing(80)
        stats_layout.setVerticalSpacing(50)

        def create_stat_box(title_text, big=False):
            box = QFrame()
            box.setObjectName("statsBox")
            if big:
                box.setStyleSheet("""
                    QFrame#statsBox {
                        background-color: transparent;
                        border: none;
                        padding: 30px;
                    }
                    QLabel#countLabel {
                        font-size: 54px;
                        font-weight: bold;
                        color: #1E1E1E;
                    }
                    QLabel#descLabel {
                        font-size: 18pt;
                        color: #555;
                    }
                """)
            else:
                box.setStyleSheet("""
                    QFrame#statsBox {
                        background-color: transparent;
                        border: none;
                        padding: 20px;
                    }
                    QLabel#countLabel {
                        font-size: 40px;
                        font-weight: bold;
                        color: #1E1E1E;
                    }
                    QLabel#descLabel {
                        font-size: 14pt;
                        color: #555;
                    }
                """)
            layout = QVBoxLayout(box)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.setSpacing(6)
            count_label = QLabel("0")
            count_label.setObjectName("countLabel")
            count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            desc_label = QLabel(title_text)
            desc_label.setObjectName("descLabel")
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(count_label)
            layout.addWidget(desc_label)
            return box, count_label

        if self.role == "admin":
            self.employee_box, self.employee_count_label = create_stat_box("Total Employees")
            self.payroll_box, self.payroll_count_label = create_stat_box("Total Payroll Records")
            self.pending_box, self.pending_count_label = create_stat_box("Pending Approvals")
            self.netpay_box, self.netpay_total_label = create_stat_box("Total Net Payroll")

            stats_layout.addWidget(self.employee_box, 0, 0)
            stats_layout.addWidget(self.payroll_box, 0, 1)
            stats_layout.addWidget(self.pending_box, 1, 0)
            stats_layout.addWidget(self.netpay_box, 1, 1)
        else:
            self.netpay_box, self.netpay_total_label = create_stat_box("Total Net Payroll", big=True)
            stats_layout.addWidget(self.netpay_box, 0, 0, Qt.AlignmentFlag.AlignCenter)

        dash_layout.addWidget(stats_container, alignment=Qt.AlignmentFlag.AlignCenter)

        announce_title = QLabel("📢 Announcements")
        announce_title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        announce_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        announce_title.setStyleSheet("margin-top: 30px; color: #333;")

        self.announcement_label = QLabel(
            "• Payday will be every 15th and 30th of the month.\n"
            "• Employees must time in/out properly to ensure accurate payroll records.\n"
            "• HR reminders: Submit leave requests at least 3 days in advance."
        )
        self.announcement_label.setFont(QFont("Segoe UI", 11))
        self.announcement_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.announcement_label.setWordWrap(True)
        self.announcement_label.setStyleSheet("""
            background-color: #fdfdfd;
            border: 1px solid #ccc;
            border-radius: 10px;
            padding: 10px;
            margin-top: 8px;
        """)

        dash_layout.addWidget(announce_title)
        dash_layout.addWidget(self.announcement_label)

        if self.role == "admin":
            self.edit_announcement_btn = QPushButton("✏️ Edit Announcements")
            self.edit_announcement_btn.setObjectName("largeButton")
            self.edit_announcement_btn.setFixedHeight(45)
            self.edit_announcement_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            self.edit_announcement_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.edit_announcement_btn.clicked.connect(self.open_announcement_editor)
            dash_layout.addWidget(self.edit_announcement_btn)

        dash_layout.addStretch()

        self.stack.addWidget(dash_page)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        self.payroll_table = QTableWidget()
        self.payroll_table.setColumnCount(8)
        self.payroll_table.setHorizontalHeaderLabels([
            "Date", "Employee", "Position", "Base", "Overtime", "Allowance", "Deductions", "Net Pay"
        ])
        self.payroll_table.setMinimumHeight(460)
        self.payroll_table.verticalHeader().setDefaultSectionSize(40)
        self.payroll_table.horizontalHeader().setDefaultSectionSize(140)

        self.payroll_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.payroll_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.payroll_table.setAlternatingRowColors(True)
        self.payroll_table.setStyleSheet("""
            QTableWidget {
                font-size: 11pt;
                selection-background-color: #cce5ff;
                selection-color: #000;
                gridline-color: #ddd;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                font-weight: bold;
            }
        """)

        self.payroll_table.cellDoubleClicked.connect(self.show_payslip_dialog)

        # Payroll Section
        pay_layout = QVBoxLayout()
        pay_layout.setContentsMargins(20, 20, 20, 20)

        if self.role == "admin":
            self.add_btn = QPushButton("➕ Generate Payroll Record")
            self.add_btn.setObjectName("generatePayrollButton")
            self.add_btn.clicked.connect(self.add_payroll_record)
            self.add_btn.setFixedSize(400, 400)
            self.add_btn.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.add_btn.setStyleSheet("""
                QPushButton#generatePayrollButton {
                    background-color: #ffb74d;      /* warm orange */
                    color: #fff;
                    font-size: 16pt;
                    font-weight: bold;
                    border-radius: 15px;
                    padding: 14px 30px;
                    border: 3px solid #ffa726;      /* accent border */
                }
                QPushButton#generatePayrollButton:hover {
                    background-color: #ffa726;
                }
                QPushButton#generatePayrollButton:pressed {
                    background-color: #fb8c00;
                }
            """)

            pay_layout.addStretch(1)
            pay_layout.addWidget(self.add_btn, alignment=Qt.AlignmentFlag.AlignCenter)
            pay_layout.addStretch(3)
        else:
            self.employee_payroll_table = QTableWidget()
            self.employee_payroll_table.setColumnCount(8)
            self.employee_payroll_table.setHorizontalHeaderLabels([
                "Date", "Employee", "Position", "Base", "Overtime", "Allowance", "Deductions", "Net Pay"
            ])
            self.employee_payroll_table.verticalHeader().setDefaultSectionSize(40)
            self.employee_payroll_table.horizontalHeader().setDefaultSectionSize(140)
            self.employee_payroll_table.setAlternatingRowColors(True)
            self.employee_payroll_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            self.employee_payroll_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
            self.employee_payroll_table.setStyleSheet("""
                QTableWidget {
                    font-size: 11pt;
                    selection-background-color: #cce5ff;
                    selection-color: #000;
                    gridline-color: #ddd;
                }
                QHeaderView::section {
                    background-color: #f0f0f0;
                    font-weight: bold;
                }
            """)
            pay_layout.addWidget(self.employee_payroll_table)
            self.employee_payroll_table.cellDoubleClicked.connect(self.show_payslip_dialog)

        pay_page = QWidget()
        pay_page.setLayout(pay_layout)
        self.stack.addWidget(pay_page)

        # --- New Record Page for Admin ---
        self.record_table = QTableWidget()
        self.record_table.setColumnCount(8)
        self.record_table.setHorizontalHeaderLabels([
            "Date", "Employee", "Position", "Base", "Overtime", "Allowance", "Deductions", "Net Pay"
        ])
        self.record_table.setMinimumHeight(460)
        self.record_table.verticalHeader().setDefaultSectionSize(40)
        self.record_table.horizontalHeader().setDefaultSectionSize(140)
        self.record_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.record_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.record_table.setAlternatingRowColors(True)
        self.record_table.setStyleSheet("""
            QTableWidget {
                font-size: 11pt;
                selection-background-color: #cce5ff;
                selection-color: #000;
                gridline-color: #ddd;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                font-weight: bold;
            }
        """)

        record_layout = QVBoxLayout()
        record_layout.setContentsMargins(20, 20, 20, 20)
        record_layout.addWidget(self.record_table)

        record_page = QWidget()
        record_page.setLayout(record_layout)
        self.stack.addWidget(record_page)

        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(3)
        self.attendance_table.setHorizontalHeaderLabels(["Employee", "Time In", "Time Out"])
        self.attendance_table.setMinimumHeight(460)
        self.attendance_table.verticalHeader().setDefaultSectionSize(40)
        self.attendance_table.horizontalHeader().setDefaultSectionSize(300)
        self.attendance_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.attendance_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.attendance_table.setAlternatingRowColors(True)
        self.attendance_table.setStyleSheet("""
            QTableWidget {
                font-size: 11pt;
                selection-background-color: #cce5ff;
                selection-color: #000;
                gridline-color: #ddd;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                font-weight: bold;
            }
        """)

        header = self.attendance_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, header.ResizeMode.Interactive)
        header.setSectionResizeMode(1, header.ResizeMode.Interactive)
        header.setSectionResizeMode(2, header.ResizeMode.Interactive)

        header.resizeSection(0, 250)
        header.resizeSection(1, 300)
        header.resizeSection(2, 300)

        att_layout = QVBoxLayout()
        att_layout.setContentsMargins(20, 20, 20, 20)
        att_layout.addWidget(self.attendance_table)
        self.timein_btn = QPushButton("🕒 Time In")
        self.timeout_btn = QPushButton("🏁 Time Out")
        self.timein_btn.setObjectName("largeButton")
        self.timeout_btn.setObjectName("largeButton")
        self.timein_btn.setFixedHeight(60)
        self.timeout_btn.setFixedHeight(60)
        self.timein_btn.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.timeout_btn.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.timein_btn.clicked.connect(self.time_in)
        self.timeout_btn.clicked.connect(self.time_out)

        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.setSpacing(25)
        btn_layout.addWidget(self.timein_btn)
        btn_layout.addWidget(self.timeout_btn)

        att_layout.addLayout(btn_layout)

        if self.role == "admin":
            self.timein_btn.hide()
            self.timeout_btn.hide()

        att_page = QWidget()
        att_page.setLayout(att_layout)
        self.stack.addWidget(att_page)

        self.pending_table = QTableWidget()
        self.pending_table.setColumnCount(5)
        self.pending_table.setHorizontalHeaderLabels(["Username", "Name", "Position", "Department", "Salary"])
        self.pending_table.setMinimumHeight(460)
        self.pending_table.verticalHeader().setDefaultSectionSize(40)
        self.pending_table.horizontalHeader().setDefaultSectionSize(200)


        self.pending_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.pending_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.pending_table.setAlternatingRowColors(True)
        self.pending_table.setStyleSheet("""
            QTableWidget {
                font-size: 11pt;
                selection-background-color: #cce5ff;
                selection-color: #000;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                font-weight: bold;
            }
        """)

        self.approve_btn = QPushButton("✅ Approve Employee")
        self.reject_btn = QPushButton("❌ Reject Employee")
        self.approve_btn.setObjectName("approveButton")
        self.reject_btn.setObjectName("rejectButton")
        self.approve_btn.setFixedHeight(60)
        self.reject_btn.setFixedHeight(60)
        self.approve_btn.clicked.connect(self.approve_selected)
        self.reject_btn.clicked.connect(self.reject_selected)

        pend_layout = QVBoxLayout()
        pend_layout.setContentsMargins(20, 20, 20, 20)
        pend_layout.addWidget(self.pending_table)
        pend_layout.addWidget(self.approve_btn)
        pend_layout.addWidget(self.reject_btn)

        pend_page = QWidget()
        pend_page.setLayout(pend_layout)
        self.stack.addWidget(pend_page)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)

        self.btn_dashboard.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_payroll.clicked.connect(self.show_payroll_page)
        self.btn_record.clicked.connect(lambda: (self.stack.setCurrentIndex(2), self.load_payroll_table()))
        self.btn_attendance.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        self.btn_pending.clicked.connect(lambda: self.stack.setCurrentIndex(4))
        self.btn_logout.clicked.connect(self.logout)

        for t in [self.payroll_table, self.attendance_table, self.pending_table]:
            t.setAlternatingRowColors(True)
            t.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
            t.verticalHeader().setVisible(False)
            t.horizontalHeader().setStretchLastSection(True)

    def update_time(self):
        self.time_label.setText("🕒 " + QTime.currentTime().toString("hh:mm:ss AP"))

    def apply_role_restrictions(self):
        if self.role == "employee":
            self.btn_pending.hide()
            self.approve_btn.hide()
        if self.role != "admin":
            self.btn_record.hide()
        if self.role == "admin":
            try:
                self.timein_btn.setEnabled(False)
                self.timeout_btn.setEnabled(False)
            except Exception:
                pass

        for tbl in [getattr(self, "payroll_table", None),
                    getattr(self, "employee_payroll_table", None),
                    getattr(self, "record_table", None)]:
            if tbl:
                try:
                    tbl.cellDoubleClicked.disconnect()
                except TypeError:
                    pass

        if self.role == "admin":
            self.payroll_table.cellDoubleClicked.connect(self.show_payslip_dialog)
            self.record_table.cellDoubleClicked.connect(self.show_payslip_dialog)
        else:
            self.employee_payroll_table.cellDoubleClicked.connect(self.show_payslip_dialog)

    def load_tables(self):
        self.load_attendance_table()

        if self.role == "admin":
            self.load_pending_table()
            self.load_record_table()
            self.update_employee_count()
            self.update_payroll_count()
            self.update_pending_count()
        else:
            self.load_employee_payroll_table()

        self.update_netpay_total()

    def update_payroll_count(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) AS total FROM payroll")
            total = cur.fetchone()["total"]
            conn.close()
            self.payroll_count_label.setText(str(total))
        except Exception as e:
            print("❌ Error fetching payroll count:", e)
            self.payroll_count_label.setText("0")

    def update_pending_count(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) AS total FROM pending_employees WHERE status='pending'")
            total = cur.fetchone()["total"]
            conn.close()
            self.pending_count_label.setText(str(total))
        except Exception as e:
            print("❌ Error fetching pending count:", e)
            self.pending_count_label.setText("0")

    def update_netpay_total(self):
        try:
            conn = get_connection()
            cur = conn.cursor()

            if self.role == "admin":
                cur.execute("SELECT SUM(netpay) AS total FROM payroll")
                total = cur.fetchone()["total"]
            else:
                username_norm = str(self.username).strip()
                cur.execute("SELECT name FROM employees WHERE LOWER(username)=LOWER(%s)", (username_norm,))
                emp = cur.fetchone()
                emp_name = emp["name"] if emp else None

                if emp_name:
                    cur.execute("""
                        SELECT SUM(netpay) AS total FROM payroll
                        WHERE LOWER(TRIM(employee_name)) = LOWER(TRIM(%s))
                           OR LOWER(TRIM(employee_name)) LIKE CONCAT('%%', LOWER(TRIM(%s)), '%%')
                    """, (emp_name, username_norm))
                else:
                    cur.execute("""
                        SELECT SUM(netpay) AS total FROM payroll
                        WHERE LOWER(TRIM(employee_name)) LIKE CONCAT('%%', LOWER(TRIM(%s)), '%%')
                    """, (username_norm,))

                row = cur.fetchone()
                total = row["total"] if row else 0

            conn.close()
            total = total or 0
            self.netpay_total_label.setText(f"₱{float(total):,.2f}")
        except Exception as e:
            print("❌ Error fetching net payroll total:", e)
            self.netpay_total_label.setText("₱0.00")

    def load_payroll_table(self):
        try:
            conn = get_connection()
            cur = conn.cursor()

            if self.role == "employee":
                username_norm = str(self.username).strip()
                cur.execute("SELECT name FROM employees WHERE LOWER(username)=LOWER(%s)", (username_norm,))
                emp = cur.fetchone()
                emp_name = emp["name"] if emp else None

                if emp_name:
                    cur.execute("""
                        SELECT * FROM payroll
                        WHERE LOWER(TRIM(employee_name)) = LOWER(TRIM(%s))
                           OR LOWER(TRIM(employee_name)) = LOWER(TRIM(%s))
                           OR LOWER(TRIM(employee_name)) LIKE CONCAT('%%', LOWER(TRIM(%s)), '%%')
                    """, (emp_name, username_norm, emp_name))
                else:
                    cur.execute("""
                        SELECT * FROM payroll
                        WHERE LOWER(TRIM(employee_name)) LIKE CONCAT('%%', LOWER(TRIM(%s)), '%%')
                    """, (username_norm,))
            else:
                cur.execute("SELECT * FROM payroll")

            rows = cur.fetchall()
            self.payroll_table.setRowCount(0)

            def val(o, key, idx):
                if isinstance(o, dict):
                    return o.get(key, "")
                try:
                    return o[idx]
                except Exception:
                    return ""

            def fmt_num(n):
                try:
                    return f"{int(float(n)):,}"
                except Exception:
                    return str(n or "")

            for r in rows:
                row = self.payroll_table.rowCount()
                self.payroll_table.insertRow(row)

                date_val = str(val(r, "date_issued", 7))
                emp_name = str(val(r, "employee_name", 0))
                position = str(val(r, "position", 1))
                base = fmt_num(val(r, "base", 2))
                overtime = fmt_num(val(r, "overtime", 3))
                allowance = fmt_num(val(r, "allowance", 4))
                deductions = fmt_num(val(r, "deductions", 5))
                netpay = fmt_num(val(r, "netpay", 6))

                values = [date_val, emp_name, position, base, overtime, allowance, deductions, netpay]

                for col, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    if col >= 3:
                        item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    self.payroll_table.setItem(row, col, item)

            conn.close()
        except Exception as e:
            print("❌ Payroll load error:", e)

    def load_record_table(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM payroll ORDER BY date_issued DESC")
            rows = cur.fetchall()
            self.record_table.setRowCount(0)

            def fmt_num(n):
                try:
                    return f"{int(float(n)):,}"
                except Exception:
                    return str(n or "")

            for r in rows:
                row = self.record_table.rowCount()
                self.record_table.insertRow(row)

                date_val = str(r.get("date_issued", ""))
                emp_name = str(r.get("employee_name", ""))
                position = str(r.get("position", ""))
                base = fmt_num(r.get("base", ""))
                overtime = fmt_num(r.get("overtime", ""))
                allowance = fmt_num(r.get("allowance", ""))
                deductions = fmt_num(r.get("deductions", ""))
                netpay = fmt_num(r.get("netpay", ""))

                values = [date_val, emp_name, position, base, overtime, allowance, deductions, netpay]
                for col, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    if col >= 3:
                        item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    self.record_table.setItem(row, col, item)

            conn.close()
        except Exception as e:
            print("❌ Record table load error:", e)

    def load_employee_payroll_table(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT name FROM employees WHERE LOWER(username)=LOWER(%s)", (self.username,))
            emp = cur.fetchone()
            emp_name = emp["name"] if emp else self.username

            cur.execute("""
                SELECT * FROM payroll
                WHERE LOWER(TRIM(employee_name)) = LOWER(TRIM(%s))
                   OR LOWER(TRIM(employee_name)) LIKE CONCAT('%%', LOWER(TRIM(%s)), '%%')
                ORDER BY date_issued DESC
            """, (emp_name, emp_name))
            rows = cur.fetchall()
            self.employee_payroll_table.setRowCount(0)

            def fmt_num(n):
                try:
                    return f"{float(n):,.2f}"
                except Exception:
                    return str(n or "")

            for r in rows:
                row = self.employee_payroll_table.rowCount()
                self.employee_payroll_table.insertRow(row)
                values = [
                    str(r.get("date_issued", "")),
                    str(r.get("employee_name", "")),
                    str(r.get("position", "")),
                    fmt_num(r.get("base", "")),
                    fmt_num(r.get("overtime", "")),
                    fmt_num(r.get("allowance", "")),
                    fmt_num(r.get("deductions", "")),
                    fmt_num(r.get("netpay", ""))
                ]
                for col, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    if col >= 3:
                        item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    self.employee_payroll_table.setItem(row, col, item)

            conn.close()
        except Exception as e:
            print("❌ Employee payroll table load error:", e)

    def load_attendance_table(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            if self.role == "employee":
                cur.execute("SELECT * FROM attendance WHERE employee_name=%s", (self.username,))
            else:
                cur.execute("SELECT * FROM attendance")
            rows = cur.fetchall()
            self.attendance_table.setRowCount(0)
            for r in rows:
                row = self.attendance_table.rowCount()
                self.attendance_table.insertRow(row)
                self.attendance_table.setItem(row, 0, QTableWidgetItem(r["employee_name"]))
                self.attendance_table.setItem(row, 1, QTableWidgetItem(str(r["time_in"])))
                self.attendance_table.setItem(row, 2, QTableWidgetItem(str(r["time_out"])))
            conn.close()
        except Exception as e:
            print("Attendance load error:", e)

    def load_pending_table(self):
        rows = fetch_pending_employees()
        self.pending_table.setRowCount(0)
        for r in rows:
            row = self.pending_table.rowCount()
            self.pending_table.insertRow(row)
            self.pending_table.setItem(row, 0, QTableWidgetItem(r["username"]))
            self.pending_table.setItem(row, 1, QTableWidgetItem(r["name"]))
            self.pending_table.setItem(row, 2, QTableWidgetItem(r["position"]))
            self.pending_table.setItem(row, 3, QTableWidgetItem(r["department"]))
            try:
                salary = f"{int(float(r['salary'])):,}"
            except Exception:
                salary = str(r.get("salary", ""))
            item = QTableWidgetItem(salary)
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.pending_table.setItem(row, 4, item)

    def add_payroll_record(self):
        dialog = PayrollDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO payroll (employee_name, position, base, overtime, allowance, deductions, netpay, date_issued)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """, data)
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Added", "Payroll record added successfully.")
                self.load_record_table()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Database error:\n{e}")

    def time_in(self):
        if self.role != "employee":
            QMessageBox.warning(self, "Access Denied", "Only employee accounts can record attendance.")
            return

        try:
            if not is_employee_approved(self.username):
                QMessageBox.warning(self, "Access Denied", "Your account is not yet approved by the admin.")
                return

            conn = get_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO attendance (employee_name, time_in) VALUES (%s, NOW())", (self.username,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", "Time In recorded.")
            self.load_attendance_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Attendance error:\n{e}")

    def show_payslip_dialog(self, row, column):

        if hasattr(self, "_payslip_open") and self._payslip_open:
            return
        self._payslip_open = True

        sender = self.sender()
        table = sender if sender else self.payroll_table

        try:
            date_issued = table.item(row, 0).text()
            employee = table.item(row, 1).text()
            position = table.item(row, 2).text()
            base = table.item(row, 3).text()
            overtime = table.item(row, 4).text()
            allowance = table.item(row, 5).text()
            deductions = table.item(row, 6).text()
            netpay = table.item(row, 7).text()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Unable to read payslip data:\n{e}")
            return

        # Build the payslip dialog (same UI)
        dlg = QDialog(self)
        dlg.setWindowTitle("🧾 Employee Payslip")
        dlg.setFixedSize(420, 480)
        dlg.setStyleSheet("""
               QDialog {
                   background-color: #ffffff;
                   border-radius: 12px;
               }
               QLabel {
                   font-size: 12pt;
                   font-family: 'Segoe UI';
               }
               #titleLabel {
                   font-size: 16pt;
                   font-weight: bold;
                   color: #222;
               }
               #netLabel {
                   font-size: 14pt;
                   font-weight: bold;
                   color: #007B00;
               }
           """)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(12)

        title = QLabel("💰 PayRight Employee Payslip")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        layout.addSpacing(10)
        fields = {
            "Employee Name": employee,
            "Position": position,
            "Date Issued": date_issued,
            "Base Salary": f"₱{base}",
            "Overtime": f"₱{overtime}",
            "Allowance": f"₱{allowance}",
            "Deductions": f"₱{deductions}",
            "Net Pay": f"₱{netpay}",
        }

        for label, value in fields.items():
            row_layout = QHBoxLayout()
            lbl = QLabel(f"{label}:")
            lbl.setFixedWidth(130)
            val = QLabel(str(value))
            row_layout.addWidget(lbl)
            row_layout.addWidget(val)
            layout.addLayout(row_layout)

        layout.addSpacing(20)
        net_lbl = QLabel(f"Total Net Pay: ₱{netpay}")
        net_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        net_lbl.setObjectName("netLabel")
        layout.addWidget(net_lbl)

        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.setSpacing(30)

        export_btn = QPushButton("🖨️ Export as PDF")
        export_btn.setFixedHeight(40)
        export_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(40)
        close_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        close_btn.clicked.connect(dlg.accept)

        btn_layout.addWidget(export_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        def export_payslip_to_pdf():
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from PyQt6.QtWidgets import QFileDialog
            from PyQt6.QtCore import QDate
            import os, webbrowser

            file_path, _ = QFileDialog.getSaveFileName(
                dlg,
                "Save Payslip as PDF",
                f"{employee}_Payslip.pdf",
                "PDF Files (*.pdf)"
            )
            if not file_path:
                return
            if not file_path.lower().endswith(".pdf"):
                file_path += ".pdf"

            try:
                c = canvas.Canvas(file_path, pagesize=letter)
                width, height = letter

                border_margin = 0.6 * inch
                c.setStrokeColor(colors.black)
                c.setLineWidth(1)
                c.rect(border_margin, border_margin, width - 2 * border_margin, height - 2 * border_margin)

                logo_path = r"C:\Users\User\Downloads\PayRights.png"
                y = height - 1.0 * inch
                if os.path.exists(logo_path):
                    c.drawImage(logo_path, border_margin + 10, y - 30, width=60, height=60, mask='auto')

                c.setFont("Helvetica-Bold", 18)
                c.drawCentredString(width / 2, height - 1.2 * inch, "PayRight Employee Payslip")

                c.line(border_margin + 10, height - 1.35 * inch, width - border_margin - 10, height - 1.35 * inch)
                c.setFont("Helvetica", 12)
                y = height - 1.8 * inch
                label_x = border_margin + 20
                value_x = border_margin + 180
                line_height = 0.3 * inch

                for k, v in fields.items():
                    c.drawString(label_x, y, f"{k}:")
                    c.drawString(value_x, y, str(v))
                    y -= line_height

                y -= 0.2 * inch
                c.setFont("Helvetica-Bold", 13)
                c.setFillColor(colors.green)
                c.drawString(label_x, y, f"Total Net Pay: ₱{netpay}")
                c.setFillColor(colors.black)

                y -= 0.6 * inch
                c.setFont("Helvetica-Oblique", 10)
                c.drawString(label_x, y, "This document was automatically generated by the PayRight Payroll System.")
                y -= 0.2 * inch
                c.drawString(label_x, y, "For any discrepancies, please contact the HR department.")

                footer_text = f"Generated on: {QDate.currentDate().toString('yyyy-MM-dd')}"
                c.setFont("Helvetica", 9)
                c.drawRightString(width - border_margin - 10, border_margin + 15, footer_text)

                c.save()
                QMessageBox.information(dlg, "Success", f"Payslip successfully saved to:\n{file_path}")
                if os.path.exists(file_path):
                    webbrowser.open_new(file_path)
            except Exception as e:
                QMessageBox.critical(dlg, "Error", f"Failed to export PDF:\n{e}")

        export_btn.clicked.connect(export_payslip_to_pdf)
        dlg.exec()
        self._payslip_open = False

        def export_payslip_to_pdf():
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from PyQt6.QtWidgets import QFileDialog
            from PyQt6.QtCore import QDate
            import os
            import webbrowser

            file_path, _ = QFileDialog.getSaveFileName(
                dlg,
                "Save Payslip as PDF",
                f"{employee}_Payslip.pdf",
                "PDF Files (*.pdf)"
            )
            if not file_path:
                return
            if not file_path.lower().endswith(".pdf"):
                file_path += ".pdf"

            try:
                c = canvas.Canvas(file_path, pagesize=letter)
                width, height = letter

                border_margin = 0.6 * inch
                c.setStrokeColor(colors.black)
                c.setLineWidth(1)
                c.rect(
                    border_margin,
                    border_margin,
                    width - 2 * border_margin,
                    height - 2 * border_margin
                )

                logo_path = r"C:\Users\User\Downloads\PayRights.png"  # ✅ Change path if needed
                y = height - 1.0 * inch
                if os.path.exists(logo_path):
                    c.drawImage(logo_path, border_margin + 10, y - 30, width=60, height=60, mask='auto')

                c.setFont("Helvetica-Bold", 18)
                c.drawCentredString(width / 2, height - 1.2 * inch, "PayRight Employee Payslip")

                c.setStrokeColor(colors.black)
                c.line(border_margin + 10, height - 1.35 * inch, width - border_margin - 10, height - 1.35 * inch)

                c.setFont("Helvetica", 12)
                y = height - 1.8 * inch
                label_x = border_margin + 20
                value_x = border_margin + 180
                line_height = 0.3 * inch

                for k, v in fields.items():
                    c.drawString(label_x, y, f"{k}:")
                    c.drawString(value_x, y, str(v))
                    y -= line_height

                y -= 0.2 * inch
                c.setFont("Helvetica-Bold", 13)
                c.setFillColor(colors.green)
                c.drawString(label_x, y, f"Total Net Pay: ₱{netpay}")
                c.setFillColor(colors.black)

                y -= 0.6 * inch
                c.setFont("Helvetica-Oblique", 10)
                c.drawString(label_x, y, "This document was automatically generated by the PayRight Payroll System.")
                y -= 0.2 * inch
                c.drawString(label_x, y, "For any discrepancies, please contact the HR department.")

                c.setFont("Helvetica", 9)
                footer_text = f"Generated on: {QDate.currentDate().toString('yyyy-MM-dd')}"
                c.drawRightString(width - border_margin - 10, border_margin + 15, footer_text)

                c.save()

                QMessageBox.information(dlg, "Success", f"Payslip successfully saved to:\n{file_path}")

                if os.path.exists(file_path):
                    webbrowser.open_new(file_path)

            except Exception as e:
                QMessageBox.critical(dlg, "Error", f"Failed to export PDF:\n{e}")

        export_btn.clicked.connect(export_payslip_to_pdf)

        dlg.exec()


    def time_out(self):
        if self.role != "employee":
            QMessageBox.warning(self, "Access Denied", "Only employee accounts can record attendance.")
            return

        try:
            if not is_employee_approved(self.username):
                QMessageBox.warning(self, "Access Denied", "Your account is not yet approved by the admin.")
                return

            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE attendance SET time_out = NOW()
                WHERE employee_name=%s AND time_out IS NULL
            """, (self.username,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", "Time Out recorded.")
            self.load_attendance_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Attendance error:\n{e}")

    def approve_selected(self):
        row = self.pending_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select", "Please select a record first.")
            return
        username = self.pending_table.item(row, 0).text()
        if approve_employee(username):
            QMessageBox.information(self, "Approved", f"{username} has been approved.")
            self.load_pending_table()
        else:
            QMessageBox.warning(self, "Error", "Approval failed.")

    def reject_selected(self):
        row = self.pending_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select", "Please select a record first.")
            return
        username = self.pending_table.item(row, 0).text()
        from Database import reject_employee
        if reject_employee(username):
            QMessageBox.information(self, "Rejected", f"{username} has been rejected and removed.")
            self.load_pending_table()
        else:
            QMessageBox.warning(self, "Error", "Failed to reject employee.")

    def logout(self):
        if self.role == "employee":
            if self.has_active_time_in():
                QMessageBox.warning(
                    self,
                    "Logout Blocked",
                    "⚠️ You still have an active Time In record.\n\n"
                    "Please Time Out first before logging out."
                )
                return
        confirm = QMessageBox.question(
            self,
            "Confirm Logout",
            "Are you sure you want to log out of PayRight?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            if hasattr(self, "login_window"):
                self.login_window.clear_credentials()
                self.login_window.show()
            self.hide()
            self.deleteLater()

    def show_payroll_page(self):
        self.stack.setCurrentIndex(1)

        if self.role == "employee":
            self.load_employee_payroll_table()

            if not hasattr(self, "refresh_timer"):
                from PyQt6.QtCore import QTimer
                self.refresh_timer = QTimer()
                self.refresh_timer.timeout.connect(self.load_employee_payroll_table)

            if not self.refresh_timer.isActive():
                self.refresh_timer.start(15000)
        else:
            if hasattr(self, "refresh_timer") and self.refresh_timer.isActive():
                self.refresh_timer.stop()

    def has_active_time_in(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM attendance 
                WHERE employee_name=%s AND time_out IS NULL
            """, (self.username,))
            active = cur.fetchone()
            conn.close()
            return bool(active)
        except Exception as e:
            print("❌ Error checking active time in:", e)
            return False

    def update_employee_count(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) AS total FROM employees")
            total = cur.fetchone()["total"]
            conn.close()
            self.employee_count_label.setText(str(total))
        except Exception as e:
            print("❌ Error fetching employee count:", e)
            self.employee_count_label.setText("0")

    def open_announcement_editor(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("✏️ Edit Announcements")
        dialog.setFixedSize(500, 500)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border-radius: 10px;
            }
            QTextEdit {
                font-size: 11pt;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton {
                font-size: 11pt;
                font-weight: bold;
                padding: 8px 16px;
            }
        """)

        from PyQt6.QtWidgets import QVBoxLayout, QTextEdit, QHBoxLayout

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        label = QLabel("Update Announcement Message:")
        label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(label)

        text_edit = QTextEdit()
        text_edit.setText(self.announcement_label.text())
        layout.addWidget(text_edit)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        save_btn = QPushButton("💾 Save")
        cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        def save_changes():
            new_text = text_edit.toPlainText().strip()
            if not new_text:
                QMessageBox.warning(dialog, "Empty", "Announcement cannot be empty.")
                return
            self.announcement_label.setText(new_text)
            QMessageBox.information(dialog, "Saved", "Announcement updated successfully.")
            dialog.accept()

        save_btn.clicked.connect(save_changes)
        cancel_btn.clicked.connect(dialog.reject)

        dialog.exec()



class PayrollDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("Generate Payroll Record")
        self.setObjectName("payrollDialog")

        screen = QApplication.primaryScreen().geometry()
        self.resize(int(screen.width() * 0.35), int(screen.height() * 0.58))

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("payrollDialogHeader")
        header.setFixedHeight(60)

        title_label = QLabel(" 💰Generate Payroll Record", header)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setObjectName("payrollDialogTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header_layout = QVBoxLayout(header)
        header_layout.addWidget(title_label)
        main_layout.addWidget(header)

        body_frame = QFrame()
        body_layout = QFormLayout(body_frame)
        body_layout.setVerticalSpacing(18)
        body_layout.setHorizontalSpacing(25)
        body_layout.setContentsMargins(40, 30, 40, 30)

        label_font = QFont("Segoe UI", 12, QFont.Weight.Bold)
        input_font = QFont("Segoe UI", 12)

        self.emp = QComboBox()
        self.emp.setFont(input_font)
        self.emp.setMinimumHeight(40)
        self.load_employees()

        self.pos = QLineEdit()
        self.pos.setReadOnly(True)
        self.pos.setFont(input_font)
        self.pos.setMinimumHeight(40)

        self.base = QLineEdit()
        self.base.setReadOnly(True)
        self.base.setFont(input_font)
        self.base.setMinimumHeight(40)

        validator = QDoubleValidator(0.0, 9999999.0, 2)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)

        self.over_hours = QLineEdit()
        self.over_hours.setValidator(validator)
        self.over_hours.setFont(input_font)
        self.over_hours.setMinimumHeight(40)
        self.over_hours.setPlaceholderText("Enter overtime hours")

        self.allow = QLineEdit()
        self.allow.setValidator(validator)
        self.allow.setFont(input_font)
        self.allow.setMinimumHeight(40)
        self.allow.setPlaceholderText("Enter allowance")

        self.ded = QLineEdit()
        self.ded.setValidator(validator)
        self.ded.setFont(input_font)
        self.ded.setMinimumHeight(40)
        self.ded.setPlaceholderText("Enter deductions")

        self.overtime_label = QLabel("₱0.00")
        self.allow_label = QLabel("₱0.00")
        self.ded_label = QLabel("₱0.00")

        self.overtime_label.setStyleSheet("color: #555; font-weight: 600;")
        self.allow_label.setStyleSheet("color: #666; font-weight: 600;")
        self.ded_label.setStyleSheet("color: #777; font-weight: 600;")

        self.overtime_row = QHBoxLayout()
        self.overtime_row.addWidget(self.over_hours)
        self.overtime_row.addWidget(self.overtime_label)

        self.allow_row = QHBoxLayout()
        self.allow_row.addWidget(self.allow)
        self.allow_row.addWidget(self.allow_label)

        self.ded_row = QHBoxLayout()
        self.ded_row.addWidget(self.ded)
        self.ded_row.addWidget(self.ded_label)

        self.net_label = QLabel("₱0.00")
        self.net_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.net_label.setObjectName("netLabel")

        self.date = QDateEdit(calendarPopup=True)
        self.date.setFont(input_font)
        self.date.setMinimumHeight(40)
        self.date.setDate(QDate.currentDate())
        self.date.setDisplayFormat("yyyy-MM-dd")

        for text, widget in [
            ("Employee:", self.emp),
            ("Position:", self.pos),
            ("Base Salary:", self.base),
            ("Overtime Hours:", self.overtime_row),
            ("Allowance:", self.allow_row),
            ("Deductions:", self.ded_row),
            ("Net Pay :", self.net_label),
            ("Date Issued:", self.date)
        ]:
            lbl = QLabel(text)
            lbl.setFont(label_font)
            body_layout.addRow(lbl, widget)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_layout.setSpacing(30)

        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setObjectName("submitButton")
        self.submit_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.submit_btn.setMinimumHeight(45)
        self.submit_btn.setMinimumWidth(140)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancelButton")
        self.cancel_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.cancel_btn.setMinimumHeight(45)
        self.cancel_btn.setMinimumWidth(140)

        button_layout.addWidget(self.submit_btn)
        button_layout.addWidget(self.cancel_btn)
        body_layout.addRow(button_layout)
        main_layout.addWidget(body_frame)

        self.submit_btn.clicked.connect(self.validate_and_confirm)
        self.cancel_btn.clicked.connect(self.reject)

        for field in (self.over_hours, self.allow, self.ded):
            field.textEdited.connect(self.update_net_pay)

        self.emp.currentIndexChanged.connect(self.update_position)

        if getattr(self, "employee_data", None):
            if len(self.employee_data) > 0:
                self.emp.setCurrentIndex(0)
                self.update_position()

        self.center_dialog()

    def center_dialog(self):
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

    def load_employees(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT name, position, salary FROM employees")
            data = cur.fetchall() or []
            conn.close()

            self.employee_data = []
            self.emp.clear()

            for row in data:
                name, pos, sal = row.get("name"), row.get("position"), row.get("salary")
                if not name:
                    continue
                self.employee_data.append({"name": name, "position": pos, "salary": float(sal or 0)})
                self.emp.addItem(name)
        except Exception as e:
            print("❌ Error loading employees:", e)
            self.employee_data = []

    def update_position(self):
        try:
            idx = self.emp.currentIndex()
            if idx < 0 or idx >= len(self.employee_data):
                self.pos.clear()
                self.base.clear()
                return
            emp = self.employee_data[idx]
            self.pos.setText(str(emp["position"]))
            self.base.setText(f"{emp['salary']:,.2f}")
            self.update_net_pay()
        except Exception as e:
            print("⚠️ Error updating position/salary:", e)

    def update_net_pay(self):
        def clean(v):
            try:
                return float(str(v).replace(",", "").replace("₱", "").strip() or 0)
            except:
                return 0.0

        b = clean(self.base.text())
        a = clean(self.allow.text())
        d = clean(self.ded.text())

        try:
            over_hours = float(self.over_hours.text().strip() or 0)
        except:
            over_hours = 0

        hourly_rate = b / 160 if b > 0 else 0
        overtime_pay = hourly_rate * over_hours * 1.25
        net = b + overtime_pay + a - d

        self.overtime_label.setText(f"₱{overtime_pay:,.2f}")
        self.allow_label.setText(f"₱{a:,.2f}")
        self.ded_label.setText(f"₱{d:,.2f}")
        self.net_label.setText(f"₱{net:,.2f}")

        if net < 0:
            self.net_label.setStyleSheet("color: #E53935; font-weight: bold;")
        else:
            self.net_label.setStyleSheet("color: #4CAF50; font-weight: bold;")

    def validate_and_confirm(self):
        if not self.over_hours.text().strip() or not self.allow.text().strip() or not self.ded.text().strip():
            QMessageBox.warning(self, "Incomplete", "Please complete all fields before submitting.")
            return

        emp_name = self.emp.currentText()
        confirm = QMessageBox.question(
            self,
            "Confirm Submission",
            f"Submit payroll for {emp_name}?\nNet Pay: {self.net_label.text()}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.accept()

    def get_data(self):
        def clean_num(v):
            try:
                return float(str(v).replace(",", "").replace("₱", "").strip() or 0)
            except:
                return 0.0

        b = clean_num(self.base.text())
        a = clean_num(self.allow.text())
        d = clean_num(self.ded.text())
        try:
            over_hours = float(self.over_hours.text().strip() or 0)
        except:
            over_hours = 0

        hourly_rate = b / 160 if b > 0 else 0
        o = hourly_rate * over_hours * 1.25
        net = b + o + a - d

        return (
            self.emp.currentText(),
            self.pos.text(),
            b, o, a, d, net,
            self.date.date().toString("yyyy-MM-dd")
        )


