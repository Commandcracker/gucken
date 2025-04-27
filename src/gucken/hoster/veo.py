from base64 import b64decode
from re import compile as re_compile, escape as re_escape

from bs4 import BeautifulSoup

from ..utils import json_loads
from ..networking import AsyncClient
from .common import DirectLink, Hoster

REDIRECT_PATTERN = re_compile("https?://[^'\"<>]+")

# Credit
# https://github.com/wolfswolke/aniworld_scraper/blob/41bd0f23cbc02352481dd92e6d986d1fe30c76bf/src/logic/search_for_links.py#L23

def deb_func1(input_string):
    result = ''
    for char in input_string:
        char_code = ord(char)
        if 0x41 <= char_code <= 0x5a:
            char_code = (char_code - 0x41 + 0xd) % 0x1a + 0x41
        elif 0x61 <= char_code <= 0x7a:
            char_code = (char_code - 0x61 + 0xd) % 0x1a + 0x61
        result += chr(char_code)
    return result

PATTERNS = [
    re_compile(re_escape('@$')),
    re_compile(re_escape('^^')),
    re_compile(re_escape('~@')),
    re_compile(re_escape('%?')),
    re_compile(re_escape('*~')),
    re_compile(re_escape('!!')),
    re_compile(re_escape('#&'))
]

def regex_func(input_string):
    for pattern in PATTERNS:
        input_string = pattern.sub('_', input_string)
    return input_string

def deb_func3(input_string, shift):
    result = []
    for char in input_string:
        result.append(chr(ord(char) - shift))
    return ''.join(result)

def deb_func(input_var):
    math_output = deb_func1(input_var)
    regexed_string = regex_func(math_output)
    cleaned_string = regexed_string.replace('_', '')
    b64_string1 = b64decode(cleaned_string).decode('utf-8')
    decoded_string = deb_func3(b64_string1, 3)
    reversed_string = decoded_string[::-1]
    b64_string2 = b64decode(reversed_string).decode('utf-8')
    return json_loads(b64_string2)

def find_script_element(raw_html):
    soup = BeautifulSoup(raw_html, features="html.parser")
    script_object = soup.find_all("script")
    obfuscated_string = ""
    for script in script_object:
        script = str(script)
        if "KGMAaM=" in script:
            obfuscated_string = script
            break
    if obfuscated_string == "":
        return None
    obfuscated_string = obfuscated_string.split('MKGMa="')[1]
    obfuscated_string = obfuscated_string.split('"')[0]
    output = deb_func(obfuscated_string)
    return output["source"]


class VOEHoster(Hoster):
    async def get_direct_link(self) -> DirectLink:
        async with AsyncClient(verify=False) as client:
            redirect_response = await client.get(self.url)
            redirect_match = REDIRECT_PATTERN.search(redirect_response.text)
            redirect_link = redirect_match.group()
            response = await client.get(redirect_link)
            return DirectLink(find_script_element(response.text))
