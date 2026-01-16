BUTTON_STYLE = """
QPushButton {
    background-color: #A54242;
    color: #FFFFFF;
    border: none;
    padding: 18px;
    font-size: 20px;
}
QPushButton:hover {
    background-color: #C05050;
}
QPushButton:pressed {
    background-color: #8B2B2B;
}
"""

SLIDER_STYLE = """
QSlider::groove:horizontal {
    height: 14px;
    background: #3A3A3A;
    border-radius: 7px;
}
QSlider::handle:horizontal {
    background: #A54242;
    width: 28px;
    margin: -8px 0;
    border-radius: 14px;
}
"""

# ===========================
# СТИЛИ ДЛЯ ВЫПАДАЮЩЕГО СПИСКА УСТРОЙСТВ
# ===========================

# Кнопка выбора устройства
DEVICE_BUTTON_STYLE = """
QPushButton {
    background-color: #1e1e1e;
    color: white;
    border: 2px solid #3a3a3a;
    border-radius: 10px;
    padding: 6px 12px;
    text-align: left;
}
QPushButton:hover {
    border-color: #4a4a4a;
}
"""

# Popup список устройств
DEVICE_LIST_STYLE = """
QFrame {
    background-color: #1e1e1e;
    border: 2px solid #3a3a3a;
    border-radius: 10px;
}

QListWidget {
    background-color: #1e1e1e;
    border: none;
    outline: 0;
}

QListWidget::item {
    color: white;
    padding: 8px 12px;
}

QListWidget::item:hover {
    background-color: #2a2a2a;
}

QListWidget::item:selected {
    background-color: #3d7eff;
}
"""
