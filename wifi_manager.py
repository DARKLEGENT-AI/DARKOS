#!/usr/bin/env python3
import sys
import subprocess

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QHBoxLayout, QMessageBox, QTableWidget,
    QTableWidgetItem, QLineEdit, QStackedLayout,
    QDialog
)
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QPushButton

# ----------------------- Стиль кнопок -----------------------
BUTTON_STYLE = """
QPushButton {
    background-color: #A54242;
    color: #FFFFFF;
    border: none;
    padding: 10px;
    font-size: 14px;
}
QPushButton:hover { background-color: #C05050; }
QPushButton:pressed { background-color: #8B2B2B; }
QPushButton:disabled { background-color: #A54242; color: #CCCCCC; }
"""

# ----------------------- Восьмиугольная кнопка -----------------------
class OctagonButton(QPushButton):
    def resizeEvent(self, event):
        super().resizeEvent(event)
        w, h = self.width(), self.height()
        cut = min(w, h) * 0.2
        from PyQt6.QtGui import QPainterPath, QRegion
        path = QPainterPath()
        path.moveTo(cut, 0)
        path.lineTo(w - cut, 0)
        path.lineTo(w, cut)
        path.lineTo(w, h - cut)
        path.lineTo(w - cut, h)
        path.lineTo(cut, h)
        path.lineTo(0, h - cut)
        path.lineTo(0, cut)
        path.closeSubpath()
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

# ----------------------- Диалог ввода пароля -----------------------
class PasswordDialog(QDialog):
    def __init__(self, ssid, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Подключение к {ssid}")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setFixedSize(350, 150)
        self.ssid = ssid
        self.password = None
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("background-color: #1F1F1F; color: #FFFFFF;")
        layout = QVBoxLayout()
        label = QLabel(f"Введите пароль для сети «{self.ssid}»:")
        label.setStyleSheet("font-size: 14px;")
        layout.addWidget(label)

        self.line_edit = QLineEdit()
        self.line_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.line_edit.setStyleSheet("""
            background-color: #2A2A2A;
            color: #FFFFFF;
            border-radius: 5px;
            padding: 6px;
        """)
        layout.addWidget(self.line_edit)

        btn_layout = QHBoxLayout()
        self.ok_btn = OctagonButton("Подключиться")
        self.ok_btn.setStyleSheet(BUTTON_STYLE)
        self.ok_btn.clicked.connect(self.on_ok)
        self.cancel_btn = OctagonButton("Отмена")
        self.cancel_btn.setStyleSheet(BUTTON_STYLE)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def on_ok(self):
        self.password = self.line_edit.text()
        self.accept()

# ----------------------- Главное окно -----------------------
class WifiManagerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_ssid = None
        self.init_ui()
        QTimer.singleShot(100, self.scan_wifi)

    def init_ui(self):
        self.setWindowTitle("Wi‑Fi Manager")
        self.resize(600, 450)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#1F1F1F"))
        self.setPalette(palette)

        self.stack = QStackedLayout()
        self.setLayout(self.stack)

        # ---------- Экран загрузки ----------
        self.loading_widget = QWidget()
        load_layout = QVBoxLayout()
        self.loading_label = QLabel("⏳ Сканирование Wi‑Fi сетей…")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("color:#FFFFFF; font-size:16px;")
        load_layout.addStretch()
        load_layout.addWidget(self.loading_label)
        load_layout.addStretch()
        self.loading_widget.setLayout(load_layout)
        self.stack.addWidget(self.loading_widget)

        # ---------- Основной экран ----------
        self.main_widget = QWidget()
        main_layout = QVBoxLayout()

        title = QLabel("Wi‑Fi сети")
        title.setStyleSheet("color:#FFFFFF; font-size:16px;")
        main_layout.addWidget(title)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["SSID", "Сигнал", "Безопасность", "Статус"]
        )
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setStyleSheet("""
            QTableWidget { background-color: #2A2A2A; color: #FFFFFF;
                           gridline-color: #3A3A3A; border-radius: 5px; }
            QHeaderView::section { background-color: #1F1F1F; color: #FFFFFF;
                                   padding: 6px; border: none; }
            QTableWidget::item:selected { background-color: #555555; }
        """)
        self.table.itemSelectionChanged.connect(self.on_select_network)
        main_layout.addWidget(self.table)

        btns = QHBoxLayout()
        refresh = OctagonButton("Обновить")
        refresh.setStyleSheet(BUTTON_STYLE)
        refresh.clicked.connect(self.reload)

        self.connect_btn = OctagonButton("Подключиться")
        self.connect_btn.setStyleSheet(BUTTON_STYLE)
        self.connect_btn.clicked.connect(self.connect_wifi)
        self.connect_btn.setEnabled(False)

        disconnect = OctagonButton("Отключиться")
        disconnect.setStyleSheet(BUTTON_STYLE)
        disconnect.clicked.connect(self.disconnect_wifi)

        btns.addWidget(refresh)
        btns.addWidget(self.connect_btn)
        btns.addWidget(disconnect)

        main_layout.addLayout(btns)
        self.main_widget.setLayout(main_layout)
        self.stack.addWidget(self.main_widget)
        self.stack.setCurrentWidget(self.loading_widget)

    # ---------- Логика ----------
    def reload(self):
        self.stack.setCurrentWidget(self.loading_widget)
        QTimer.singleShot(100, self.scan_wifi)

    def scan_wifi(self):
        self.table.setRowCount(0)
        self.connect_btn.setEnabled(False)

        try:
            output = subprocess.check_output(
                ["nmcli", "-t", "-f", "IN-USE,SSID,SIGNAL,SECURITY", "dev", "wifi", "list"],
                text=True
            )
        except Exception:
            QMessageBox.critical(self, "Ошибка", "NetworkManager недоступен")
            return

        for line in output.splitlines():
            in_use, ssid, signal, security = (line.split(":") + [""])[:4]
            ssid = ssid or "<скрытая сеть>"
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(ssid))

            sig = int(signal or 0)
            sig_item = QTableWidgetItem(f"{sig}%")
            sig_item.setForeground(
                QColor("#6FCF97") if sig >= 70 else
                QColor("#F2C94C") if sig >= 40 else
                QColor("#EB5757")
            )
            self.table.setItem(row, 1, sig_item)
            self.table.setItem(row, 2, QTableWidgetItem(security or "OPEN"))
            self.table.setItem(row, 3, QTableWidgetItem("Подключено" if in_use == "*" else ""))
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, ssid)

        self.table.resizeColumnsToContents()
        self.stack.setCurrentWidget(self.main_widget)

    def on_select_network(self):
        items = self.table.selectedItems()
        if items:
            ssid = items[0].data(Qt.ItemDataRole.UserRole)
            self.selected_ssid = ssid
            self.connect_btn.setEnabled(ssid != "<скрытая сеть>")

    def connect_wifi(self):
        if not self.selected_ssid:
            return
        dlg = PasswordDialog(self.selected_ssid, self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.password:
            pwd = dlg.password
            try:
                subprocess.check_call([
                    "nmcli", "dev", "wifi", "connect",
                    self.selected_ssid, "password", pwd
                ])
                QMessageBox.information(self, "Wi‑Fi", "Подключение выполнено")
                self.reload()
            except subprocess.CalledProcessError:
                QMessageBox.critical(self, "Ошибка", "Не удалось подключиться")

    def disconnect_wifi(self):
        try:
            out = subprocess.check_output(
                ["nmcli", "-t", "-f", "DEVICE,TYPE", "dev"], text=True
            )
            for line in out.splitlines():
                dev, typ = line.split(":")
                if typ == "wifi":
                    subprocess.call(["nmcli", "dev", "disconnect", dev])
                    self.reload()
                    return
        except Exception:
            pass

# ---------- Запуск ----------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = WifiManagerApp()
    win.show()
    sys.exit(app.exec())
