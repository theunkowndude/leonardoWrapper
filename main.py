import sys
import configparser
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QCheckBox, QTextEdit, QMessageBox, QMenuBar, QFileDialog
)
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QAction
from leonardoWrapper.leonardo import Leonardo  


class ImageGenerationThread(QThread):
    result_signal = pyqtSignal(object)
    error_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)

    def __init__(self, leonardo_instance, prompt, model_id, sd_version, negative_prompt, width, height, amount_of_images, seed, photo_real, high_contrast):
        super().__init__()
        self.leonardo = leonardo_instance
        self.prompt = prompt
        self.model_id = model_id
        self.sd_version = sd_version
        self.negative_prompt = negative_prompt
        self.width = width
        self.height = height
        self.amount_of_images = amount_of_images
        self.seed = seed
        self.photo_real = photo_real
        self.high_contrast = high_contrast

    def run(self):
        try:
            self.status_signal.emit("starting")
            generation_id = self.leonardo.create_generate_image(
                prompt=self.prompt,
                model_id=self.model_id,
                sd_version=self.sd_version,
                negative_prompt=self.negative_prompt,
                width=self.width,
                height=self.height,
                amount_of_images=self.amount_of_images,
                seed=self.seed,
                photo_real=self.photo_real,
                high_contrast=self.high_contrast
            )
            self.status_signal.emit("waiting")
            self.leonardo.wait_for_image_generation(generation_id)
            result = self.leonardo.get_image_generation(generation_id)
            self.result_signal.emit(result)
        except Exception as e:
            self.error_signal.emit(str(e))


class LeonardoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_config()
        self.load_language()
        self.leonardo = None
        self.image_save_path = None

    def initUI(self):
        self.setWindowTitle('Leonardo Image Generation')
        self.setGeometry(100, 100, 600, 400)

        self.setStyleSheet("""
            QWidget {
                background-color: #fff;
                color: #000;
            }
            QPushButton {
                background-color: #000;
                color: #fff;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #ffa500;
            }
            QLineEdit {
                border: 1px solid #000;
                border-radius: 5px;
                padding: 5px;
            }
            QTextEdit {
                border: 1px solid #cc0000;
                border-radius: 5px;
                padding: 5px;
                background-color: #ffffcc;
            }
        """)

        layout = QVBoxLayout()

        # Menu bar for language selection
        menu_bar = QMenuBar(self)
        language_menu = menu_bar.addMenu("Language 🌐")

        english_action = QAction("English", self)
        english_action.triggered.connect(lambda: self.set_language("english"))
        language_menu.addAction(english_action)

        vietnamese_action = QAction("Vietnamese", self)
        vietnamese_action.triggered.connect(lambda: self.set_language("vietnamese"))
        language_menu.addAction(vietnamese_action)

        layout.setMenuBar(menu_bar)

        self.prompt_input = QLineEdit(self)
        layout.addWidget(QLabel("Prompt 📝"))
        layout.addWidget(self.prompt_input)

        self.negative_prompt_input = QLineEdit(self)
        layout.addWidget(QLabel("Negative Prompt 📝"))
        layout.addWidget(self.negative_prompt_input)

        self.model_select = QComboBox(self)
        self.model_select.currentTextChanged.connect(self.update_sd_version)
        layout.addWidget(QLabel("Model"))
        layout.addWidget(self.model_select)

        self.sd_version_label = QLabel(self)
        layout.addWidget(QLabel("⬇ SD Version ⬇ "))
        layout.addWidget(self.sd_version_label)

        self.width_input = QLineEdit(self)
        self.width_input.setText("1536")  # Default value
        layout.addWidget(QLabel("Width"))
        layout.addWidget(self.width_input)

        self.height_input = QLineEdit(self)
        self.height_input.setText("1536")  # Default value
        layout.addWidget(QLabel("Height"))
        layout.addWidget(self.height_input)

        self.amount_of_images_input = QLineEdit(self)
        self.amount_of_images_input.setText("1")
        layout.addWidget(QLabel("Amount of Images🎑"))
        layout.addWidget(self.amount_of_images_input)

        self.seed_input = QLineEdit(self)
        layout.addWidget(QLabel("Seed"))
        layout.addWidget(self.seed_input)

        self.photo_real_checkbox = QCheckBox("Photo Real", self)
        layout.addWidget(self.photo_real_checkbox)

        self.high_contrast_checkbox = QCheckBox("High Contrast", self)
        layout.addWidget(self.high_contrast_checkbox)

        self.select_directory_button = QPushButton("Select Directory", self)
        self.select_directory_button.clicked.connect(self.select_directory)
        layout.addWidget(self.select_directory_button)

        self.generate_button = QPushButton("Generate Image", self)
        self.generate_button.clicked.connect(self.generate_image)
        layout.addWidget(self.generate_button)

        self.result_output = QTextEdit(self)
        self.result_output.setReadOnly(True)
        layout.addWidget(QLabel("Result"))
        layout.addWidget(self.result_output)

        self.status_label = QLabel(self)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def load_config(self):
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8')

        self.username = config['Account']['username']
        self.password = config['Account']['password']
        self.proxy = config['Proxy'].get('proxy', None)

        self.models = {}
        for name, details in config.items('Models'):
            model_id, sd_version = details.split('|')
            self.models[name] = {'id': model_id, 'sd_version': sd_version}
        self.model_select.addItems(self.models.keys())

        self.languages = config['Languages']

    def load_language(self):
        self.current_language = 'english'
        self.set_language(self.current_language)

    def set_language(self, language):
        self.current_language = language
        self.setWindowTitle(self.languages[f'{language}_title'])
        self.prompt_input.setPlaceholderText(self.languages[f'{language}_prompt'])
        self.negative_prompt_input.setPlaceholderText(self.languages[f'{language}_negative_prompt'])
        self.width_input.setPlaceholderText(self.languages[f'{language}_width'])
        self.height_input.setPlaceholderText(self.languages[f'{language}_height'])
        self.amount_of_images_input.setPlaceholderText(self.languages[f'{language}_amount_of_images'])
        self.seed_input.setPlaceholderText(self.languages[f'{language}_seed'])
        self.photo_real_checkbox.setText(self.languages[f'{language}_photo_real'])
        self.high_contrast_checkbox.setText(self.languages[f'{language}_high_contrast'])
        self.select_directory_button.setText(self.languages[f'{language}_select_directory'])
        self.generate_button.setText(self.languages[f'{language}_generate_image'])
        self.result_output.setPlaceholderText(self.languages[f'{language}_result'])

    def update_sd_version(self):
        model_name = self.model_select.currentText()
        self.sd_version_label.setText(self.models[model_name]['sd_version'])

    def generate_image(self):
        if not self.image_save_path:
            self.append_message(self.languages[f'{self.current_language}_select_directory_warning'], 'red')
            return

        if not self.leonardo:
            if self.proxy:
                self.leonardo = Leonardo(username=self.username, password=self.password, proxy=self.proxy)
            else:
                self.leonardo = Leonardo(username=self.username, password=self.password)

        prompt = self.prompt_input.text()
        model_name = self.model_select.currentText()
        model_details = self.models[model_name]
        model_id = model_details['id']
        sd_version = model_details['sd_version']
        negative_prompt = self.negative_prompt_input.text()
        width = int(self.width_input.text())
        height = int(self.height_input.text())
        amount_of_images = int(self.amount_of_images_input.text())
        seed = int(self.seed_input.text()) if self.seed_input.text() else None
        photo_real = self.photo_real_checkbox.isChecked()
        high_contrast = self.high_contrast_checkbox.isChecked()

        self.thread = ImageGenerationThread(self.leonardo, prompt, model_id, sd_version, negative_prompt, width, height, amount_of_images, seed, photo_real, high_contrast)
        self.thread.result_signal.connect(self.display_result)
        self.thread.error_signal.connect(self.display_error)
        self.thread.status_signal.connect(self.update_status)
        self.thread.start()

    def display_result(self, result):
        self.result_output.clear()
        for image in result['generated_images']:
            self.result_output.append(image['url'])
            self.download_image(image['url'])
        self.append_message(self.languages[f'{self.current_language}_completed'], 'green')

    def display_error(self, error):
        self.append_message(error, 'red')
        self.append_message(self.languages[f'{self.current_language}_error'], 'red')

    def update_status(self, status_key):
        status_message = self.languages[f'{self.current_language}_{status_key}']
        color = 'blue' if status_key in ['starting', 'waiting'] else 'green'
        self.append_message(status_message, color)

    def select_directory(self):
        self.image_save_path = QFileDialog.getExistingDirectory(self, self.languages[f'{self.current_language}_select_directory'])
        if self.image_save_path:
            self.append_message(f"{self.languages[f'{self.current_language}_directory_selected']}: {self.image_save_path}", 'blue')

    def download_image(self, url):
        import os
        import requests

        if not self.image_save_path:
            self.image_save_path = os.getcwd()
            self.append_message(f"No directory selected. Using current directory: {self.image_save_path}", 'blue')

        try:
            response = requests.get(url)
            if response.status_code == 200:
                os.makedirs(self.image_save_path, exist_ok=True)
                image_path = os.path.join(self.image_save_path, os.path.basename(url))
                with open(image_path, 'wb') as file:
                    file.write(response.content)
                self.append_message(f"Image successfully saved to: {image_path}", 'green')
            else:
                self.append_message(f"Failed to download image. Status code: {response.status_code}", 'red')
        except Exception as e:
            self.append_message(f"An error occurred while downloading the image: {str(e)}", 'red')

    def append_message(self, message, color):
        self.result_output.append(f"<span style='color:{color};'>{message}</span>")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LeonardoApp()
    window.show()
    sys.exit(app.exec())
