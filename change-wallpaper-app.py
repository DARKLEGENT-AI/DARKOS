import sys
import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QFileDialog, QHBoxLayout, QMessageBox
)
from PyQt6.QtWidgets import QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt, QSize, QRectF
from PyQt6.QtGui import QColor, QPalette, QIcon, QPixmap, QPainterPath, QRegion
from PyQt6.QtWidgets import QPushButton

# Однородный стиль кнопок
BUTTON_STYLE = """
QPushButton {
    background-color: #A54242;
    color: #FFFFFF;
    border: none;
    padding: 10px;
    font-size: 14px;
}
QPushButton:hover {
    background-color: #C05050;
}
QPushButton:pressed {
    background-color: #8B2B2B;
}
QPushButton:disabled {
    background-color: #A54242;
    color: #CCCCCC;
}
"""

# ----------------------- Восьмиугольная кнопка -----------------------
class OctagonButton(QPushButton):
    def resizeEvent(self, event):
        """При изменении размера кнопки пересоздаем восьмиугольник"""
        super().resizeEvent(event)
        w = self.width()
        h = self.height()
        cut = min(w, h) * 0.2  # величина среза углов

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

        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

# ----------------------- Главное окно -----------------------
class WallpaperApp(QWidget):
    def __init__(self):
        super().__init__()
        self.wallpaper_folder = None
        self.wallpaper_files = []
        self.selected_wallpaper = None
        self.initUI()
        self.check_feh_package()

    def initUI(self):
        self.setWindowTitle("Минималистичный выбор обоев")
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#1F1F1F"))
        self.setPalette(palette)

        layout = QVBoxLayout()
        self.label = QLabel("Выберите папку или файл с обоями:")
        self.label.setStyleSheet("color: #FFFFFF; font-size: 16px;")
        layout.addWidget(self.label)

        # ---------------- Кнопки выбора ----------------
        btn_layout = QHBoxLayout()
        self.folder_btn = OctagonButton("Выбрать папку")
        self.folder_btn.setStyleSheet(BUTTON_STYLE)
        self.folder_btn.clicked.connect(self.select_folder)
        btn_layout.addWidget(self.folder_btn)

        self.file_btn = OctagonButton("Выбрать файл")
        self.file_btn.setStyleSheet(BUTTON_STYLE)
        self.file_btn.clicked.connect(self.select_file)
        btn_layout.addWidget(self.file_btn)
        layout.addLayout(btn_layout)

        # ---------------- Список изображений ----------------
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(100, 100))

        # Цвет выделения
        palette = self.list_widget.palette()
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#555555"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
        self.list_widget.setPalette(palette)

        # Общий стиль списка
        self.list_widget.setStyleSheet("""
            background-color: #2A2A2A;
            color: #FFFFFF;
            border-radius: 5px;
            padding: 5px;
        """)

        self.list_widget.itemClicked.connect(self.on_select_wallpaper)
        layout.addWidget(self.list_widget)

        # ---------------- Кнопка применения ----------------
        self.apply_btn = OctagonButton("Установить обои")
        self.apply_btn.setStyleSheet(BUTTON_STYLE)
        self.apply_btn.clicked.connect(self.set_wallpaper)
        self.apply_btn.setEnabled(False)
        layout.addWidget(self.apply_btn)

        self.setLayout(layout)
        self.resize(500, 600)

    # ----------------------- Проверка feh -----------------------
    def check_feh_package(self):
        try:
            subprocess.run(["feh", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            deb_path = os.path.join(os.path.dirname(sys.argv[0]), "feh_3.9.1-2_amd64.deb")
            if os.path.exists(deb_path):
                reply = QMessageBox.question(
                    self,
                    "Feh не найден",
                    "Приложение feh не установлено. Установить локальный пакет feh_3.9.1-2_amd64.deb?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.install_feh_deb(deb_path)
            else:
                QMessageBox.warning(
                    self,
                    "Feh не найден",
                    "Feh не установлен и локальный пакет feh_3.9.1-2_amd64.deb не найден!"
                )

    def install_feh_deb(self, deb_path):
        try:
            subprocess.run(["sudo", "dpkg", "-i", deb_path], check=True)
            subprocess.run(["sudo", "apt-get", "-f", "install", "-y"], check=True)
            QMessageBox.information(self, "Успех", "Feh успешно установлен!")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось установить feh: {e}")

    # ----------------------- Выбор изображений -----------------------
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку с обоями")
        if folder:
            self.wallpaper_folder = folder
            self.wallpaper_files = [
                f for f in os.listdir(folder)
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))
            ]
            self.populate_previews()
            self.apply_btn.setEnabled(False)

    def select_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file:
            self.wallpaper_folder = os.path.dirname(file)
            self.wallpaper_files = [os.path.basename(file)]
            self.populate_previews()
            self.apply_btn.setEnabled(False)

    def populate_previews(self):
        self.list_widget.clear()
        for img_file in self.wallpaper_files:
            item = QListWidgetItem()
            img_path = os.path.join(self.wallpaper_folder, img_file)
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                icon = QIcon(pixmap.scaled(
                    100, 100,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
                item.setIcon(icon)
            item.setText(img_file)
            item.setToolTip(img_file)
            self.list_widget.addItem(item)

    # ----------------------- Работа с выбранной картинкой -----------------------
    def on_select_wallpaper(self, item):
        self.selected_wallpaper = item.text()
        self.apply_btn.setEnabled(True)

    def set_wallpaper(self):
        if not self.selected_wallpaper or not self.wallpaper_folder:
            return
        path = os.path.join(self.wallpaper_folder, self.selected_wallpaper)
        try:
            subprocess.run(["feh", "--bg-scale", path])
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось установить обои: {e}")

# ----------------------- Запуск приложения -----------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WallpaperApp()
    window.show()
    sys.exit(app.exec())
