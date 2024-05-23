from abc import abstractmethod
from os import remove

from chafa import chafa
from chafa.loader import Loader
from httpx import AsyncClient
from rich.text import Text
from textual.app import RenderResult
from textual.widget import Widget
from rich_pixels import Pixels
from PIL import Image
from io import BytesIO
from tempfile import NamedTemporaryFile


class ImageWidget(Widget):
    def __init__(self, width: int, height: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.width = width
        self.styles.width = width
        self.styles.max_width = width
        self.styles.min_width = width

        self.height = height
        _h = int(height / 2)
        self.styles.height = _h
        self.styles.max_height = _h
        self.styles.min_height = _h

        self.render_result: RenderResult = ""

    @abstractmethod
    def update_from_url(self, url: str):
        pass

    @abstractmethod
    def render(self):
        return self.render_result


class ChafaSymbolsImage(ImageWidget):
    # https://pypi.org/project/chafa.py/
    # https://hpjansson.org/chafa/
    # https://imagemagick.org/script/download.php


    # TODO: Support different loaders
    # https://chafapy.mage.black/usage/examples.html
    # TODO: Support all PixelModes

    async def update_from_url(self, url: str):
        async with AsyncClient(verify=False) as client:
            response = await client.get(url)
            with NamedTemporaryFile(mode="wb", prefix="gucken-", delete=False) as tf:
                tf.write(response.content)
                tf.close()

                config = chafa.CanvasConfig()

                config.width = self.width
                config.height = self.height

                image = Loader(tf.name)

                config.calc_canvas_geometry(
                    self.width,
                    self.height,
                    0.5
                )

                canvas = chafa.Canvas(config)

                canvas.draw_all_pixels(
                    image.pixel_type,
                    image.get_pixels(),
                    image.width,
                    image.height,
                    image.rowstride
                )

                self.render_result = Text.from_ansi(canvas.print().decode(), no_wrap=True)
                try:
                    remove(tf.name)
                except FileNotFoundError:
                    pass
                self.refresh()


class RichPixelsImage(ImageWidget):
    # https://pypi.org/project/rich-pixels/

    async def update_from_url(self, url: str):
        async with AsyncClient(verify=False) as client:
            response = await client.get(url)
            img = Image.open(BytesIO(response.content))
            img = img.resize((self.width, self.height))
            self.render_result = Pixels.from_image(img)
            self.refresh()

"""
yield ChafaSymbolsImage(25, 50)
yield RichPixelsImage(25, 50)

img = self.query_one(RichPixelsImage)
await img.update_from_url(series_search_result.cover)

img = self.query_one(ChafaSymbolsImage)
await img.update_from_url(series_search_result.cover)
"""
