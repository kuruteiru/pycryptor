from typing import Any
import PySide6.QtWidgets as qtw
import string
import random
import sys

config: dict[str, Any] = {
    "alphabet": string.ascii_lowercase + string.digits
}

def main() -> None:
    if len(sys.argv) == 1:
        app = qtw.QApplication(sys.argv)
        window = App()
        window.show()
        sys.exit(app.exec())

    match sys.argv[1]:
        case "-e" | "-encrypt": print("encrypt")
        case "-d" | "-decrypt": print("decrypt")
        case "-k" | "-keygen": print("key generation")
        case _: print("unknown argument")

def generate_keys(key_size: int) -> tuple[tuple[int, int], tuple[int, int]]:
    p = generate_prime(key_size // 2)
    q = generate_prime(key_size // 2)
    n = p * q
    euler = (p - 1) * (q - 1)

    e = find_coprime(euler)
    d = modular_inverse(e, euler)

    public_key = (e, n)
    private_key = (d, n)

    return (public_key, private_key)

def encrypt(message: str, public_key: tuple[int, int]) -> str:
    e, n = public_key
    return ' '.join(
        str(pow(ord(char), e, n)) 
        for char in message
    )

def decrypt(ciphertext: str, private_key: tuple[int, int]) -> str:
    d, n = private_key
    return ''.join(
        chr(pow(int(chunk), d, n)) 
        for chunk in ciphertext.split()
    )

def generate_prime(bits: int) -> int:
    while True:
        num = random.getrandbits(bits)
        if is_prime(num): return num

def is_prime(num: int) -> bool:
    if num < 2: return False

    for _ in range(10):
        a = random.randint(2, num - 2)
        if pow(a, num - 1, num) != 1: return False

    return True

def find_coprime(euler: int) -> int:
    e = 3
    while gcd(e, euler) != 1: e += 2
    return e

def gcd(a: int, b: int) -> int:
    while b: a, b = b, a % b
    return a

def modular_inverse(a: int, m: int) -> int:
    m0, x0, x1 = m, 0, 1
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0

    return x1 + m0 if x1 < 0 else x1

class App(qtw.QMainWindow):
    def __init__(self) -> None:
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

        self.output_label = qtw.QLabel("output")
        self.main_layout.addWidget(self.output_label)
        self.output_text = qtw.QTextEdit()
        self.output_text.setReadOnly(True)
        self.main_layout.addWidget(self.output_text)

        self.public_key_label = qtw.QLabel("public key")
        self.main_layout.addWidget(self.public_key_label)
        self.public_key_text = qtw.QLineEdit()
        self.main_layout.addWidget(self.public_key_text)

        self.private_key_label = qtw.QLabel("private key")
        self.main_layout.addWidget(self.private_key_label)
        self.private_key_text = qtw.QLineEdit()
        self.main_layout.addWidget(self.private_key_text)

        button_layout = qtw.QHBoxLayout()

        encrypt_button = qtw.QPushButton("encrypt")
        encrypt_button.clicked.connect(self.encrypt)
        button_layout.addWidget(encrypt_button)

        decrypt_button = qtw.QPushButton("decrypt")
        decrypt_button.clicked.connect(self.decrypt)
        button_layout.addWidget(decrypt_button)

        generate_key_button = qtw.QPushButton("generate keys")
        generate_key_button.clicked.connect(self.generate_keys)
        button_layout.addWidget(generate_key_button)

        self.main_layout.addLayout(button_layout)

    def encrypt(self):
        try:
            keys: list[str] = self.public_key_text.text().split(',')
            public_key: tuple[int, int] = (int(keys[0]), int(keys[1]))
            encrypted_text: str = encrypt(self.input_text.toPlainText(), public_key)
            self.output_text.setText(encrypted_text)
        except Exception as e:
            self.output_text.setText(f"error: {e}")

    def decrypt(self):
        try:
            keys: list[str] = self.private_key_text.text().split(',')
            private_key: tuple[int, int] = (int(keys[0]), int(keys[1]))
            decrypted_text: str = decrypt(self.input_text.toPlainText(), private_key)
            self.output_text.setText(decrypted_text)
        except Exception as e:
            self.output_text.setText(f"error: {e}")

    def generate_keys(self):
        try:
            public_key, private_key = generate_keys(2048)
            self.public_key_text.setText(f"{public_key[0]},{public_key[1]}")
            self.private_key_text.setText(f"{private_key[0]},{private_key[1]}")
        except Exception as e:
            self.output_text.setText(f"error: {e}")

if __name__ == "__main__": main()
