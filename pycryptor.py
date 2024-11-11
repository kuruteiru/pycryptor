import PySide6.QtWidgets as qtw
import PySide6.QtCore as qtc
import ciphers
import sys

config = {
    "alphabet": "abcdefghijklmnopqrstuvwxyz",
    "substitution_characters": ('x', 'q'),
    "replaced_characters": ('j', 'i')
}

class App(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("pycryptor")
        # self.setGeometry(200, 200, 600, 400)

        self.central_widget = qtw.QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = qtw.QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        self.gui_layout = qtw.QVBoxLayout()

        self.current_cipher = None
        self.cipher_selection = qtw.QComboBox()
        self.cipher_selection.currentTextChanged.connect(self.select_cipher)
        self.cipher_selection.addItems(["playfair", "adfgvx", "adfgx"])
        self.cipher_selection.setCurrentText("playfair")
        self.cipher_selection.setGeometry(int(self.width()/2), int(self.height()/2), int(self.width()/2), int(self.height()/2))
        self.main_layout.addWidget(self.cipher_selection)

        self.main_layout.addLayout(self.gui_layout)
        self.render_gui()

    def clear_layout(self, layout: qtw.QLayout | None): 
        if layout is None: return
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            if item.layout():
                self.clear_layout(item.layout())
                item.layout().deleteLater()

    def select_cipher(self, cipher_name: str):
        rerender = self.current_cipher is not None
        match cipher_name:
            case "playfair": self.current_cipher = ciphers.playfair
            case "adfgvx": self.current_cipher = ciphers.adfgvx
            case "adfgx": pass

        if rerender: self.render_gui()

    def encrypt(self):
        if self.current_cipher is None: return
        self.update_key_matrix()
        encrypted_text = self.current_cipher.encrypt(self.key_text.text(), config["alphabet"], self.input_text.toPlainText())
        self.output_text.setText(encrypted_text.upper())
        formatted_input = self.current_cipher.format_text(self.input_text.toPlainText()).upper()
        formatted_input = ''.join([
                c if i == 0 or i % 2 != 0
                else f' {c}'
                for i, c in enumerate(formatted_input)
        ])
        self.formatted_input_text.setText(formatted_input)

    def decrypt(self):
        if self.current_cipher is None: return
        self.update_key_matrix()
        decrypted_text = self.current_cipher.decrypt(self.key_text.text(), config["alphabet"], self.input_text.toPlainText())
        self.output_text.setText(decrypted_text.upper())
        formatted_input = self.current_cipher.format_text(self.input_text.toPlainText()).upper()
        self.formatted_input_text.setText(formatted_input)
        formatted_input = self.input_text.toPlainText().upper()
        formatted_input = ''.join([
                c if i == 0 or i % 2 != 0
                else f' {c}'
                for i, c in enumerate(formatted_input)
        ])
        self.formatted_input_text.setText(formatted_input)

    def update_key_matrix(self):
        if self.current_cipher is None: return
        matrix = self.current_cipher.create_key_matrix(self.key_text.text(), config["alphabet"])
        
        for i in range(5):
            for j in range(5):
                item = qtw.QTableWidgetItem(matrix[i][j])
                item.setTextAlignment(qtc.Qt.AlignmentFlag.AlignCenter)
                self.key_matrix_table.setItem(i, j, item)

    def render_gui(self):
        input_values = {}

        if hasattr(self, "key_text") and self.key_text.text(): 
            input_values["key"] = self.key_text.text()

        if hasattr(self, "input_text") and self.input_text.toPlainText(): 
            input_values["input"] = self.input_text.toPlainText()

        self.clear_layout(self.gui_layout)

        self.key_label = qtw.QLabel("key")
        self.gui_layout.addWidget(self.key_label)
        self.key_text = qtw.QLineEdit()
        if "key" in input_values: self.key_text.setText(input_values["key"])
        self.gui_layout.addWidget(self.key_text)

        self.key_matrix_table = qtw.QTableWidget(5, 5)
        self.key_matrix_table.setFixedSize(190, 150)
        self.key_matrix_table.setEditTriggers(qtw.QTableWidget.EditTrigger.NoEditTriggers)
        self.key_matrix_table.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.key_matrix_table.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.key_matrix_table.horizontalHeader().setVisible(False)
        self.key_matrix_table.verticalHeader().setVisible(False)

        for i in range(5):
            self.key_matrix_table.setColumnWidth(i, 30)
            self.key_matrix_table.setRowHeight(i, 30)

        self.input_label = qtw.QLabel("input")
        self.gui_layout.addWidget(self.input_label)
        self.input_text = qtw.QTextEdit()
        if "input" in input_values: self.input_text.setText(input_values["input"])
        self.gui_layout.addWidget(self.input_text)

        self.formatted_input_label = qtw.QLabel("formatted input")
        self.gui_layout.addWidget(self.formatted_input_label)
        self.formatted_input_text = qtw.QTextEdit()
        self.formatted_input_text.setReadOnly(True)
        self.gui_layout.addWidget(self.formatted_input_text)

        self.v_box_layout = qtw.QHBoxLayout()

        self.output_label = qtw.QLabel("output")
        self.gui_layout.addWidget(self.output_label)
        self.output_text = qtw.QTextEdit()
        self.output_text.setReadOnly(True)
        self.v_box_layout.addWidget(self.output_text)
        self.v_box_layout.addWidget(self.key_matrix_table)
        self.gui_layout.addLayout(self.v_box_layout)
        self.update_key_matrix() 

        self.button_layout = qtw.QHBoxLayout()
        
        self.encrypt_button = qtw.QPushButton("encrypt")
        self.encrypt_button.clicked.connect(self.encrypt)
        self.button_layout.addWidget(self.encrypt_button)
        
        self.decrypt_button = qtw.QPushButton("decrypt")
        self.decrypt_button.clicked.connect(self.decrypt)
        self.button_layout.addWidget(self.decrypt_button)
        
        self.gui_layout.addLayout(self.button_layout)

def main():
    app = qtw.QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__": main()
