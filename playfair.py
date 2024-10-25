ALPHABET = "abcdefghijklmnopqrstuvwxyz"
SUBSTITUTION_CHARACTERS = ('X', 'Q')

def format_text(input: str) -> str: 
    key = "keynzud"
    unique = key + ALPHABET
    print(f"unique: {unique}")
    unique = list(unique) 
    print(f"unique: {unique}")
    unique = ''.join(unique)
    print(f"unique: {unique}")

def create_key_matrix(key: str) ->  list[list[str]]:
    key = key.lower().replace('j', 'i')
    key = sorted(set(key), key = lambda x: key.index(x)) 
    key += ''.join([x for x in ALPHABET.replace('j', '') if x not in key])
    return [list(key[i:i + 5]) for i in range(0, 25, 5)]
 
def print_key_matrix(matrix: list[list[str]]):
    for i in range(0, 25, 5): print(matrix[i:i + 5])

def encrypt(input: str, key: str) -> str:
    ciphered_text = "ct"
    main()
    return ciphered_text

def decrypt(input: str, key: str) -> str: pass

def main():
    # format_text("input")
    matrix = create_key_matrix("keynzu")
    print(f"matrix {matrix}")
    print_key_matrix(matrix)

if __name__ == '__main__': main()
