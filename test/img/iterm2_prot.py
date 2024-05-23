# https://iterm2.com/documentation-images.html
from base64 import b64encode


def print_img(
    fine_content: bytes,
    width: int = None,
    height: int = None,
    preserve_aspect_ratio: int = None,
    fine_name: str = None
):
    s = ["\033]1337;File=inline=1"]

    if width:
        s.append(f";width={width}")
    if height:
        s.append(f";height={height}")
    if preserve_aspect_ratio:
        s.append(f";preserveAspectRatio={preserve_aspect_ratio}")
    if fine_name:
        s.append(f";name={b64encode(fine_name.encode()).decode()}")

    s.append(f":{b64encode(fine_content).decode()}")
    s.append("\007")
    print("".join(s))


def main():
    file_path = "<img_path>"

    with open(file_path, "rb") as image_file:
        fine_content = image_file.read()

    print_img(fine_content, 50, 20)


if __name__ == "__main__":
    main()
