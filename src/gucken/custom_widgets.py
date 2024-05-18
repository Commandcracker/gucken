from textual import events
from textual.message import Message
from textual.widgets import DataTable


class SortableTable(DataTable):
    """
    TODO: Add mouse support.
    TODO: Improve UX
    """

    class SortChanged(Message):
        def __init__(
            self, sortable_table: "SortableTable", previous: int, now: int
        ) -> None:
            self.sortable_table = sortable_table
            self.previous = previous
            self.now = now
            super().__init__()

        @property
        def control(self) -> "SortableTable":
            return self.sortable_table

    def __init__(self, *args, **kwargs):
        self.move_mode = False
        super().__init__(cursor_type="row", *args, **kwargs)

    async def _on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            self.move_mode = not self.move_mode

    def _move_item(self, offset: int) -> None:
        previous = self.cursor_row
        now = previous + offset

        i1 = self._row_locations.get_key(previous)
        i2 = self._row_locations.get_key(now)
        self._row_locations[i1] = now
        self._row_locations[i2] = previous
        self.cursor_coordinate = (
            self.cursor_coordinate.down() if offset > 0 else self.cursor_coordinate.up()
        )
        self._update_count += 1
        self.refresh()
        self.post_message(self.SortChanged(self, previous, now))

    def action_cursor_up(self) -> None:
        if not self.move_mode:
            super().action_cursor_up()
            return
        if self.cursor_row - 1 >= 0:
            self._move_item(-1)

    def action_cursor_down(self) -> None:
        if not self.move_mode:
            super().action_cursor_down()
            return
        if self.cursor_row + 1 < self.row_count:
            self._move_item(1)
