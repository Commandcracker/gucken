# Based on https://github.com/beautifier/js-beautify/blob/main/python/jsbeautifier/unpackers/packer.py
from re import compile, DOTALL, ASCII

class UnpackingError(Exception):
    pass

DETECT_PATTERN = compile(
    r"eval[ ]*\([ ]*function[ ]*\([ ]*p[ ]*,[ ]*a[ ]*,[ ]*c[ ]*,[ ]*k[ ]*,[ ]*e[ ]*,[ ]*"
)
FILTERARGS_PATTERNS = [
    compile(r"}\('(.*)', *(\d+|\[\]), *(\d+), *'(.*)'\.split\('\|'\), *(\d+), *(.*)\)\)", DOTALL),
    compile(r"}\('(.*)', *(\d+|\[\]), *(\d+), *'(.*)'\.split\('\|'\)", DOTALL),
]
WORD_PATTERN = compile(r"\b\w+\b", ASCII)
REPLACESTRINGS_PATTERN = compile(r'var *(_\w+)\=\["(.*?)"\];', DOTALL)

def detect(source: str) -> tuple[bool, str, str]:
    """Detects whether `source` is P.A.C.K.E.R. coded."""
    beginstr = ""
    endstr = ""
    begin_offset = -1
    mystr = DETECT_PATTERN.search(source)
    if mystr:
        begin_offset = mystr.start()
        beginstr = source[:begin_offset]
    if begin_offset != -1:
        source_end = source[begin_offset:]
        if source_end.split("')))", 1)[0] == source_end:
            try:
                endstr = source_end.split("}))", 1)[1]
            except IndexError:
                endstr = ""
        else:
            endstr = source_end.split("')))", 1)[1]
    return mystr is not None, beginstr, endstr

def unpack(source: str, beginstr: str = "", endstr: str = "") -> str:
    """Unpacks P.A.C.K.E.R. packed js code."""
    payload, symtab, radix, count = _filterargs(source)

    if count != len(symtab):
        raise UnpackingError("Malformed p.a.c.k.e.r. symtab.")

    try:
        unbase = Unbaser(radix)
    except TypeError:
        raise UnpackingError("Unknown p.a.c.k.e.r. encoding.")

    def lookup(match) -> str:
        """Look up symbols in the synthetic symtab."""
        word = match.group(0)
        return symtab[unbase(word)] or word

    payload = payload.replace("\\\\", "\\").replace("\\'", "'")
    source = WORD_PATTERN.sub(lookup, payload)
    return _replacestrings(source, beginstr, endstr)

def _filterargs(source: str) -> tuple[str, list[str], int, int]:
    """Juice from a source file the four args needed by decoder."""
    for juicer in FILTERARGS_PATTERNS:
        args = juicer.search(source)
        if args:
            a = args.groups()
            if a[1] == "[]":
                a = list(a)
                a[1] = 62
                a = tuple(a)
            try:
                return a[0], a[3].split("|"), int(a[1]), int(a[2])
            except ValueError:
                raise UnpackingError("Corrupted p.a.c.k.e.r. data.")
    raise UnpackingError("Could not make sense of p.a.c.k.e.r data (unexpected code structure)")

def _replacestrings(source: str, beginstr: str = "", endstr: str = "") -> str:
    """Strip string lookup table (list) and replace values in source."""
    match = REPLACESTRINGS_PATTERN.search(source)
    if match:
        varname, strings = match.groups()
        startpoint = len(match.group(0))
        lookup = strings.split('","')
        variable = "%s[%%d]" % varname
        for index, value in enumerate(lookup):
            source = source.replace(variable % index, '"%s"' % value)
        return source[startpoint:]
    return beginstr + source + endstr

class Unbaser:
    """Functor for a given base. Will efficiently convert strings to natural numbers."""
    ALPHABET = {
        62: "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        95: (
            " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
        ),
    }

    def __init__(self, base: int):
        self.base = base

        if 36 < base < 62:
            if base not in self.ALPHABET:
                self.ALPHABET[base] = self.ALPHABET[62][:base]

        if 2 <= base <= 36:
            self.unbase = lambda string: int(string, base)
        else:
            try:
                self.dictionary = {cipher: index for index, cipher in enumerate(self.ALPHABET[base])}
            except KeyError:
                raise TypeError("Unsupported base encoding.")

            self.unbase = self._dictunbaser

    def __call__(self, string: str) -> int:
        return self.unbase(string)

    def _dictunbaser(self, string: str) -> int:
        """Decodes a value to an integer."""
        ret = 0
        for index, cipher in enumerate(string[::-1]):
            ret += (self.base**index) * self.dictionary[cipher]
        return ret
