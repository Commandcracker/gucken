# pip install libsixel-python

from libsixel import SIXEL_OPTFLAG_OUTPUT, SIXEL_OPTFLAG_HEIGHT
from libsixel.encoder import Encoder, SIXEL_OPTFLAG_WIDTH
from tempfile import NamedTemporaryFile
from os import remove


def to_sic(
    path: str,
    width: int = None,
    height: int = None
) -> str:
    rf = NamedTemporaryFile(prefix="img-", suffix=".six", delete=False)

    encoder = Encoder()
    if width:
        encoder.setopt(SIXEL_OPTFLAG_WIDTH, width)
    if height:
        encoder.setopt(SIXEL_OPTFLAG_HEIGHT, height)
    encoder.setopt(SIXEL_OPTFLAG_OUTPUT, rf.name)
    encoder.encode(path)

    with open(rf.name, "r") as f:
        sic = f.read()

    remove(rf.name)
    return sic


def main():
    file_path = "<img_path>"
    print(to_sic(file_path, 500, 500))


if __name__ == "__main__":
    main()
