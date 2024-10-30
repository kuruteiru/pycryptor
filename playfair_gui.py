from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
import sys
import unicodedata

config = {
    "key": "keynzu",
    "alphabet": "abcdefghijklmnopqrstuvwxyz",
    "substitution_characters": ('x', 'q'),
    "replaced_characters": ('j', 'i')
}

def format_text(input_text: str) -> str:
    formatted_text = [
        c.lower() for c in input_text
        if c.isalnum() or c.isspace()
    ]

    for i in range(len(formatted_text)):
        if formatted_text[i].isspace() or formatted_text[i].isnumeric():
            formatted_text[i] = ('x' + unicodedata.name(formatted_text[i]).replace(' ', '') + 'x').lower()

    formatted_text = [
        c for c in unicodedata.normalize('NFD', ''.join(formatted_text))
        if unicodedata.category(c) != 'Mn'
    ]

    i = 0
    while i < len(formatted_text) - 1:
        if formatted_text[i] == formatted_text[i + 1]:
            sub_char = config["substitution_characters"][0]
            if formatted_text[i] == sub_char:
                sub_char = config["substitution_characters"][1]
            formatted_text.insert(i + 1, sub_char)
        i += 1

    if len(formatted_text) % 2 != 0:
        sub_char = config["substitution_characters"][0]
        if formatted_text[-1] == sub_char:
            sub_char = config["substitution_characters"][1]
        formatted_text.append(sub_char)

    return ''.join(formatted_text)

def create_key_matrix(key: str, alphabet: str) -> list:
    key = key.lower().replace('j', 'i')
    key = sorted(set(key), key=lambda x: key.index(x))
    key += ''.join([x for x in alphabet.replace('j', '') if x not in key])
    return [list(key[i:i + 5]) for i in range(0, 25, 5)]

def character_position(matrix: list, character: str) -> tuple:
    if character == 'j': character = 'i'
    for i, row in enumerate(matrix):
        if character in row: return (i, row.index(character))
    return (-1, -1)

def encrypt(key: str, alphabet: str, input_text: str) -> str:
    matrix = create_key_matrix(key, alphabet)
    formatted_text = format_text(input_text)
    encrypted_text = []

    for i in range(0, len(formatted_text), 2):
        char_a = character_position(matrix, formatted_text[i])
        char_b = character_position(matrix, formatted_text[i + 1])
        if char_a[0] == char_b[0]:
            encrypted_text.append(matrix[char_a[0]][(char_a[1] + 1) % 5] + matrix[char_b[0]][(char_b[1] + 1) % 5])
        elif char_a[1] == char_b[1]:
            encrypted_text.append(matrix[(char_a[0] + 1) % 5][char_a[1]] + matrix[(char_b[0] + 1) % 5][char_b[1]])
        else:
            encrypted_text.append(matrix[char_a[0]][char_b[1]] + matrix[char_b[0]][char_a[1]])

    return ''.join(encrypted_text)

def decrypt(key: str, alphabet: str, encrypted_text: str) -> str:
    matrix = create_key_matrix(key, alphabet)
    decrypted_text = []

    for i in range(0, len(encrypted_text), 2):
        char_a = character_position(matrix, encrypted_text[i])
        char_b = character_position(matrix, encrypted_text[i + 1])
        if char_a[0] == char_b[0]:
            decrypted_text.append(matrix[char_a[0]][(char_a[1] - 1) % 5] + matrix[char_b[0]][(char_b[1] - 1) % 5])
        elif char_a[1] == char_b[1]:
            decrypted_text.append(matrix[(char_a[0] - 1) % 5][char_a[1]] + matrix[(char_b[0] - 1) % 5][char_b[1]])
        else:
            decrypted_text.append(matrix[char_a[0]][char_b[1]] + matrix[char_b[0]][char_a[1]])

    return ''.join(decrypted_text)

class CipherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Playfair Cipher GUI")
        self.setGeometry(200, 200, 600, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        
        self.input_label = QLabel("Input Text:")
        self.layout.addWidget(self.input_label)
        
        self.input_text = QLineEdit()
        self.layout.addWidget(self.input_text)
        
        self.encrypted_label = QLabel("Encrypted Text:")
        self.layout.addWidget(self.encrypted_label)
        
        self.encrypted_text = QTextEdit()
        self.encrypted_text.setReadOnly(True)
        self.layout.addWidget(self.encrypted_text)
        
        self.decrypted_label = QLabel("Decrypted Text:")
        self.layout.addWidget(self.decrypted_label)
        
        self.decrypted_text = QTextEdit()
        self.decrypted_text.setReadOnly(True)
        self.layout.addWidget(self.decrypted_text)
        
        self.button_layout = QHBoxLayout()
        
        self.encrypt_button = QPushButton("Encrypt")
        self.encrypt_button.clicked.connect(self.handle_encrypt)
        self.button_layout.addWidget(self.encrypt_button)
        
        self.decrypt_button = QPushButton("Decrypt")
        self.decrypt_button.clicked.connect(self.handle_decrypt)
        self.button_layout.addWidget(self.decrypt_button)
        
        self.layout.addLayout(self.button_layout)

    def handle_encrypt(self):
        open_text = self.input_text.text()
        encrypted_text = encrypt(config["key"], config["alphabet"], open_text)
        self.encrypted_text.setText(encrypted_text)

    def handle_decrypt(self):
        encrypted_text = self.encrypted_text.toPlainText()
        decrypted_text = decrypt(config["key"], config["alphabet"], encrypted_text)
        self.decrypted_text.setText(decrypted_text)

app = QApplication(sys.argv)
window = CipherApp()
window.show()
sys.exit(app.exec_())

