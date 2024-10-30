import unicodedata

config = {
    "key": "keynzu",
    "alphabet": "abcdefghijklmnopqrstuvwxyz",
    "substitution_characters": ('x', 'q'),
    "replaced_characters": ('j', 'i')
}

def main():
    open_text = "Open / text $$ sample 12:45 j ěščřžýáíé"
    encrypted_text = encrypt(config["key"], config["alphabet"], open_text)
    decrypted_text = decrypt(config["key"], config["alphabet"], encrypted_text)

    print(f"open text:\t{open_text}")
    print(f"formatted text:\t{format_text(open_text)}")
    print(f"encrypted text:\t{encrypted_text}")
    print(f"decrypted text:\t{decrypted_text}")

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

def create_key_matrix(key: str, alphabet: str) ->  list[list[str]]:
    key = key.lower().replace('j', 'i')
    key = sorted(set(key), key = lambda x: key.index(x)) 
    key += ''.join([x for x in alphabet.replace('j', '') if x not in key])
    return [list(key[i:i + 5]) for i in range(0, 25, 5)]
 
def print_key_matrix(matrix: list[list[str]]) -> None:
    for i in range(0, 5): print(matrix[i])

def character_position(matrix: list[list[str]], character: str) -> tuple[int, int]:
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
        char_b = character_position(matrix, formatted_text[i+1])
        encrypted_pair = None

        if char_a[0] == char_b[0]:
            encrypted_pair = matrix[char_a[0]][(char_a[1] + 1) % 5] + matrix[char_b[0]][(char_b[1] + 1) % 5]
        elif char_a[1] == char_b[1]:
            encrypted_pair = matrix[(char_a[0] + 1) % 5][char_a[1]] + matrix[(char_b[0] + 1) % 5][char_b[1]]
        else:
            encrypted_pair = matrix[char_a[0]][char_b[1]] + matrix[char_b[0]][char_a[1]]

        encrypted_text.append(encrypted_pair)
    
    return ''.join(encrypted_text)

def decrypt(key: str, alphabet: str, encrypted_text: str) -> str:
    matrix = create_key_matrix(key, alphabet)
    decrypted_text = []
    
    for i in range(0, len(encrypted_text), 2):
        char_a = character_position(matrix, encrypted_text[i])
        char_b = character_position(matrix, encrypted_text[i+1])
        decrypted_pair = None

        if char_a[0] == char_b[0]:
            decrypted_pair = matrix[char_a[0]][(char_a[1] - 1) % 5] + matrix[char_b[0]][(char_b[1] - 1) % 5]
        elif char_a[1] == char_b[1]:
            decrypted_pair = matrix[(char_a[0] - 1) % 5][char_a[1]] + matrix[(char_b[0] - 1) % 5][char_b[1]]
        else: 
            decrypted_pair = matrix[char_a[0]][char_b[1]] + matrix[char_b[0]][char_a[1]]

        decrypted_text.append(decrypted_pair)
    
    return ''.join(decrypted_text)

if __name__ == '__main__': main()
