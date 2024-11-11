import PySide6.QtWidgets as qtw
import ciphers
import sys

class App(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("playfair")
        self.setGeometry(200, 200, 600, 400)
        self.central_widget = qtw.QWidget()
        self.setCentralWidget(self.central_widget)
        self.mainLayout = qtw.QVBoxLayout()
        self.central_widget.setLayout(self.mainLayout)

        self.current_cipher = None
        self.cipher_selection = qtw.QComboBox()
        self.cipher_selection.addItems(["playfair", "adfgvx", "adfgx"])
        self.cipher_selection.currentTextChanged.connect(self.change_cipher)
        self.mainLayout.addWidget(self.cipher_selection)

    def change_cipher(self, cipher_name: str):
        match cipher_name:
            case "playfair": self.current_cipher = ciphers.playfair
            case "adfgvx": self.current_cipher = ciphers.adfgvx
            case "adfgx": pass

        print(self.current_cipher)

    def handle_encrypt(self):
        selected_cipher = self.cipher_selection.currentText()
        if selected_cipher == "Playfair": pass
            # encrypted_text = playfair.encrypt(self.key_text.text(), "alphabet", self.input_text.toPlainText())
        elif selected_cipher == "Caesar":
            # Caesar cipher encryption logic
            pass
        # self.output_text.setText(encrypted_text)

    def handle_decrypt(self):
        selected_cipher = self.cipher_selection.currentText()
        if selected_cipher == "Playfair": pass
            # decrypted_text = playfair.decrypt(self.key_text.text(), "alphabet", self.input_text.toPlainText())
        elif selected_cipher == "Caesar":
            # Caesar cipher decryption logic
            pass
        # self.output_text.setText(decrypted_text)

def main():
    app = qtw.QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__": main()
