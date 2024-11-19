import unicodedata
import sys

config = {
    "alphabet": "abcdefghijklmnopqrstuvwxyz",
}

def main():
    print("affine")
    if len(sys.argv) == 1: return
    match sys.argv[1]:
        case "-e" | "-encrypt": print('encrypt')
        case "-d" | "-decrypt": print('decrypt')
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
    
    return formatted_text

def gcd(a: int, b: int) -> int:
    while b != 0:
        a, b = b, a % b
    return a

def mod_inverse(a: int, m: int) -> int:
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    raise ValueError(f"No modular inverse for a={a}, m={m}")

def encrypt(a: int, b: int, input_text: str) -> str:
    if gcd(a, len(config["alphabet"])) != 1:
        raise ValueError(f"a={a} is not coprime with the alphabet length {len(config['alphabet'])}.")
    
    formatted_text = format_text(input_text)
    m = len(config["alphabet"])
    encrypted_text = ""

    for char in formatted_text:
        if char in config["alphabet"]:
            x = config["alphabet"].index(char)
            encrypted_char = config["alphabet"][(a * x + b) % m]
            encrypted_text += encrypted_char
        else:
            encrypted_text += char  # Preserve spaces and unsupported characters
    
    return encrypted_text

def decrypt(a: int, b: int, encrypted_text: str) -> str:
    if gcd(a, len(config["alphabet"])) != 1:
        raise ValueError(f"a={a} is not coprime with the alphabet length {len(config['alphabet'])}.")
    
    m = len(config["alphabet"])
    a_inv = mod_inverse(a, m)
    decrypted_text = ""

    for char in encrypted_text:
        if char in config["alphabet"]:
            y = config["alphabet"].index(char)
            decrypted_char = config["alphabet"][(a_inv * (y - b)) % m]
            decrypted_text += decrypted_char
        else:
            decrypted_text += char 
    
    return decrypted_text

if __name__ == "__main__": main()
