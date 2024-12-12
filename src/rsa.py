from PySide6 import QtWidgets as qtw
import text_formatter as tf
from math import gcd
import random
import sys

BIT_LENGTH = 512
BLOCK_SIZE = 4
ASCII_BITS = 8

def main():
    if len(sys.argv) == 1:
        app = qtw.QApplication(sys.argv)

        stylesheet_path = "../stylesheet"
        try: 
            with open(stylesheet_path, "r") as stylesheet:
                app.setStyleSheet(stylesheet.read())
        except FileNotFoundError:
            print("the stylesheet file does not exist")
        except IOError:
            print("an error occurred while reading stylesheet file")
        except:
            print("stylesheet error")

        window = App()
        window.show()
        sys.exit(app.exec())

    match sys.argv[1]:
        case "-e" | "-encrypt": print('encrypt')
        case "-d" | "-decrypt": print('decrypt')
        case "-k" | "-keygen": print('keygen')
        case _: print("unknown argument")
        
def is_prime(n, k = 50): 
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0: return False
    
    def miller_test(d, n):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1: return True
        while d != n - 1:
            x = (x * x) % n
            d *= 2
            if x == 1: return False
            if x == n - 1: return True
        return False
    
    d = n - 1
    while d % 2 == 0: d //= 2
    
    for _ in range(k):
        if not miller_test(d, n): return False

    return True

def generate_large_prime(bit_length: int) -> int:
    while True:
        prime_candidate = random.getrandbits(bit_length)
        if is_prime(prime_candidate): return prime_candidate

def generate_keys(bit_length: int = 4096) -> tuple[tuple[int, int], tuple[int, int]]:
    p = generate_large_prime(bit_length)
    q = generate_large_prime(bit_length)
    n = p * q
    phi = (p - 1) * (q - 1)
    e = random.randint(2, phi - 1)
    while gcd(e, phi) != 1:
        e = random.randint(2, phi - 1)
    d = pow(e, -1, phi)
    return (n, e), (n, d)

def text_to_numeric(text: str) -> int:
    binary = ''.join(
        format(ord(char), f'0{ASCII_BITS}b')
        for char in text
    )
    return int(binary, 2)

def numeric_to_text(number: int) -> str:
    binary = format(number, 'b')
    padded_binary = binary.zfill(
        (len(binary) + ASCII_BITS - 1) // ASCII_BITS * ASCII_BITS
    )
    chars = [
        chr(int(padded_binary[i:i+ASCII_BITS], 2))
        for i in range(0, len(padded_binary), ASCII_BITS)
    ]
    return ''.join(chars)

def encrypt(message: str, public_key: tuple[int, int]) -> list[int]:
    n, e = public_key
    blocks = [
        text_to_numeric(message[i:i+BLOCK_SIZE])
        for i in range(0, len(message), BLOCK_SIZE)
    ]
    return [pow(block, e, n) for block in blocks]

def decrypt(ciphertext: list[int], private_key: tuple[int, int]) -> str:
    n, d = private_key
    blocks = [
        pow(block, d, n)
        for block in ciphertext
    ]
    return ''.join(numeric_to_text(block) for block in blocks)

class App(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("rsa")
        self.central_widget = qtw.QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = qtw.QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.input_label = qtw.QLabel("input")
        self.main_layout.addWidget(self.input_label)
        self.input_text = qtw.QTextEdit()
        self.main_layout.addWidget(self.input_text)

        self.input_label = qtw.QLabel("public key (n, e)")
        self.main_layout.addWidget(self.input_label)
        self.public_key_field = qtw.QLineEdit()
        self.main_layout.addWidget(self.public_key_field)

        self.input_label = qtw.QLabel("private key (n, d)")
        self.main_layout.addWidget(self.input_label)
        self.private_key_field = qtw.QLineEdit()
        self.main_layout.addWidget(self.private_key_field)

        self.input_label = qtw.QLabel("output")
        self.main_layout.addWidget(self.input_label)
        self.output_text = qtw.QTextEdit()
        self.output_text.setReadOnly(True)
        self.main_layout.addWidget(self.output_text)

        button_layout = qtw.QHBoxLayout()

        self.generate_keys_button = qtw.QPushButton("generate keys")
        self.generate_keys_button.clicked.connect(self.generate_keys)
        button_layout.addWidget(self.generate_keys_button)

        self.encrypt_button = qtw.QPushButton("encrypt")
        self.encrypt_button.clicked.connect(self.encrypt_text)
        button_layout.addWidget(self.encrypt_button)

        self.decrypt_button = qtw.QPushButton("decrypt")
        self.decrypt_button.clicked.connect(self.decrypt_text)
        button_layout.addWidget(self.decrypt_button)

        self.main_layout.addLayout(button_layout)

        self.generate_keys()

    def encrypt_text(self):
        try:
            text = tf.normalize_text(self.input_text.toPlainText())
            public_key = eval(self.public_key_field.text())
            encrypted = encrypt(text, public_key)
            self.output_text.setText(str(encrypted))
        except Exception as e:
            self.output_text.setText(f"error: {e}")

    def decrypt_text(self):
        try:
            text = eval(self.output_text.toPlainText())
            private_key = eval(self.private_key_field.text())
            decrypted = decrypt(text, private_key)
            self.output_text.setText(decrypted)
        except Exception as e:
            self.output_text.setText(f"error: {e}")

    def generate_keys(self):
        try:
            self.public_key, self.private_key = generate_keys(BIT_LENGTH)
            self.public_key_field.setText(str(self.public_key))
            self.private_key_field.setText(str(self.private_key))
        except Exception as e:
            self.output_text.setText(f"error: {e}")

if __name__ == "__main__": main()
