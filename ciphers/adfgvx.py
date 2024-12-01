from typing import Any
import text_formatter as tf
import PySide6.QtWidgets as qtw
import PySide6.QtCore as qtc
import random
import string
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
        case "-e" | "-encrypt": print('encrypt')
        case "-d" | "-decrypt": print('decrypt')
        case "-k" | "-keymatrix": print('keymatrix')
        case "-f" | "-format": print('format')
        case _: print("unknown argument")

def format_text(input_text: str) -> str:
    if len(input_text) <= 0: return input_text

    char_map: dict[str, str] = tf.get_char_map()
    formatted_text: str = tf.normalize_text(input_text, char_map=char_map)

    return formatted_text

def create_key_matrix(key: str, alphabet: str) -> list[list[str]]:
    if len(key) > 0:
        char_map = {' ': ''}
        for c in char_map: char_map[c] = ''
        key = tf.normalize_text(key, char_map=char_map)

    key_matrix = sorted(set(key), key=lambda x: key.index(x))
    key_matrix += [x for x in alphabet if x not in key_matrix]

    size = 6
    return [key_matrix[i:i+size] for i in range(0, len(key_matrix), size)]

def create_columnar_key(key: str) -> list[int]:
    if len(key) <= 0: return []

    key = format_text(key)
    positions: list[int] = list(range(len(key)))
    pairs: list[tuple[str, int]] = sorted(zip(key, positions))
    sorted_positions: list[int] = list(zip(*pairs))[1]

    return sorted_positions

def random_alphabet(length: int) -> str:
    alphabet: str = string.ascii_lowercase + string.digits
    result: list[str] = random.sample(alphabet, length)
    return ''.join(result)

def get_coordinates(key_matrix: list[list[str]], char: str) -> tuple[str, str]:
    coordinates: str = "ADFGVX"
    for i, row in enumerate(key_matrix):
        if char in row:
            return (coordinates[i], coordinates[row.index(char)])
    return ('', '')

def encrypt(input_text: str, key1: str, key2: str, alphabet: str) -> str:
    if len(input_text) <= 0: return input_text
    key1 = key1.replace(' ', '')
    key2 = key2.replace(' ', '')

    matrix: list[list[str]] = create_key_matrix(key1, alphabet)
    formatted_text: str = format_text(input_text)

    coordinates: str = '' 
    for char in formatted_text:
        coords: tuple[str, str] = get_coordinates(matrix, char)
        coordinates += coords[0] + coords[1]

    key_order: list[int] = create_columnar_key(key2)
    key_length: int = len(key2)

    columns: list[str] = [coordinates[i::key_length] for i in range(key_length)]
    encrypted_text = ''.join(columns[i] for i in key_order)

    # uncomment for presentation, delete afterwards
    # separated: list[str] = []
    # cc = 0
    # for i, c in enumerate(encrypted_text):
    #     current_col_length = len(columns[cc])
    #     if i == 0 or i % current_col_length != 0:
    #         separated.append(c)
    #     else: 
    #         separated.append(f' {c}')
    #         if cc < len(columns) - 1: cc += 1
    # encrypted_text = ''.join(separated)

    return encrypted_text

def decrypt(input_text: str, key1: str, key2: str, alphabet: str) -> str:
    if len(input_text) <= 0: return input_text
    input_text = input_text.replace(' ', '')
    key1 = key1.replace(' ', '')
    key2 = key2.replace(' ', '')

    matrix: list[list[str]] = create_key_matrix(key1, alphabet)
    key_order: list[int] = create_columnar_key(key2)
    key_length: int = len(key2)

    col_lengths: list[int] = [
            len(input_text) // key_length if key_length > 0 else 0
    ] * key_length
    remainder: int = len(input_text) % key_length if key_length > 0 else 0
    for i in range(remainder): col_lengths[i] += 1

    columns: list[str] = [''] * key_length
    pos: int = 0
    for i in key_order:
        columns[i] = input_text[pos:pos+col_lengths[i]]
        pos += col_lengths[i]

    coordinates: str = ''
    for i in range(max(col_lengths)):
        for col in columns:
            if i >= len(col): continue
            coordinates += col[i]

    decrypted_text: str = ''
    for i in range(0, len(coordinates), 2):
        row_idx: int = "ADFGVX".index(coordinates[i])
        col_idx: int = "ADFGVX".index(coordinates[i + 1])
        decrypted_text += matrix[row_idx][col_idx]

    char_map: dict[str, str] = tf.get_char_map()
    decrypted_text = tf.replace_char_map_values(decrypted_text, char_map)

    return decrypted_text

class App(qtw.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("adfgvx")
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

        self.matrix_size = 6
        self.cell_size = 30

        self.key_matrix_table = qtw.QTableWidget(self.matrix_size, self.matrix_size)
        self.key_matrix_table.setFixedSize(
            self.matrix_size * self.cell_size + self.cell_size + 50,
            self.matrix_size * self.cell_size + self.cell_size
        )
        self.key_matrix_table.setEditTriggers(qtw.QTableWidget.EditTrigger.NoEditTriggers)
        self.key_matrix_table.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.key_matrix_table.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        headers: list[str] = ['A', 'D', 'F', 'G', 'V', 'X']
        self.key_matrix_table.setHorizontalHeaderLabels(headers)
        self.key_matrix_table.setVerticalHeaderLabels(headers)
        self.key_matrix_table.horizontalHeader().setDefaultAlignment(qtc.Qt.AlignmentFlag.AlignCenter)
        self.key_matrix_table.verticalHeader().setDefaultAlignment(qtc.Qt.AlignmentFlag.AlignCenter)
        self.key_matrix_table.horizontalHeader().setFixedHeight(self.cell_size)
        self.key_matrix_table.verticalHeader().setFixedWidth(self.cell_size)
        self.key_matrix_table.horizontalHeader().setSectionResizeMode(qtw.QHeaderView.ResizeMode.Fixed)
        self.key_matrix_table.verticalHeader().setSectionResizeMode(qtw.QHeaderView.ResizeMode.Fixed)

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

        self.h_box_layout = qtw.QHBoxLayout()

        self.output_label = qtw.QLabel("output")
        self.main_layout.addWidget(self.output_label)
        self.output_text = qtw.QTextEdit()
        self.output_text.setReadOnly(True)
        self.h_box_layout.addWidget(self.output_text)
        self.main_layout.addLayout(self.h_box_layout)

        matrix = create_key_matrix(self.key1_text.text(), config["alphabet"])
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                item = qtw.QTableWidgetItem(matrix[i][j])
                item.setTextAlignment(qtc.Qt.AlignmentFlag.AlignCenter)
                self.key_matrix_table.setItem(i, j, item)

        self.key_matrix_v_box_layout = qtw.QVBoxLayout()

        generate_button = qtw.QPushButton("generate")
        generate_button.clicked.connect(self.random_key_matrix)

        self.key_matrix_v_box_layout.addWidget(self.key_matrix_table)
        self.key_matrix_v_box_layout.addWidget(generate_button)
        self.key_matrix_v_box_layout.addStretch()

        self.h_box_layout.addLayout(self.key_matrix_v_box_layout)

        button_layout = qtw.QHBoxLayout()

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
            self.input_text.toPlainText(),
            self.key1_text.text(),
            self.key2_text.text(),
            config["alphabet"]
        )
        self.output_text.setText(encrypted_text.upper())

    def decrypt(self):
        self.update_key_matrix()
        decrypted_text = decrypt(
            self.input_text.toPlainText(),
            self.key1_text.text(),
            self.key2_text.text(),
            config["alphabet"]
        )
        self.output_text.setText(decrypted_text.upper())

    def update_key_matrix(self):
        matrix = create_key_matrix(self.key1_text.text(), config["alphabet"])
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                item = qtw.QTableWidgetItem(matrix[i][j])
                item.setTextAlignment(qtc.Qt.AlignmentFlag.AlignCenter)
                self.key_matrix_table.setItem(i, j, item)

    def random_key_matrix(self):
        self.key1_text.setText(random_alphabet(self.matrix_size * self.matrix_size))
        self.update_key_matrix()

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
