# https://github.com/Textualize/rich/discussions/384#discussioncomment-9286378

import io
import sys
from base64 import b64encode
from pathlib import Path

from PIL import Image
from rich.segment import Segment
from textual.widget import Widget
from textual.app import App, ComposeResult
from textual.geometry import Size, NULL_SIZE
from textual.containers import Center, Middle
from rich.console import (
    Console,
    ConsoleOptions,
    ConsoleRenderable,
    RenderResult,
    RichCast,
)
from rich.style import Style


PLACEHOLDER = 0x10EEEE

# fmt: off
NUMBER_TO_DIACRITIC = [
     0x00305, 0x0030d, 0x0030e, 0x00310, 0x00312, 0x0033d, 0x0033e, 0x0033f, 0x00346, 0x0034a, 0x0034b, 0x0034c, 0x00350, 0x00351, 0x00352, 0x00357,
     0x0035b, 0x00363, 0x00364, 0x00365, 0x00366, 0x00367, 0x00368, 0x00369, 0x0036a, 0x0036b, 0x0036c, 0x0036d, 0x0036e, 0x0036f, 0x00483, 0x00484,
     0x00485, 0x00486, 0x00487, 0x00592, 0x00593, 0x00594, 0x00595, 0x00597, 0x00598, 0x00599, 0x0059c, 0x0059d, 0x0059e, 0x0059f, 0x005a0, 0x005a1,
     0x005a8, 0x005a9, 0x005ab, 0x005ac, 0x005af, 0x005c4, 0x00610, 0x00611, 0x00612, 0x00613, 0x00614, 0x00615, 0x00616, 0x00617, 0x00657, 0x00658,
     0x00659, 0x0065a, 0x0065b, 0x0065d, 0x0065e, 0x006d6, 0x006d7, 0x006d8, 0x006d9, 0x006da, 0x006db, 0x006dc, 0x006df, 0x006e0, 0x006e1, 0x006e2,
     0x006e4, 0x006e7, 0x006e8, 0x006eb, 0x006ec, 0x00730, 0x00732, 0x00733, 0x00735, 0x00736, 0x0073a, 0x0073d, 0x0073f, 0x00740, 0x00741, 0x00743,
     0x00745, 0x00747, 0x00749, 0x0074a, 0x007eb, 0x007ec, 0x007ed, 0x007ee, 0x007ef, 0x007f0, 0x007f1, 0x007f3, 0x00816, 0x00817, 0x00818, 0x00819,
     0x0081b, 0x0081c, 0x0081d, 0x0081e, 0x0081f, 0x00820, 0x00821, 0x00822, 0x00823, 0x00825, 0x00826, 0x00827, 0x00829, 0x0082a, 0x0082b, 0x0082c,
     0x0082d, 0x00951, 0x00953, 0x00954, 0x00f82, 0x00f83, 0x00f86, 0x00f87, 0x0135d, 0x0135e, 0x0135f, 0x017dd, 0x0193a, 0x01a17, 0x01a75, 0x01a76,
     0x01a77, 0x01a78, 0x01a79, 0x01a7a, 0x01a7b, 0x01a7c, 0x01b6b, 0x01b6d, 0x01b6e, 0x01b6f, 0x01b70, 0x01b71, 0x01b72, 0x01b73, 0x01cd0, 0x01cd1,
     0x01cd2, 0x01cda, 0x01cdb, 0x01ce0, 0x01dc0, 0x01dc1, 0x01dc3, 0x01dc4, 0x01dc5, 0x01dc6, 0x01dc7, 0x01dc8, 0x01dc9, 0x01dcb, 0x01dcc, 0x01dd1,
     0x01dd2, 0x01dd3, 0x01dd4, 0x01dd5, 0x01dd6, 0x01dd7, 0x01dd8, 0x01dd9, 0x01dda, 0x01ddb, 0x01ddc, 0x01ddd, 0x01dde, 0x01ddf, 0x01de0, 0x01de1,
     0x01de2, 0x01de3, 0x01de4, 0x01de5, 0x01de6, 0x01dfe, 0x020d0, 0x020d1, 0x020d4, 0x020d5, 0x020d6, 0x020d7, 0x020db, 0x020dc, 0x020e1, 0x020e7,
     0x020e9, 0x020f0, 0x02cef, 0x02cf0, 0x02cf1, 0x02de0, 0x02de1, 0x02de2, 0x02de3, 0x02de4, 0x02de5, 0x02de6, 0x02de7, 0x02de8, 0x02de9, 0x02dea,
     0x02deb, 0x02dec, 0x02ded, 0x02dee, 0x02def, 0x02df0, 0x02df1, 0x02df2, 0x02df3, 0x02df4, 0x02df5, 0x02df6, 0x02df7, 0x02df8, 0x02df9, 0x02dfa,
     0x02dfb, 0x02dfc, 0x02dfd, 0x02dfe, 0x02dff, 0x0a66f, 0x0a67c, 0x0a67d, 0x0a6f0, 0x0a6f1, 0x0a8e0, 0x0a8e1, 0x0a8e2, 0x0a8e3, 0x0a8e4, 0x0a8e5,
     0x0a8e6, 0x0a8e7, 0x0a8e8, 0x0a8e9, 0x0a8ea, 0x0a8eb, 0x0a8ec, 0x0a8ed, 0x0a8ee, 0x0a8ef, 0x0a8f0, 0x0a8f1, 0x0aab0, 0x0aab2, 0x0aab3, 0x0aab7,
     0x0aab8, 0x0aabe, 0x0aabf, 0x0aac1, 0x0fe20, 0x0fe21, 0x0fe22, 0x0fe23, 0x0fe24, 0x0fe25, 0x0fe26, 0x10a0f, 0x10a38, 0x1d185, 0x1d186, 0x1d187,
     0x1d188, 0x1d189, 0x1d1aa, 0x1d1ab, 0x1d1ac, 0x1d1ad, 0x1d242, 0x1d243, 0x1d244
]
# fmt: on


class KittyImage(Widget):
    _next_image_id = 1

    class _Renderable:
        def __init__(self, image_id: int, size: Size) -> None:
            self._image_id = image_id
            self._size = size

        def __rich_console__(
            self, _console: Console, _options: ConsoleOptions
        ) -> RenderResult:
            style = Style(color=f"rgb({(self._image_id >> 16) & 255}, {(self._image_id >> 8) & 255}, {self._image_id & 255})")
            id_char = NUMBER_TO_DIACRITIC[(self._image_id >> 24) & 255]
            for r in range(self._size.height):
                line = ""
                for c in range(self._size.width):
                    line += f"{chr(PLACEHOLDER)}{chr(NUMBER_TO_DIACRITIC[r])}{chr(NUMBER_TO_DIACRITIC[c])}{chr(id_char)}"
                line += "\n"
                yield Segment(line, style=style)

    def __init__(
        self,
        image: Image,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        image_buffer = io.BytesIO()
        image.save(image_buffer, format="png")
        self._image_data = image_buffer.getvalue()

        self._image_id = KittyImage._next_image_id
        KittyImage._next_image_id += 1

        self._placement_size = NULL_SIZE

        self._send_image_to_terminal()

    def _send_image_to_terminal(self) -> None:
        data = b64encode(self._image_data)
        while data:
            chunk, data = data[:4096], data[4096:]

            ans = [
                f"\033_Gi={self._image_id},m={1 if data else 0},f=100,q=2".encode(
                    "ascii"
                )
            ]
            if chunk:
                ans.append(b";")
                ans.append(chunk)
            ans.append(b"\033\\")

            # Dangerous. Could interfer with the writer thread. But we can't use textual's functions
            # to write to the terminal.
            # It buffers output. There's no way around that (Driver.flush() is a no-op).
            # This buffering re-chunks the data which leads to a failed transmission.
            sys.__stdout__.buffer.write(b"".join(ans))
            sys.__stdout__.buffer.flush()

    def _create_virtual_placement(self, size: Size) -> None:
        # Same issue as above, even though the size of the data probably would still work with the
        # buffering. But we have this hack in place anyway, so it shouldn't matter anymore.
        sys.__stdout__.buffer.write(
            f"\033_Ga=p,U=1,i={self._image_id},c={size.width},r={size.height},q=2\033\\".encode(
                "ascii"
            )
        )
        sys.__stdout__.flush()

    def render(self) -> ConsoleRenderable | RichCast:
        if self._placement_size != self.content_size:
            self._create_virtual_placement(self.content_size)
            self._placement_size = self.content_size
        return KittyImage._Renderable(self._image_id, self.content_size)


class ImageApp(App[None]):
    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                yield KittyImage(Image.open(Path("<img_path>")))

    def on_mount(self) -> None:
        self.query_one(KittyImage).styles.width = 20
        self.query_one(KittyImage).styles.height = 15


if __name__ == "__main__":
    ImageApp().run()
