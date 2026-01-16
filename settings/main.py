import os
import sys
import subprocess

# ================== ГЛОБАЛЬНЫЙ МАСШТАБ ==================
APP_SCALE = 1.0  # 1.0 = 100%, 1.25 = 125%, 1.5 = 150%

os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_SCALE_FACTOR"] = str(APP_SCALE)
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
# =======================================================

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QStackedWidget
)
from PyQt6.QtGui import QColor, QPalette

from widgets import OctagonButton
from ui_styles import BUTTON_STYLE
from sound_settings import SoundSettings


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Системные настройки")
        self.resize(400, 300)

        # Цвет фона
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#1F1F1F"))
        self.setPalette(palette)

        self.stack = QStackedWidget()

        # -------- Главное меню --------
        menu = QWidget()
        menu_layout = QVBoxLayout(menu)

        title = QLabel("Системные настройки")
        title.setStyleSheet("color: white; font-size: 26px;")
        menu_layout.addWidget(title)

        # Кнопка звука
        sound_btn = OctagonButton("🔊 Настройки звука")
        sound_btn.setStyleSheet(BUTTON_STYLE)
        sound_btn.clicked.connect(self.open_sound)
        menu_layout.addWidget(sound_btn)

        # Кнопка обоев
        wallpaper_btn = OctagonButton("🖼️ Сменить обои")
        wallpaper_btn.setStyleSheet(BUTTON_STYLE)
        wallpaper_btn.clicked.connect(self.change_wallpaper)
        menu_layout.addWidget(wallpaper_btn)

        # Wi-Fi
        wifi_btn = OctagonButton("📶 Настройки Wi-Fi")
        wifi_btn.setStyleSheet(BUTTON_STYLE)
        wifi_btn.clicked.connect(self.open_wifi_manager)
        menu_layout.addWidget(wifi_btn)

        # -------- Экран звука --------
        self.sound_screen = SoundSettings(self.go_home)

        self.stack.addWidget(menu)
        self.stack.addWidget(self.sound_screen)

        layout = QVBoxLayout(self)
        layout.addWidget(self.stack)

    # ---------- Навигация ----------
    def open_sound(self):
        self.stack.setCurrentWidget(self.sound_screen)

    def go_home(self):
        self.stack.setCurrentIndex(0)

    # ---------- Внешние приложения ----------
    def change_wallpaper(self):
        try:
            subprocess.Popen([sys.executable, "change-wallpaper-app.py"])
        except Exception as e:
            print(f"Не удалось запустить смену обоев: {e}")

    def open_wifi_manager(self):
        try:
            subprocess.Popen([sys.executable, "wifi_manager.py"])
        except Exception as e:
            print(f"Не удалось запустить Wi-Fi менеджер: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
