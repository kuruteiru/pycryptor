import text_formatter as tf
from PIL import Image as pimg
from PySide6 import ( 
    QtWidgets as qtw,
    QtCore as qtc,
    QtGui as qtg
)
import sys
import os

def text_to_binary(text: str) -> str:
    return ''.join(
        format(ord(char), '08b')
        for char in text
    )

def binary_to_text(binary: str) -> str:
    return ''.join(
        chr(int(binary[i:i+8], 2))
        for i in range(0, len(binary), 8)
    )

def calculate_image_capacity(image_path: str) -> int:
    img = pimg.open(image_path)
    width, height = img.size
    return (width * height * 3) // 8

def hide_message(image_path: str, message: str, output_path: str) -> bool:
    img = pimg.open(image_path)
    img = img.convert('RGB')
    width, height = img.size

    pixels = img.load()
    if pixels is None: return False
    
    message = tf.normalize_text(message)
    binary_message = text_to_binary(message)
    binary_length = format(len(binary_message), '032b')
    full_binary = binary_length + binary_message

    if len(full_binary) > width * height * 3: return False

    index = 0
    for y in range(height):
        for x in range(width):
            if index >= len(full_binary): break

            r, g, b = pixels[x, y]
            
            new_r = (r & 0xFE) | int(full_binary[index])
            index += 1

            if index < len(full_binary):
                new_g = (g & 0xFE) | int(full_binary[index])
                index += 1
            else:
                new_g = g

            if index < len(full_binary):
                new_b = (b & 0xFE) | int(full_binary[index])
                index += 1
            else:
                new_b = b

            pixels[x, y] = (new_r, new_g, new_b)

    img.save(output_path)
    return True

def extract_message(image_path: str) -> str:
    img = pimg.open(image_path)
    img = img.convert('RGB')
    width, height = img.size
    pixels = img.load()
    if pixels is None: return ''

    binary_length = ''
    index = 0
    for y in range(height):
        for x in range(width):
            if index >= 32: break

            r, g, b = pixels[x, y]
            binary_length += str(r & 1)
            index += 1

            if index < 32:
                binary_length += str(g & 1)
                index += 1

            if index < 32:
                binary_length += str(b & 1)
                index += 1

    message_length = int(binary_length, 2)
    binary_message = ''
    index = 0

    for y in range(height):
        for x in range(width):
            if len(binary_message) >= message_length + 32: break

            r, g, b = pixels[x, y]
            
            if index < message_length + 32:
                binary_message += str(r & 1)
                index += 1

            if index < message_length + 32:
                binary_message += str(g & 1)
                index += 1

            if index < message_length + 32:
                binary_message += str(b & 1)
                index += 1

    binary_message = binary_message[32:]
    return binary_to_text(binary_message)

class App(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("steganography")
        self.central_widget = qtw.QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = qtw.QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        image_group = qtw.QGroupBox("image")
        image_layout = qtw.QVBoxLayout()
        
        input_image_layout = qtw.QHBoxLayout()
        self.image_path_field = qtw.QLineEdit()
        self.image_path_field.setReadOnly(True)
        self.browse_image_button = qtw.QPushButton("select image")
        self.browse_image_button.clicked.connect(self.select_image)
        input_image_layout.addWidget(self.image_path_field)
        input_image_layout.addWidget(self.browse_image_button)
        image_layout.addLayout(input_image_layout)

        self.image_details_label = qtw.QLabel("no image selected")
        image_layout.addWidget(self.image_details_label)

        self.image_preview = qtw.QLabel()
        self.image_preview.setFixedSize(300, 300)
        self.image_preview.setScaledContents(False)
        image_layout.addWidget(self.image_preview)

        image_group.setLayout(image_layout)
        self.main_layout.addWidget(image_group)

        message_group = qtw.QGroupBox("message")
        message_layout = qtw.QVBoxLayout()
        
        self.message_input = qtw.QTextEdit()
        message_layout.addWidget(self.message_input)

        output_layout = qtw.QHBoxLayout()
        self.output_path_field = qtw.QLineEdit()
        self.output_path_field.setReadOnly(True)
        self.browse_output_button = qtw.QPushButton("choose output")
        self.browse_output_button.clicked.connect(self.browse_output)
        output_layout.addWidget(self.output_path_field)
        output_layout.addWidget(self.browse_output_button)
        message_layout.addLayout(output_layout)

        message_group.setLayout(message_layout)
        self.main_layout.addWidget(message_group)

        button_layout = qtw.QHBoxLayout()
        
        self.hide_button = qtw.QPushButton("hide message")
        self.hide_button.clicked.connect(self.hide_message)
        button_layout.addWidget(self.hide_button)

        self.extract_button = qtw.QPushButton("extract message")
        self.extract_button.clicked.connect(self.extract_message)
        button_layout.addWidget(self.extract_button)

        self.main_layout.addLayout(button_layout)

        result_group = qtw.QGroupBox("result")
        result_layout = qtw.QVBoxLayout()
        self.result_text = qtw.QTextEdit()
        self.result_text.setReadOnly(True)
        result_layout.addWidget(self.result_text)
        result_group.setLayout(result_layout)
        self.main_layout.addWidget(result_group)

    def select_image(self):
        file_path, _ = qtw.QFileDialog.getOpenFileName(
            self, 
            "select image", 
            "", 
            "image files (*.png *.jpg *.jpeg *.bmp)"
        )

        if not file_path: return

        self.image_path_field.setText(file_path)
        pixmap = qtg.QPixmap(file_path)
        scaled_pixmap = pixmap.scaled(
            300, 300, 
            qtc.Qt.KeepAspectRatio, 
            qtc.Qt.SmoothTransformation
        )
        self.image_preview.setPixmap(scaled_pixmap)
        
        img = pimg.open(file_path)
        details = (
            f"pixels: {img.width}x{img.height}\n"
            f"size: {os.path.getsize(file_path)} bytes\n"
            f"format: {img.format}\n"
            f"mode: {img.mode}\n"
            f"storage capacity: {calculate_image_capacity(file_path)} chars"
        )
        self.image_details_label.setText(details)

    def browse_output(self):
        """Open file dialog to choose output image."""
        file_path, _ = qtw.QFileDialog.getSaveFileName(
            self, 
            "save steganography image", 
            "", 
            "image files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.output_path_field.setText(file_path)

    def hide_message(self):
        """Hide message in the selected image."""
        try:
            input_image = self.image_path_field.text()
            output_image = self.output_path_field.text()
            message = self.message_input.toPlainText()

            if not input_image or not output_image:
                self.result_text.setText("select input and output images")
                return

            if not message:
                self.result_text.setText("enter a message to hide")
                return

            success = hide_message(input_image, message, output_image)
            
            if success:
                pixmap = qtg.QPixmap(output_image)
                scaled_pixmap = pixmap.scaled(
                    300, 300, 
                    qtc.Qt.KeepAspectRatio, 
                    qtc.Qt.SmoothTransformation
                )
                self.image_preview.setPixmap(scaled_pixmap)
                
                self.result_text.setText(f"message hidden successfully in {output_image}")
            else:
                self.result_text.setText("message too long for selected image")

        except Exception as e:
            self.result_text.setText(f"error: {str(e)}")

    def extract_message(self):
        try:
            input_image = self.image_path_field.text()
            if not input_image:
                self.result_text.setText("select an image")
                return

            message = extract_message(input_image)
            self.result_text.setText(message)

        except Exception as e:
            self.result_text.setText(f"error: {str(e)}")

def main():
    if len(sys.argv) == 1:
        app = qtw.QApplication(sys.argv)
        stylesheet_path = "../stylesheet"
        try: 
            with open(stylesheet_path, "r") as stylesheet:
                app.setStyleSheet(stylesheet.read())
        except FileNotFoundError:
            print("stylesheet file does not exist")
        except IOError:
            print("error reading stylesheet file")

        window = App()
        window.show()
        sys.exit(app.exec())

if __name__ == "__main__": main()
