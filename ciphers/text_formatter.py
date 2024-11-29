import unicodedata
import sys

def main() -> None: 
    if len(sys.argv) == 1: return
    match sys.argv[1]:
        case "-x" | "-x": print('x')
        case _: print("unknown argument")

def normalize_text(input_text: str, black_list: list[str] | None = None, char_map: dict[str, str] | None = None) -> str:
    if len(input_text) <= 0: return input_text
    if black_list is None: black_list = ['\n', '\t', '\r']

    normalized_text: list[str] = [
        c.lower() for c in input_text.strip()
        if c not in black_list and (c.isalnum() or c.isspace())
    ]

    normalized_text = [
        c for i, c in enumerate(normalized_text)
        if not c.isspace() or (i == 0 or not normalized_text[i-1].isspace())
    ]

    if char_map is not None:
        normalized_text = list(replace_char_map_keys(''.join(normalized_text), char_map))

    normalized_text = [
        c for c in unicodedata.normalize('NFD', ''.join(normalized_text))
        if unicodedata.category(c) != 'Mn'
    ]

    return ''.join(normalized_text)

def normalize_spaces(input_text: str) -> str:
    if len(input_text) <= 0: return input_text
    result: list[str] = []
    
    result = [
        c for i, c in enumerate(input_text)
        if not c.isspace() or (i == 0 or not input_text[i-1].isspace())
    ]

    for i in range(len(input_text)):
        if input_text[i].isspace():
            try: 
                space_code = ('x' + unicodedata.name(' ') + 'x').lower()
                result.append(space_code)
            except: pass
            continue

        result.append(input_text[i])

    return ''.join(result)

def get_char_map() -> dict[str, str]:
    char_map: dict[str, str] = {
        str(i): 'x' + unicodedata.name(str(i)).lower().replace("digit", '').replace(' ', '') + 'x' 
        for i in range(10)
    }
    char_map[' '] = 'x' + unicodedata.name(' ').lower() + 'x'
    return char_map

def get_nonrepeating_char_map() -> dict[str, str]:
    char_map: dict[str, str] = {
        str(i): 'x' + format_repeating_chars(
            unicodedata.name(str(i)).lower().replace("digit", '').replace(' ', '')
        ) + 'x' 
        for i in range(10)
    }
    char_map[' '] = 'x' + unicodedata.name(' ').lower() + 'x'
    return char_map

def get_deleting_char_map(chars: list[str] | None = None) -> dict[str, str]:
    if chars is not None:
        char_map: dict[str, str] = {c: '' for c in chars}
        return char_map

    char_map: dict[str, str] = {str(i): '' for i in range(10)}
    char_map[' '] = ''
    return char_map

def replace_char_map_keys(input_text: str, char_map: dict[str, str]) -> str:
    if len(input_text) <= 0: return input_text
    for key, value in char_map.items():
        input_text = input_text.replace(key, value)

    return input_text

def replace_char_map_values(input_text: str, char_map: dict[str, str] | None = None) -> str:
    if len(input_text) <= 0: return input_text
    if char_map is None: char_map = get_char_map()
    for key, value in char_map.items():
        input_text = input_text.replace(value, key)

    return input_text

def groups_of(input_text: str, length: int) -> str:
    if len(input_text) <= 0: return input_text
    return ''.join([
        c if i == 0 or i % length != 0
        else f' {c}'
        for i, c in enumerate(input_text)
    ])

def format_repeating_chars(input_text: str) -> str:
    if len(input_text) < 2: return input_text

    result: list[str] = []
    for i in range(len(input_text)):
        result.append(input_text[i])
        if i < len(input_text) - 1 and input_text[i] == input_text[i+1]:
            sub_char: str = 'x' if input_text[i] != 'x' else 'q'
            result.append(sub_char)

    return ''.join(result)

# todo: make better
def revert_repeating_chars(input_text: str, char_map: dict[str, str] | None = None) -> str:
    if len(input_text) < 2: return input_text

    result: list[str] = []
    for i in range(len(input_text)):
        # if char_map is not None: 
        #     if i < len(input_text) - 1 and input_text[i] == 'x' and input_text[i-1]  == input_text[i+1]:
        #         continue

        result.append(input_text[i])

    return ''.join(result).replace('xqx', 'xx')

def even_length(input_text: str) -> str:
    if len(input_text) <= 0: return input_text
    if len(input_text) % 2 != 0:
        sub_char: str = 'x' if input_text[-1] != 'x' else 'q'
        input_text = input_text + sub_char

    return input_text

def revert_even_length(input_text: str) -> str:
    if len(input_text) <= 0: return input_text
    if len(input_text) % 2 != 0: return input_text
     
    if input_text[len(input_text)-1] == 'x':
        return input_text[:len(input_text)-1]
        
    if input_text[len(input_text)-1] == 'q' and input_text[len(input_text)-2] == 'x':
        return input_text[:len(input_text)-1]

    return input_text

if __name__ == "__main__": main()
