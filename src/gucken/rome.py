from re import compile as re_compile

ROMAN_PATTERN = re_compile(r"\b[IVXLCDM]+\b")
ROMAN_NUMERALS = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def roman_to_int(roman: str) -> int:
    result = 0
    prev_value = 0
    for char in reversed(roman):
        value = ROMAN_NUMERALS[char]
        if value < prev_value:
            result -= value
        else:
            result += value
        prev_value = value
    return result


def replace_roman_numerals(text: str) -> str:
    def repl(match):
        return str(roman_to_int(match.group(0)))

    return ROMAN_PATTERN.sub(repl, text)
