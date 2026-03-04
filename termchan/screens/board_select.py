from textual import on, work
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Input, ListItem, ListView, Static

from termchan.config import FAVORITE_BOARDS
from termchan.models import Board


class BoardItem(ListItem):
    def __init__(self, board, **kw):
        super().__init__(**kw)
        self.board = board

    def compose(self) -> ComposeResult:
        sfw = "🟢" if self.board.ws_board else "🔴"
        yield Static(f"{sfw}  [bold]/{self.board.board}/[/bold] — {self.board.title}")


class BoardSelectScreen(Screen):
    BINDINGS = [("escape", "quit", "Quit"), ("q", "quit", "Quit")]

    def __init__(self):
        super().__init__()
        self._boards = []

    def compose(self) -> ComposeResult:
        with Container():
            yield Static("[bold]Select a Board[/bold]  [dim]Type to filter, Enter to select[/dim]")
            yield Input(placeholder="Search boards...", id="search")
            yield ListView(id="board-list")

    async def on_mount(self):
        self._load_boards()

    @work(thread=False)
    async def _load_boards(self):
        from termchan.api import fetch_boards

        lv = self.query_one("#board-list", ListView)
        try:
            self._boards = await fetch_boards()
        except Exception as e:
            lv.mount(ListItem(Static(f"[red]Error: {e}[/red]")))
            return
        self._populate()

    def _populate(self, query=""):
        lv = self.query_one("#board-list", ListView)
        lv.clear()
        q = query.lower()

        def matches(b):
            return q in b.board.lower() or q in b.title.lower()

        favs = [b for b in self._boards if b.board in FAVORITE_BOARDS and (not q or matches(b))]
        rest = [b for b in self._boards if b.board not in FAVORITE_BOARDS and (not q or matches(b))]

        if favs:
            lv.append(ListItem(Static("[bold cyan]★ Favorites[/bold cyan]")))
            for b in favs: lv.append(BoardItem(b))

        if rest:
            lv.append(ListItem(Static("[bold cyan]═ All Boards[/bold cyan]")))
            for b in rest: lv.append(BoardItem(b))

    @on(Input.Changed, "#search")
    def _filter_changed(self, ev):
        self._populate(ev.value)

    @on(ListView.Selected, "#board-list")
    def _board_picked(self, ev):
        if isinstance(ev.item, BoardItem):
            from termchan.screens.catalog import CatalogScreen
            self.app.push_screen(CatalogScreen(ev.item.board))

    def action_quit(self):
        self.app.exit()
