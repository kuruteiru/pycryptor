import sys
import unicodedata
import PySide6.QtWidgets as qtw

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
        #if formatted_text[i].isspace() or formatted_text[i].isnumeric():
        if not formatted_text[i].isalpha():
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
    print(formatted_text)
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
    # formatted_text = format_text(encrypted_text)
    formatted_text = encrypted_text
    if len(formatted_text) % 2 != 0:
        sub_char = config["substitution_characters"][0]
        if formatted_text[-1] == sub_char:
            sub_char = config["substitution_characters"][1]
        formatted_text.append(sub_char)

    print(formatted_text)
    decrypted_text = []

    for i in range(0, len(formatted_text), 2):
        char_a = character_position(matrix, formatted_text[i])
        char_b = character_position(matrix, formatted_text[i + 1])
        if char_a[0] == char_b[0]:
            decrypted_text.append(matrix[char_a[0]][(char_a[1] - 1) % 5] + matrix[char_b[0]][(char_b[1] - 1) % 5])
        elif char_a[1] == char_b[1]:
            decrypted_text.append(matrix[(char_a[0] - 1) % 5][char_a[1]] + matrix[(char_b[0] - 1) % 5][char_b[1]])
        else:
            decrypted_text.append(matrix[char_a[0]][char_b[1]] + matrix[char_b[0]][char_a[1]])

    return ''.join(decrypted_text)

class CipherApp(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("playfair")
        self.setGeometry(200, 200, 600, 400)
        self.central_widget = qtw.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = qtw.QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.key_label = qtw.QLabel("key")
        self.layout.addWidget(self.key_label)
        self.key_text = qtw.QLineEdit()
        self.layout.addWidget(self.key_text)
        
        self.input_label = qtw.QLabel("input")
        self.layout.addWidget(self.input_label)
        self.input_text = qtw.QTextEdit()
        self.layout.addWidget(self.input_text)

        self.output_label = qtw.QLabel("output")
        self.layout.addWidget(self.output_label)
        self.output_text = qtw.QTextEdit()
        self.output_text.setReadOnly(True)
        self.layout.addWidget(self.output_text)
        
        self.button_layout = qtw.QHBoxLayout()
        
        self.encrypt_button = qtw.QPushButton("encrypt")
        self.encrypt_button.clicked.connect(self.handle_encrypt)
        self.button_layout.addWidget(self.encrypt_button)
        
        self.decrypt_button = qtw.QPushButton("decrypt")
        self.decrypt_button.clicked.connect(self.handle_decrypt)
        self.button_layout.addWidget(self.decrypt_button)
        
        self.layout.addLayout(self.button_layout)

    def handle_encrypt(self):
        print(self.key_text.text())
        encrypted_text = encrypt(self.key_text.text(), config["alphabet"], self.input_text.toPlainText())
        self.output_text.setText(encrypted_text)

    def handle_decrypt(self):
        print(self.key_text.text())
        decrypted_text = decrypt(self.key_text.text(), config["alphabet"], self.input_text.toPlainText())
        self.output_text.setText(decrypted_text)

app = qtw.QApplication(sys.argv)
window = CipherApp()
window.show()
sys.exit(app.exec_())
