from string import ascii_lowercase
from typing import Any
from math import gcd
import PySide6.QtWidgets as qtw
import text_formatter as tf
import sys

config: dict[str, Any] = {
    "alphabet": ascii_lowercase,
}

def main() -> None:
    if len(sys.argv) == 1:
        app = qtw.QApplication(sys.argv)
        window = App()
        window.show()
        sys.exit(app.exec())

    match sys.argv[1]:
        case "-e" | "-encrypt": print('encrypt')
        case "-d" | "-decrypt": print('decrypt')
        case "-f" | "-format": print('format')
        case _: print("unknown argument")

def modular_inverse(a: int, m: int) -> int | None:
    if m == 0: return None
    if gcd(a, m) != 1: return None

    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1: return x

    return None

def format_encryption_input(input_text: str) -> str:
    if len(input_text) <= 0: return input_text
    char_map: dict[str, str] = tf.get_char_map()
    formatted_text: str = tf.normalize_text(input_text, char_map=char_map)
    return formatted_text

def format_decryption_input(input_text: str) -> str:
    if len(input_text) <= 0: return input_text
    char_map: dict[str, str] = tf.get_deleting_char_map()
    formatted_text: str = tf.normalize_text(input_text, char_map=char_map)
    return formatted_text

def encrypt(input_text: str, a: int, b: int, alphabet: str) -> str | None:
    if len(input_text) <= 0: return input_text

    m: int = len(alphabet)
    if m == 0: return None

    if modular_inverse(a, m) is None: return ''

    formatted_text: str = format_encryption_input(input_text)
    encrypted_text: list[str] = []
    for char in formatted_text:
        if char in alphabet:
            x: int = alphabet.index(char)
            encrypted_text.append(alphabet[(a * x + b) % m])
        else:
            encrypted_text.append(char)

    return ''.join(encrypted_text)

def decrypt(input_text: str, a: int, b: int, alphabet: str) -> str | None:
    if len(input_text) <= 0: return input_text

    m: int = len(alphabet)
    if m == 0: return None

    a_inv: int | None = modular_inverse(a, m)
    if a_inv is None: return ''

    formatted_text: str = format_decryption_input(input_text)
    decrypted_text: list[str] = []
    for char in formatted_text:
        if char in alphabet:
            x: int = alphabet.index(char)
            decrypted_text.append(alphabet[(a_inv * (x - b)) % m])
        else:
            decrypted_text.append(char)

    char_map: dict[str, str] = tf.get_char_map()
    return tf.replace_char_map_values(''.join(decrypted_text), char_map=char_map)

class App(qtw.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("affine")
        self.central_widget = qtw.QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = qtw.QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.a_label = qtw.QLabel("multiplier (a)")
        self.main_layout.addWidget(self.a_label)
        self.a_input = qtw.QSpinBox()
        self.a_input.setRange(1, len(config["alphabet"]) - 1)
        self.main_layout.addWidget(self.a_input)

        self.b_label = qtw.QLabel("additive Shift (b)")
        self.main_layout.addWidget(self.b_label)
        self.b_input = qtw.QSpinBox()
        self.b_input.setRange(0, len(config["alphabet"]) - 1)
        self.main_layout.addWidget(self.b_input)

        self.input_label = qtw.QLabel("input")
        self.main_layout.addWidget(self.input_label)
        self.input_text = qtw.QTextEdit()
        self.main_layout.addWidget(self.input_text)

        self.formatted_input_label = qtw.QLabel("formatted Input")
        self.main_layout.addWidget(self.formatted_input_label)
        self.formatted_input_text = qtw.QTextEdit()
        self.formatted_input_text.setReadOnly(True)
        self.main_layout.addWidget(self.formatted_input_text)

        self.output_label = qtw.QLabel("output")
        self.main_layout.addWidget(self.output_label)
        self.output_text = qtw.QTextEdit()
        self.output_text.setReadOnly(True)
        self.main_layout.addWidget(self.output_text)

        button_layout = qtw.QHBoxLayout()

        encrypt_button = qtw.QPushButton("encrypt")
        encrypt_button.clicked.connect(self.encrypt)
        button_layout.addWidget(encrypt_button)

        decrypt_button = qtw.QPushButton("decrypt")
        decrypt_button.clicked.connect(self.decrypt)
        button_layout.addWidget(decrypt_button)

        self.main_layout.addLayout(button_layout)

    def encrypt(self):
        a = self.a_input.value()
        b = self.b_input.value()
        input_text = self.input_text.toPlainText()

        formatted_input = format_encryption_input(input_text)
        self.formatted_input_text.setText(formatted_input.upper())

        encrypted_text = encrypt(input_text, a, b, config["alphabet"])
        if encrypted_text is not None:
            self.output_text.setText(tf.groups_of(encrypted_text.upper(), 5))

    def decrypt(self):
        a = self.a_input.value()
        b = self.b_input.value()
        input_text = self.input_text.toPlainText()

        formatted_input = format_encryption_input(input_text)
        self.formatted_input_text.setText(formatted_input.upper())

        decrypted_text = decrypt(input_text, a, b, config["alphabet"])
        if decrypted_text is not None:
            self.output_text.setText(decrypted_text.upper())

if __name__ == "__main__": main()
