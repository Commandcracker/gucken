# pip install textual-imageview
from textual.binding import Binding
from textual.widgets import Header, Footer
from pathlib import Path
from PIL import Image
from textual.app import ComposeResult, App
from textual_imageview.viewer import ImageViewer


class ColorApp(App):
    TITLE = "vimg"

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", priority=True),
        # Movement
        Binding("w,up", "move(0, 1)", "Up", show=True, key_display="W/↑"),
        Binding("s,down", "move(0, -1)", "Down", show=True, key_display="S/↓"),
        Binding("a,left", "move(1, 0)", "Left", show=True, key_display="A/←"),
        Binding("d,right", "move(-1, 0)", "Right", show=True, key_display="D/→"),
        Binding("q,=", "zoom(-1)", "Zoom In", show=True, key_display="Q/+"),
        Binding("e,-", "zoom(1)", "Zoom Out", show=True, key_display="E/-"),
        # Faster movement
        Binding("W,shift+up", "move(0, 3)", "Fast Up", show=False),
        Binding("S,shift+down", "move(0, -3)", "Fast Dowm", show=False),
        Binding("A,shift+left", "move(3, 0)", "Fast Left", show=False),
        Binding("D,shift+right", "move(-3, 0)", "Fast Right", show=False),
        Binding("E,+", "zoom(-2)", "Fast Zoom In", show=False),
        Binding("Q,_", "zoom(2)", "Fast Zoom Out", show=False),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield self.image_viewer
        yield Footer()

    def __init__(self):
        super().__init__()
        self.image_viewer = ImageViewer(Image.open(Path("<img>")))

    def action_move(self, delta_x: int, delta_y: int):
        self.image_viewer.image.move(delta_x, delta_y)
        self.image_viewer.refresh()
        self.refresh()

    def action_zoom(self, delta: int):
        self.image_viewer.image.zoom(delta)
        self.image_viewer.refresh()
        self.refresh()


if __name__ == "__main__":
    app = ColorApp()
    app.run()
