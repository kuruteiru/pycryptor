from PySide6 import QtWidgets as qtw
from hashlib import sha3_512
import zipfile
import base64
import rsa
import sys
import os

# sys.set_int_max_str_digits(100000)

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
        case "-n" | "-nzu": print('nzu')
        case _: print("unknown argument")

def hash_file(file_path: str) -> str:
    hasher = sha3_512()
    with open(file_path, "rb") as file:
        while chunk := file.read(4096):
            hasher.update(chunk)
    return hasher.hexdigest()

def sign_file(file_path: str, private_key: tuple[int, int]) -> str:
    file_hash = hash_file(file_path)
    encrypted_blocks = rsa.encrypt(file_hash, private_key)
    return base64.b64encode(str(encrypted_blocks).encode()).decode()

def verify_signature(file_path: str, signature: str, public_key: tuple[int, int]) -> bool:
    if signature.startswith('rsa_sha3-512 '):
        signature = signature.split(' ')[1]

    file_hash = hash_file(file_path)
    padding = len(signature) % 4

    if padding != 0: 
        signature += '=' * (4 - padding)
    
    decoded_str = base64.b64decode(signature).decode()
    encrypted_blocks = eval(decoded_str)
    decrypted_hash = rsa.decrypt(encrypted_blocks, public_key)

    return decrypted_hash == file_hash

def save_keys(public_key: tuple[int, int], private_key: tuple[int, int], save_dir: str) -> None:
    public_key_path = os.path.join(save_dir, "key.pub")
    private_key_path = os.path.join(save_dir, "key.priv")

    with open(public_key_path, "w") as pub_file:
            pub_file.write(f"rsa {base64.b64encode(str(public_key).encode()).decode()}")

    with open(private_key_path, "w") as priv_file:
        priv_file.write(f"rsa {base64.b64encode(str(private_key).encode()).decode()}")

def load_key(file_path: str) -> tuple[int, int]:
    with open(file_path, "r") as key_file:
        content = key_file.read().strip().split(" ")[1]

    return eval(base64.b64decode(content).decode())

def package_signed_file(file_path: str, signature: str, save_dir: str) -> None:
    zip_path = os.path.join(save_dir, os.path.basename(file_path) + ".zip")
    sign_path = os.path.splitext(file_path)[0] + ".sign"

    with open(sign_path, "w") as sign_file:
        sign_file.write(f"rsa_sha3-512 {signature}")

    with zipfile.ZipFile(zip_path, "w") as zip_file:
        zip_file.write(file_path, os.path.basename(file_path))
        zip_file.write(sign_path, os.path.basename(sign_path))

    os.remove(sign_path)

class App(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("dsa")
        self.central_widget = qtw.QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = qtw.QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.file_label = qtw.QLabel("file: no file selected")
        self.main_layout.addWidget(self.file_label)

        self.status_label = qtw.QLabel("")
        self.main_layout.addWidget(self.status_label)

        self.select_file_button = qtw.QPushButton("select file")
        self.select_file_button.clicked.connect(self.select_file)
        self.main_layout.addWidget(self.select_file_button)

        self.load_keys_layout = qtw.QHBoxLayout()

        self.load_public_key_button = qtw.QPushButton("load public key")
        self.load_public_key_button.clicked.connect(self.load_public_key)
        self.load_keys_layout.addWidget(self.load_public_key_button)

        self.load_private_key_button = qtw.QPushButton("load private key")
        self.load_private_key_button.clicked.connect(self.load_private_key)
        self.load_keys_layout.addWidget(self.load_private_key_button)

        self.main_layout.addLayout(self.load_keys_layout)

        self.generate_keys_button = qtw.QPushButton("generate keys")
        self.generate_keys_button.clicked.connect(self.generate_keys)
        self.main_layout.addWidget(self.generate_keys_button)

        self.sign_button = qtw.QPushButton("sign file")
        self.sign_button.clicked.connect(self.sign_file)
        self.sign_button.setEnabled(False)
        self.main_layout.addWidget(self.sign_button)

        self.verify_button = qtw.QPushButton("verify signature")
        self.verify_button.clicked.connect(self.verify_signature)
        self.verify_button.setEnabled(False)
        self.main_layout.addWidget(self.verify_button)

        self.main_layout.addStretch()

        self.private_key: tuple[int, int] | None = None
        self.public_key: tuple[int, int] | None = None
        self.file_path: str | None = None

    def select_file(self) -> None:
        file_path, _ = qtw.QFileDialog.getOpenFileName(self, "select file")
        if not file_path: return

        self.file_path = file_path
        self.file_label.setText(f"file: {file_path}")
        self.sign_button.setEnabled(True)
        self.verify_button.setEnabled(True)

    def load_public_key(self) -> None:
        key_path , _ = qtw.QFileDialog.getOpenFileName(self, "select public key")
        if not key_path: return

        if os.path.splitext(key_path)[1] != ".pub":
            self.status_label.setText("public key file must have a .pub extension")
            return

        self.public_key = load_key(key_path)
        self.status_label.setText("public key loaded")

    def load_private_key(self) -> None:
        key_path , _ = qtw.QFileDialog.getOpenFileName(self, "select private key")
        if not key_path: return

        if os.path.splitext(key_path)[1] != ".priv":
            self.status_label.setText("private key file must have a .priv extension")
            return

        self.private_key = load_key(key_path)
        self.status_label.setText("private key loaded")

    def generate_keys(self) -> None:
        try:
            self.public_key, self.private_key = rsa.generate_keys(512)
            save_dir = qtw.QFileDialog.getExistingDirectory(self, "select directory to save keys")
            if not save_dir: return

            save_keys(self.public_key, self.private_key, save_dir)
            self.status_label.setText("keys generated and saved")

        except Exception as e: print(e)

    def sign_file(self) -> None:
        if not self.file_path or not self.private_key:
            self.status_label.setText("no file selected or keys missing")
            return

        try:
            signature = sign_file(self.file_path, self.private_key)
            save_dir = qtw.QFileDialog.getExistingDirectory(self, "select directory to save signed file")
            if not save_dir: return

            package_signed_file(self.file_path, signature, save_dir)
            self.status_label.setText("file signed and saved")

        except Exception as e: print(e)

    def verify_signature(self) -> None:
        if not self.file_path:
            self.status_label.setText("no file selected")
            return

        try:
            sign_path, _ = qtw.QFileDialog.getOpenFileName(self, "select sign file")
            key_path, _ = qtw.QFileDialog.getOpenFileName(self, "select public key")
            if not sign_path or not key_path: return
            
            with open(sign_path, "r") as sign_file:
                content = sign_file.read().strip()
                signature = content.split(' ')[1]

            public_key = load_key(key_path)
            
            if verify_signature(self.file_path, signature, public_key):
                self.status_label.setText("signature valid")
            else:
                self.status_label.setText("signature invalid")

        except Exception as e: print(e)

if __name__ == "__main__": main()
