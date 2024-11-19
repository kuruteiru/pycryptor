import unicodedata
import sys

config = {
    "alphabet": "abcdefghijklmnopqrstuvwxyz0123456789",
}

def main():
    print("adfgvx")
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
        if c.isalnum() or c.isspace()
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
    key_matrix += [x for x in alphabet if x not in key_matrix]
    return [key_matrix[i:i+6] for i in range(0, 36, 6)]

def create_columnar_key(key: str) -> list[int]:
    key = format_text(key)
    positions = list(range(len(key)))
    pairs = sorted(zip(key, positions))
    sorted_positions = list(zip(*pairs))[1]
    return sorted_positions

def get_coordinates(key_matrix: list[list[str]], char: str) -> tuple[str, str]:
    coordinates = "ADFGVX"
    for i, row in enumerate(key_matrix):
        if char in row: return (coordinates[i], coordinates[row.index(char)])
    return ('', '')

def encrypt(key1: str, key2: str, input_text: str) -> str:
    matrix = create_key_matrix(key1)
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

def decrypt(key1: str, key2: str, encrypted_text: str) -> str:
    matrix = create_key_matrix(key1)
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
        row_idx = "ADFGVX".index(coordinates[i])
        col_idx = "ADFGVX".index(coordinates[i + 1])
        decrypted_text += matrix[row_idx][col_idx]
    
    return decrypted_text

if __name__ == "__main__": main()
