import unicodedata
import sys

config = {
    "alphabet": "abcdefghijklmnopqrstuvwxyz",
    "substitution_characters": ('x', 'q'),
    "replaced_characters": ('j', 'i')
}

def main(): 
    if len(sys.argv) == 1: return
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

if __name__ == "__main__": main()
