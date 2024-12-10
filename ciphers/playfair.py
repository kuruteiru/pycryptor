from typing import Any
import text_formatter as tf
import PySide6.QtWidgets as qtw
import PySide6.QtCore as qtc
import unicodedata
import string
import sys

config: dict[str, Any] = {
    "alphabet": string.ascii_lowercase.replace('j', '')
}

def main() -> None: 
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
        case "-k" | "-keymatrix": print('keymatrix')
        case "-f" | "-format": print('format')
        case _: print("unknown argument")

def format_text(input_text: str) -> str:
    if len(input_text) <= 0: return input_text
    char_map: dict[str, str] = tf.get_nonrepeating_char_map()

    formatted_text: str = ''
    formatted_text = tf.normalize_text(input_text, char_map = char_map)
    formatted_text = tf.format_repeating_chars(formatted_text)
    formatted_text = tf.even_length(formatted_text)
    formatted_text = formatted_text.replace('j', 'i')

    return formatted_text

def create_key_matrix(key: str, alphabet: str) -> list[list[str]]:
    key = key.lower().replace('j', 'i')
    key_matrix: list[str] = [
        c for c in unicodedata.normalize('NFD', key) 
        if c.isalpha() and unicodedata.category(c) != 'Mn'
    ]
    key_matrix = sorted(set(key_matrix), key = lambda x: key_matrix.index(x))
    key_matrix += [x for x in alphabet if x not in key_matrix]
    return [key_matrix[i:i+5] for i in range(0, 25, 5)]

def get_coordinates(matrix: list[list[str]], char: str) -> tuple[int, int]:
    if char == 'j': char = 'i'
    for i, row in enumerate(matrix):
        if char in row: return (i, row.index(char))
    return (-1, -1)

def encrypt(input_text: str, key: str, alphabet: str) -> str:
    if len(input_text) <= 0: return input_text

    matrix: list[list[str]] = create_key_matrix(key, alphabet)
    formatted_text: str = format_text(input_text)
    encrypted_text: list[str] = []

    for i in range(0, len(formatted_text), 2):
        char_a: tuple[int, int] = get_coordinates(matrix, formatted_text[i])
        char_b: tuple[int, int] = get_coordinates(matrix, formatted_text[i+1])

        if char_a[0] == char_b[0]:
            encrypted_text.append(matrix[char_a[0]][(char_a[1] + 1) % 5] + matrix[char_b[0]][(char_b[1] + 1) % 5])
        elif char_a[1] == char_b[1]:
            encrypted_text.append(matrix[(char_a[0] + 1) % 5][char_a[1]] + matrix[(char_b[0] + 1) % 5][char_b[1]])
        else:
            encrypted_text.append(matrix[char_a[0]][char_b[1]] + matrix[char_b[0]][char_a[1]])

    return ''.join(encrypted_text)

def decrypt(input_text: str, key: str, alphabet: str) -> str:
    if len(input_text) <= 0: return input_text

    matrix: list[list[str]] = create_key_matrix(key, alphabet)
    formatted_text: str = tf.even_length(input_text.lower())
    decrypted_text: list[str] = []

    for i in range(0, len(formatted_text), 2):
        char_a: tuple[int, int] = get_coordinates(matrix, formatted_text[i])
        char_b: tuple[int, int] = get_coordinates(matrix, formatted_text[i+1])

        if char_a[0] == char_b[0]:
            decrypted_text.append(matrix[char_a[0]][(char_a[1] - 1) % 5] + matrix[char_b[0]][(char_b[1] - 1) % 5])
        elif char_a[1] == char_b[1]:
            decrypted_text.append(matrix[(char_a[0] - 1) % 5][char_a[1]] + matrix[(char_b[0] - 1) % 5][char_b[1]])
        else:
            decrypted_text.append(matrix[char_a[0]][char_b[1]] + matrix[char_b[0]][char_a[1]])

    decrypted_text = list(tf.revert_repeating_chars(''.join(decrypted_text)))
    decrypted_text = list(tf.replace_char_map_values(''.join(decrypted_text), tf.get_nonrepeating_char_map()))
    decrypted_text = list(tf.revert_even_length(''.join(decrypted_text)))

    return ''.join(decrypted_text)

class App(qtw.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("playfair")
        self.central_widget: qtw.QWidget = qtw.QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout: qtw.QVBoxLayout = qtw.QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.key_label: qtw.QLabel = qtw.QLabel("key")
        self.main_layout.addWidget(self.key_label)
        self.key_text: qtw.QLineEdit = qtw.QLineEdit()
        self.main_layout.addWidget(self.key_text)

        self.matrix_size: int = 5
        self.cell_size: int = 30

        self.key_matrix_table: qtw.QTableWidget = qtw.QTableWidget(self.matrix_size, self.matrix_size)
        self.key_matrix_table.setFixedSize(self.matrix_size * self.cell_size + 40, self.matrix_size * self.cell_size)
        self.key_matrix_table.setEditTriggers(qtw.QTableWidget.EditTrigger.NoEditTriggers)
        self.key_matrix_table.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.key_matrix_table.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.key_matrix_table.horizontalHeader().setVisible(False)
        self.key_matrix_table.verticalHeader().setVisible(False)

        for i in range(self.matrix_size):
            self.key_matrix_table.setColumnWidth(i, self.cell_size)
            self.key_matrix_table.setRowHeight(i, self.cell_size)

        self.input_label: qtw.QLabel = qtw.QLabel("input")
        self.main_layout.addWidget(self.input_label)
        self.input_text: qtw.QTextEdit = qtw.QTextEdit()
        self.main_layout.addWidget(self.input_text)

        self.formatted_input_label: qtw.QLabel = qtw.QLabel("formatted input")
        self.main_layout.addWidget(self.formatted_input_label)
        self.formatted_input_text: qtw.QTextEdit = qtw.QTextEdit()
        self.formatted_input_text.setReadOnly(True)
        self.main_layout.addWidget(self.formatted_input_text)

        v_box_layout: qtw.QHBoxLayout = qtw.QHBoxLayout()

        output_label: qtw.QLabel = qtw.QLabel("output")
        self.main_layout.addWidget(output_label)
        self.output_text: qtw.QTextEdit = qtw.QTextEdit()
        self.output_text.setReadOnly(True)
        v_box_layout.addWidget(self.output_text)
        v_box_layout.addWidget(self.key_matrix_table)
        self.main_layout.addLayout(v_box_layout)

        matrix: list[list[str]] = create_key_matrix(self.key_text.text(), config["alphabet"])
        
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                item: qtw.QTableWidgetItem = qtw.QTableWidgetItem(matrix[i][j])
                item.setTextAlignment(qtc.Qt.AlignmentFlag.AlignCenter)
                self.key_matrix_table.setItem(i, j, item)

        button_layout: qtw.QHBoxLayout = qtw.QHBoxLayout()

        encrypt_button: qtw.QPushButton = qtw.QPushButton("encrypt")
        encrypt_button.clicked.connect(self.encrypt)
        button_layout.addWidget(encrypt_button)

        decrypt_button: qtw.QPushButton = qtw.QPushButton("decrypt")
        decrypt_button.clicked.connect(self.decrypt)
        button_layout.addWidget(decrypt_button)

        self.main_layout.addLayout(button_layout)

    def encrypt(self) -> None:
        self.update_key_matrix()
        encrypted_text: str = encrypt(
            self.input_text.toPlainText(),
            self.key_text.text(), 
            config["alphabet"]
        )
        self.output_text.setText(encrypted_text.upper())

        formatted_input: str = format_text(self.input_text.toPlainText()).upper()
        formatted_input = tf.groups_of(formatted_input, 2)
        self.formatted_input_text.setText(formatted_input)

    def decrypt(self) -> None:
        self.update_key_matrix()
        decrypted_text: str = decrypt(
            self.input_text.toPlainText(),
            self.key_text.text(), 
            config["alphabet"]
        )
        self.output_text.setText(decrypted_text.upper())

        formatted_input: str = self.input_text.toPlainText().upper()
        formatted_input = tf.groups_of(formatted_input, 2)
        self.formatted_input_text.setText(formatted_input)

    def update_key_matrix(self) -> None:
        matrix: list[list[str]] = create_key_matrix(self.key_text.text(), config["alphabet"])
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                item = qtw.QTableWidgetItem(matrix[i][j])
                item.setTextAlignment(qtc.Qt.AlignmentFlag.AlignCenter)
                self.key_matrix_table.setItem(i, j, item)


    def clear_layout(self, layout: qtw.QLayout | None) -> None: 
        if layout is None: return
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            if item.layout():
                self.clear_layout(item.layout())
                item.layout().deleteLater()

if __name__ == "__main__": main()
