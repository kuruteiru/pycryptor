import PySide6.QtWidgets as qtw
import PySide6.QtCore as qtc
import unicodedata
import sys

config = {
    "alphabet": "abcdefghiklmnopqrstuvwxyz",
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
    
    formatted_text = ''.join([
        c for c in unicodedata.normalize('NFD', ''.join(formatted_text))
        if unicodedata.category(c) != 'Mn'
    ])
    
    formatted_text = formatted_text.replace('j', 'i')
    return formatted_text

def create_key_matrix(key: str, alphabet: str) -> list[list[str]]:
    key = format_text(key)
    key_matrix = sorted(set(key), key = lambda x: key.index(x))
    key_matrix += [x for x in alphabet.replace('j', '') if x not in key_matrix]
    return [key_matrix[i:i+5] for i in range(0, 25, 5)]

def create_columnar_key(key: str) -> list[int]:
    key = format_text(key)
    positions = list(range(len(key)))
    pairs = sorted(zip(key, positions))
    sorted_positions = list(zip(*pairs))[1]
    return sorted_positions

def get_coordinates(key_matrix: list[list[str]], char: str) -> tuple[str, str]:
    coordinates = "ADFGX"
    for i, row in enumerate(key_matrix):
        if char in row: return (coordinates[i], coordinates[row.index(char)])
    return ('', '')

def encrypt(key1: str, key2: str, alphabet: str, input_text: str) -> str:
    matrix = create_key_matrix(key1, alphabet)
    formatted_text = format_text(input_text)
    coordinates = ""
    for char in formatted_text:
        coords = get_coordinates(matrix, char)
        coordinates += coords[0] + coords[1]
    
    key_order = create_columnar_key(key2)
    key_length = len(key2)
    
    if len(coordinates) % key_length != 0:
        x_coords = get_coordinates(matrix, 'x')
        while len(coordinates) % key_length != 0:
            coordinates += x_coords[0] + x_coords[1]
    
    columns = [coordinates[i::key_length] for i in range(key_length)]
    return ''.join(columns[i] for i in key_order)

def decrypt(key1: str, key2: str, alphabet: str, encrypted_text: str) -> str:
    matrix = create_key_matrix(key1, alphabet)
    key_order = create_columnar_key(key2)
    key_length = len(key2)
    col_length = len(encrypted_text) // key_length
    columns = [''] * key_length

    pos = 0
    for i in range(col_length):
        for j in key_order:
            if pos < len(encrypted_text):
                columns[j] += encrypted_text[pos]
                pos += 1
    
    coordinates = ""
    for i in range(col_length):
        for col in columns:
            if i < len(col):
                coordinates += col[i]
    
    decrypted_text = ""
    for i in range(0, len(coordinates), 2):
        row_idx = "ADFGX".index(coordinates[i])
        col_idx = "ADFGX".index(coordinates[i + 1])
        decrypted_text += matrix[row_idx][col_idx]
    
    return decrypted_text

class App(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("adfgx")
        self.central_widget = qtw.QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = qtw.QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.key1_label = qtw.QLabel("key 1")
        self.main_layout.addWidget(self.key1_label)
        self.key1_text = qtw.QLineEdit()
        self.main_layout.addWidget(self.key1_text)

        self.key2_label = qtw.QLabel("key 2")
        self.main_layout.addWidget(self.key2_label)
        self.key2_text = qtw.QLineEdit()
        self.main_layout.addWidget(self.key2_text)

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

        matrix = create_key_matrix(self.key1_text.text(), config["alphabet"])
        
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
        print("encrypt")
        self.update_key_matrix()
        encrypted_text = encrypt(
            self.key1_text.text(), 
            self.key2_text.text(), 
            config["alphabet"], 
            self.input_text.toPlainText()
        )
        self.output_text.setText(encrypted_text.upper())

        formatted_input = format_text(self.input_text.toPlainText()).upper()
        print(f"formated_input: {formatted_input}")
        formatted_input = ''.join([
            c if i == 0 or i % 2 != 0
            else f' {c}'
            for i, c in enumerate(formatted_input)
        ])
        self.formatted_input_text.setText(formatted_input)

    def decrypt(self):
        print("decrypt")
        self.update_key_matrix()
        decrypted_text = decrypt(
            self.key1_text.text(), 
            self.key2_text.text(), 
            config["alphabet"],
            self.input_text.toPlainText()
        )
        self.output_text.setText(decrypted_text.upper())

        formatted_input = format_text(self.input_text.toPlainText()).upper()
        # formatted_input = self.input_text.toPlainText().upper()
        print(f"formated_input: {formatted_input}")
        formatted_input = ''.join([
            c if i == 0 or i % 2 != 0
            else f' {c}'
            for i, c in enumerate(formatted_input)
        ])
        self.formatted_input_text.setText(formatted_input)

    def update_key_matrix(self):
        matrix = create_key_matrix(self.key1_text.text(), config["alphabet"])
        
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
