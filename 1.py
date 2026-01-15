import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextBrowser, QListView, QHBoxLayout, QAbstractItemView
from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QColor, QPalette, QFont

class ChatApp(QWidget):
    def __init__(self):
        super().__init__()

        # Инициализация UI
        self.selected_model = None  # Модель, выбранная пользователем
        self.initUI()

    def initUI(self):
        # Заголовок окна
        self.setWindowTitle('Chat with Ollama')

        # Настройка фона окна
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Background, QColor('#1F1F1F'))  # Темный фон
        self.setPalette(palette)

        # Основной layout (вертикальный)
        layout = QVBoxLayout()

        # Метка для выбора модели
        self.label = QLabel('Выберите модель:', self)
        self.label.setStyleSheet("color: #FFFFFF; font-size: 16px;")
        layout.addWidget(self.label)

        # Создаем кастомный выпадающий список (QListView)
        self.model_list_view = QListView(self)
        self.model_list_view.setStyleSheet("""
            background-color: #2A2A2A;
            color: #FFFFFF;
            border-radius: 5px;
            font-size: 14px;
            padding: 5px;
        """)
        self.model_list_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.model_list_view.setSpacing(2)  # Между элементами

        # Модель данных для списка
        self.model_list = QStringListModel(self)
        self.model_list_view.setModel(self.model_list)
        self.model_list_view.clicked.connect(self.on_select_model)
        layout.addWidget(self.model_list_view)

        # Чат (QTextBrowser для отображения сообщений)
        self.chat_display = QTextBrowser(self)
        self.chat_display.setStyleSheet("""
            background-color: #2A2A2A;
            color: #FFFFFF;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #A54242;
            font-size: 14px;
        """)
        layout.addWidget(self.chat_display)

        # Контейнер для ввода текста и кнопки
        input_layout = QHBoxLayout()

        # Поле ввода текста
        self.text_input = QLineEdit(self)
        self.text_input.setStyleSheet("""
            background-color: #2A2A2A;
            color: #FFFFFF;
            padding: 8px;
            border-radius: 5px;
            border: 1px solid #A54242;
            font-size: 14px;
        """)
        self.text_input.setEnabled(False)  # Изначально поле ввода отключено
        input_layout.addWidget(self.text_input)

        # Кнопка отправки
        self.button = QPushButton('Отправить', self)
        self.button.setStyleSheet("""
            background-color: #A54242;
            color: #FFFFFF;
            padding: 10px;
            border-radius: 5px;
            font-size: 14px;
        """)
        self.button.setEnabled(False)  # Изначально кнопка отправки отключена
        self.button.clicked.connect(self.on_send)
        input_layout.addWidget(self.button)

        # Добавляем контейнер для ввода и кнопки в основной layout
        layout.addLayout(input_layout)

        # Устанавливаем layout
        self.setLayout(layout)

        # Настройка размеров окна
        self.resize(400, 500)

        # Получаем список доступных моделей Ollama
        self.get_ollama_models()

    def get_ollama_models(self):
        # Получаем список моделей через команду "ollama list"
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            if result.returncode == 0:
                models = result.stdout.splitlines()  # Разделяем вывод на строки
                self.model_list.setStringList(["Выберите модель"] + models)  # Добавляем модели в список
            else:
                self.chat_display.append(f"Ошибка при получении моделей: {result.stderr.strip()}")
        except Exception as e:
            self.chat_display.append(f"Ошибка при вызове Ollama: {str(e)}")

    def on_select_model(self):
        # Получаем выбранную модель из списка
        selected_model = self.model_list_view.selectedIndexes()
        
        if not selected_model:
            return  # Ничего не выбрано, выходим

        selected_model = self.model_list.stringList()[selected_model[0].row()]
        
        if selected_model == "Выберите модель":
            return  # Не активируем чат, если модель не выбрана

        self.selected_model = selected_model
        self.chat_display.append(f"<b>Ollama:</b> Вы выбрали модель: {selected_model}")
        
        # Переключаем интерфейс в режим чата
        self.text_input.setEnabled(True)
        self.button.setEnabled(True)

    def on_send(self):
        # Получаем текст из поля ввода
        user_message = self.text_input.text()
        
        if user_message.strip() == '':
            return

        # Добавляем сообщение пользователя в чат
        self.chat_display.append(f"<b>Вы:</b> {user_message}")

        # Отправляем сообщение в выбранную модель и получаем ответ
        response = self.get_ollama_response(user_message)

        # Добавляем ответ от модели в чат
        self.chat_display.append(f"<b>{self.selected_model}:</b> {response}")

        # Очистить поле ввода
        self.text_input.clear()

    def get_ollama_response(self, message):
        try:
            # Выполнение команды Ollama через subprocess
            result = subprocess.run(
                ['ollama', 'run', self.selected_model],  # Пробуем только имя модели без лишних данных
                input=message, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            
            if result.returncode == 0:
                return result.stdout.strip()  # Ответ от модели
            else:
                return f"Ошибка: {result.stderr.strip()}"
        
        except Exception as e:
            return f"Ошибка при вызове Ollama: {str(e)}"


if __name__ == '__main__':
    # Создаем экземпляр приложения
    app = QApplication(sys.argv)

    # Создаем и показываем окно приложения
    window = ChatApp()
    window.show()

    # Запуск основного цикла приложения
    sys.exit(app.exec_())
