ALPHABET = "abcdefghijklmnopqrstuvwxyz"
SUBSTITUTION_CHARACTERS = ('X', 'Q')

def format_text(input: str) -> str: pass

def create_key_matrix(key: str, substitution_characters: tuple) ->  list[list[str]] | None:
    if len(key) < 5: return None

    return [['']*5]*5

def encrypt(input: str, key: str) -> str:
    ciphered_text = "ct"
    return ciphered_text

def decrypt(input: str, key: str) -> str: pass

if __name__ == '__main__':
    matrix = create_key_matrix("keykey", SUBSTITUTION_CHARACTERS)
    if not matrix: print("m is none")
    print(f"al len:{len(ALPHABET)}")
    print(f"matrix {matrix}")
    print(encrypt(1, True))
    print("test")