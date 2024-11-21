import PySide6.QtWidgets as qtw
import PySide6.QtCore as qtc
import unicodedata
import sys

config = {
    "alphabet": "abcdefghijklmnopqrstuvwxyz",
    "substitution_characters": ('x', 'q'),
    "replaced_characters": ('j', 'i')
}

def main(): 
    if len(sys.argv) == 1:
        app = qtw.QApplication(sys.argv)
        window = App()
        window.show()
        sys.exit(app.exec())

    match sys.argv[1]:
        case "-e" | "-encrypt": print('encrypt')
        case "-d" | "-decrypt": print('decrypt')
        case "-k" | "-keymatrix": print('keymatrix')
        case "-f" | "-format": print('format')
        case _: print("unknown argument")

def format_text(input_text: str) -> str:
    formatted_text = [
        c.lower() for c in input_text
        if c.isalpha() or c.isspace()
    ]

    formatted_text = [
        c for i, c in enumerate(formatted_text)
        if c != ' ' or (i == 0 or formatted_text[i - 1] != ' ')
    ]

    for i in range(len(formatted_text)):
        if formatted_text[i].isspace():
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

def create_key_matrix(key: str, alphabet: str) -> list[list[str]]:
    key = key.lower().replace('j', 'i')
    key_matrix = [c for c in unicodedata.normalize('NFD', key) if c.isalpha() and unicodedata.category(c) != 'Mn']
    key_matrix = sorted(set(key_matrix), key = lambda x: key_matrix.index(x))
    key_matrix += [x for x in alphabet.replace('j', '') if x not in key_matrix]
    return [key_matrix[i:i+5] for i in range(0, 25, 5)]

def get_coordinates(matrix: list[list[str]], char: str) -> tuple[int, int]:
    if char == 'j': char = 'i'
    for i, row in enumerate(matrix):
        if char in row: return (i, row.index(char))
    return (-1, -1)

def encrypt(key: str, alphabet: str, input_text: str) -> str:
    matrix = create_key_matrix(key, alphabet)
    formatted_text = format_text(input_text)
    encrypted_text = []

    for i in range(0, len(formatted_text), 2):
        char_a = get_coordinates(matrix, formatted_text[i])
        char_b = get_coordinates(matrix, formatted_text[i + 1])
        if char_a[0] == char_b[0]:
            encrypted_text.append(matrix[char_a[0]][(char_a[1] + 1) % 5] + matrix[char_b[0]][(char_b[1] + 1) % 5])
        elif char_a[1] == char_b[1]:
            encrypted_text.append(matrix[(char_a[0] + 1) % 5][char_a[1]] + matrix[(char_b[0] + 1) % 5][char_b[1]])
        else:
            encrypted_text.append(matrix[char_a[0]][char_b[1]] + matrix[char_b[0]][char_a[1]])

    return ''.join(encrypted_text)

def decrypt(key: str, alphabet: str, encrypted_text: str) -> str:
    matrix = create_key_matrix(key, alphabet)
    formatted_text = encrypted_text.lower()
    decrypted_text = []

    if len(formatted_text) % 2 != 0:
        sub_char = config["substitution_characters"][0]
        if formatted_text[-1] == sub_char:
            sub_char = config["substitution_characters"][1]
        formatted_text += sub_char

    for i in range(0, len(formatted_text), 2):
        char_a = get_coordinates(matrix, formatted_text[i])
        char_b = get_coordinates(matrix, formatted_text[i + 1])
        if char_a[0] == char_b[0]:
            decrypted_text.append(matrix[char_a[0]][(char_a[1] - 1) % 5] + matrix[char_b[0]][(char_b[1] - 1) % 5])
        elif char_a[1] == char_b[1]:
            decrypted_text.append(matrix[(char_a[0] - 1) % 5][char_a[1]] + matrix[(char_b[0] - 1) % 5][char_b[1]])
        else:
            decrypted_text.append(matrix[char_a[0]][char_b[1]] + matrix[char_b[0]][char_a[1]])

    space = 'x' + unicodedata.name(' ') + 'x'
    return ''.join(decrypted_text).replace(space.lower(), ' ')

class App(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("playfair")
        # self.setGeometry(200, 200, 600, 400)
        self.central_widget = qtw.QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = qtw.QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.key_label = qtw.QLabel("key")
        self.main_layout.addWidget(self.key_label)
        self.key_text = qtw.QLineEdit()
        self.main_layout.addWidget(self.key_text)

        self.matrix_size = 5
        self.cell_size = 30

        self.key_matrix_table = qtw.QTableWidget(self.matrix_size, self.matrix_size)
        self.key_matrix_table.setFixedSize(self.matrix_size * self.cell_size + 40, self.matrix_size * self.cell_size)
        self.key_matrix_table.setEditTriggers(qtw.QTableWidget.EditTrigger.NoEditTriggers)
        self.key_matrix_table.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.key_matrix_table.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.key_matrix_table.horizontalHeader().setVisible(False)
        self.key_matrix_table.verticalHeader().setVisible(False)

        for i in range(self.matrix_size):
            self.key_matrix_table.setColumnWidth(i, self.cell_size)
            self.key_matrix_table.setRowHeight(i, self.cell_size)

        self.input_label = qtw.QLabel("input")
        self.main_layout.addWidget(self.input_label)
        self.input_text = qtw.QTextEdit()
        self.main_layout.addWidget(self.input_text)

        self.formatted_input_label = qtw.QLabel("formatted input")
        self.main_layout.addWidget(self.formatted_input_label)
        self.formatted_input_text = qtw.QTextEdit()
        self.formatted_input_text.setReadOnly(True)
        self.main_layout.addWidget(self.formatted_input_text)

        v_box_layout = qtw.QHBoxLayout()

        output_label = qtw.QLabel("output")
        self.main_layout.addWidget(output_label)
        self.output_text = qtw.QTextEdit()
        self.output_text.setReadOnly(True)
        v_box_layout.addWidget(self.output_text)
        v_box_layout.addWidget(self.key_matrix_table)
        self.main_layout.addLayout(v_box_layout)

        matrix = create_key_matrix(self.key_text.text(), config["alphabet"])
        
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                item = qtw.QTableWidgetItem(matrix[i][j])
                item.setTextAlignment(qtc.Qt.AlignmentFlag.AlignCenter)
                self.key_matrix_table.setItem(i, j, item)

        button_layout = qtw.QHBoxLayout()

        encrypt_button = qtw.QPushButton("encrypt")
        encrypt_button.clicked.connect(self.encrypt)
        button_layout.addWidget(encrypt_button)

        decrypt_button = qtw.QPushButton("decrypt")
        decrypt_button.clicked.connect(self.decrypt)
        button_layout.addWidget(decrypt_button)

        self.main_layout.addLayout(button_layout)

    def encrypt(self):
        self.update_key_matrix()
        encrypted_text = encrypt(
            self.key_text.text(), 
            config["alphabet"], 
            self.input_text.toPlainText()
        )
        self.output_text.setText(encrypted_text.upper())
        formatted_input = format_text(self.input_text.toPlainText()).upper()
        formatted_input = ''.join([
            c if i == 0 or i % 2 != 0
            else f' {c}'
            for i, c in enumerate(formatted_input)
        ])
        self.formatted_input_text.setText(formatted_input)

    def decrypt(self):
        self.update_key_matrix()
        decrypted_text = decrypt(
            self.key_text.text(), 
            config["alphabet"],
            self.input_text.toPlainText()
        )
        self.output_text.setText(decrypted_text.upper())
        formatted_input = format_text(self.input_text.toPlainText()).upper()
        self.formatted_input_text.setText(formatted_input)
        formatted_input = self.input_text.toPlainText().upper()
        formatted_input = ''.join([
            c if i == 0 or i % 2 != 0
            else f' {c}'
            for i, c in enumerate(formatted_input)
        ])
        self.formatted_input_text.setText(formatted_input)

    def update_key_matrix(self):
        matrix = create_key_matrix(self.key_text.text(), config["alphabet"])
        
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                item = qtw.QTableWidgetItem(matrix[i][j])
                item.setTextAlignment(qtc.Qt.AlignmentFlag.AlignCenter)
                self.key_matrix_table.setItem(i, j, item)


    def clear_layout(self, layout: qtw.QLayout | None): 
        if layout is None: return
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            if item.layout():
                self.clear_layout(item.layout())
                item.layout().deleteLater()

if __name__ == "__main__": main()
