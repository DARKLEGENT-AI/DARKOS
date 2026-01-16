import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSlider,
    QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QFrame
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QColor

from ui_styles import SLIDER_STYLE, BUTTON_STYLE, DEVICE_BUTTON_STYLE, DEVICE_LIST_STYLE
from widgets import OctagonButton

# ================== ВИДИМЫЕ ДЕЛЕНИЯ ПОД ПОЛЗУНКОМ ==================
class SliderTicks(QWidget):
    def __init__(self, slider, ticks=5, color="#2a2a2a", parent=None):
        """
        slider - QSlider, под которым рисуем деления
        ticks - количество делений (включая крайние)
        color - цвет делений (фон ползунка)
        """
        super().__init__(parent)
        self.slider = slider
        self.ticks = ticks
        self.color = QColor(color)
        self.setFixedHeight(10)

        # Обновление при изменении ширины слайдера
        self.slider.resizeEvent = self._resize_slider

    def _resize_slider(self, event):
        self.update()  # перерисовать деления
        event.accept()  # пропустить стандартный обработчик

    def paintEvent(self, event):
        if self.slider.width() <= 0:
            return
        w = self.slider.width()
        h = self.height()
        p = QPainter(self)
        p.setPen(self.color)
        for i in range(self.ticks):
            x = int(i * (w - 1) / (self.ticks - 1))
            p.drawLine(x, 0, x, h)
        p.end()

# ================== НАШ POPUP СПИСОК ==================
class DevicePopup(QFrame):
    def __init__(self, on_select):
        super().__init__(None, Qt.WindowType.Popup)
        self.on_select = on_select

        self.setStyleSheet(DEVICE_LIST_STYLE)

        self.list = QListWidget(self)
        self.list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list.itemClicked.connect(self._clicked)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(self.list)

    def open(self, button: QPushButton, items: list[str]):
        self.list.clear()
        for i in items:
            QListWidgetItem(i, self.list)
        self.list.setFixedHeight(self.list.sizeHintForRow(0) * len(items))
        self.adjustSize()
        pos = button.mapToGlobal(QPoint(0, button.height() + 4))
        self.move(pos)
        self.show()

    def _clicked(self, item: QListWidgetItem):
        self.on_select(item.text())
        self.close()

# ================== ОСНОВНОЙ КЛАСС ==================
class SoundSettings(QWidget):
    def __init__(self, go_back_callback):
        super().__init__()
        self.go_back = go_back_callback

        self.source_popup = DevicePopup(self.set_source)
        self.sink_popup = DevicePopup(self.set_sink)

        self.init_ui()
        self.load_devices()
        self.load_volume()

    def init_ui(self):
        main = QVBoxLayout(self)
        main.setSpacing(20)

        title = QLabel("🔊 Настройки звука")
        title.setStyleSheet("color: white; font-size: 26px;")
        main.addWidget(title)

        blocks = QHBoxLayout()
        blocks.setSpacing(40)

        # ---------- ВХОД ----------
        in_layout = QVBoxLayout()
        in_layout.setSpacing(12)

        in_title = QLabel("🎤 Вход")
        in_title.setStyleSheet("color: white; font-size: 20px;")
        in_layout.addWidget(in_title)

        self.source_btn = QPushButton("Выбрать микрофон")
        self.source_btn.setStyleSheet(DEVICE_BUTTON_STYLE)
        self.source_btn.clicked.connect(self.show_sources)
        in_layout.addWidget(self.source_btn)

        self.source_slider = QSlider(Qt.Orientation.Horizontal)
        self.source_slider.setRange(0, 100)
        self.source_slider.setStyleSheet(SLIDER_STYLE)
        self.source_slider.valueChanged.connect(self.set_source_volume)
        in_layout.addWidget(self.source_slider)

        # видимые деления под ползунком
        self.source_ticks = SliderTicks(self.source_slider, color="#2a2a2a")
        in_layout.addWidget(self.source_ticks)

        self.source_val = QLabel("0%")
        self.source_val.setStyleSheet("color: white; font-size: 16px;")
        in_layout.addWidget(self.source_val)

        # ---------- ВЫХОД ----------
        out_layout = QVBoxLayout()
        out_layout.setSpacing(12)

        out_title = QLabel("🔈 Выход")
        out_title.setStyleSheet("color: white; font-size: 20px;")
        out_layout.addWidget(out_title)

        self.sink_btn = QPushButton("Выбрать устройство")
        self.sink_btn.setStyleSheet(DEVICE_BUTTON_STYLE)
        self.sink_btn.clicked.connect(self.show_sinks)
        out_layout.addWidget(self.sink_btn)

        self.sink_slider = QSlider(Qt.Orientation.Horizontal)
        self.sink_slider.setRange(0, 100)
        self.sink_slider.setStyleSheet(SLIDER_STYLE)
        self.sink_slider.valueChanged.connect(self.set_sink_volume)
        out_layout.addWidget(self.sink_slider)

        # видимые деления под ползунком
        self.sink_ticks = SliderTicks(self.sink_slider, color="#2a2a2a")
        out_layout.addWidget(self.sink_ticks)

        self.sink_val = QLabel("0%")
        self.sink_val.setStyleSheet("color: white; font-size: 16px;")
        out_layout.addWidget(self.sink_val)

        blocks.addLayout(in_layout)
        blocks.addLayout(out_layout)
        main.addLayout(blocks)

        back = OctagonButton("← Назад")
        back.setStyleSheet(BUTTON_STYLE)
        back.clicked.connect(self.go_back)
        main.addWidget(back)

    # ---------- DEVICES ----------
    def load_devices(self):
        self.sources = self._list("sources")
        self.sinks = self._list("sinks")

    def _list(self, t):
        try:
            out = subprocess.check_output(
                ["pactl", "list", "short", t],
                text=True
            )
            return [l.split("\t")[1] for l in out.splitlines()]
        except Exception:
            return []

    def show_sources(self):
        self.source_popup.open(self.source_btn, self.sources)

    def show_sinks(self):
        self.sink_popup.open(self.sink_btn, self.sinks)

    def set_source(self, name):
        subprocess.run(["pactl", "set-default-source", name])
        self.source_btn.setText(name)
        self.load_volume()

    def set_sink(self, name):
        subprocess.run(["pactl", "set-default-sink", name])
        self.sink_btn.setText(name)
        self.load_volume()

    # ---------- VOLUME ----------
    def _vol(self, t):
        try:
            o = subprocess.check_output(
                ["pactl", f"get-{t}-volume", f"@DEFAULT_{t.upper()}@"],
                text=True
            )
            return int(o.split("/")[1].replace("%", "").strip())
        except Exception:
            return 0

    def load_volume(self):
        sv = self._vol("source")
        kv = self._vol("sink")

        self.source_slider.setValue(sv)
        self.sink_slider.setValue(kv)
        self.source_val.setText(f"{sv}%")
        self.sink_val.setText(f"{kv}%")

    def set_source_volume(self, v):
        subprocess.run(["pactl", "set-source-volume", "@DEFAULT_SOURCE@", f"{v}%"])
        self.source_val.setText(f"{v}%")

    def set_sink_volume(self, v):
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{v}%"])
        self.sink_val.setText(f"{v}%")
