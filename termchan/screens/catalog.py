from textual import on, work
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Label, ListItem, ListView, Static

from termchan.html_parser import strip_html
from termchan.models import Board, CatalogThread


class ThreadItem(ListItem):
    def __init__(self, thread, board, **kw):
        super().__init__(**kw)
        self.thread = thread
        self.board = board

    def compose(self) -> ComposeResult:
        t = self.thread
        title = t.title or "[dim]No subject[/dim]"
        if t.sticky: title = f"📌 {title}"
        if t.closed: title = f"🔒 {title}"

        has_file = "📎" if t.has_image else "  "
        stats = f"R:[bold]{t.replies}[/bold] / I:[bold]{t.images}[/bold] {has_file}"

        # grab first ~120 chars of the post for preview
        preview = strip_html(t.com).replace("\n", " ")
        if len(preview) > 120: preview = preview[:120] + "…"

        yield Static(f"[bold yellow]{title}[/bold yellow]\n[dim]{preview}[/dim]\n[cyan]{stats}[/cyan]")


class CatalogScreen(Screen):
    BINDINGS = [
        ("escape", "back", "Back"),
        ("q", "back", "Back"),
        ("r", "reload", "Refresh"),
    ]

    def __init__(self, board):
        super().__init__()
        self.board = board

    def compose(self) -> ComposeResult:
        with Container():
            yield Static(
                f"[bold]/{self.board.board}/ — {self.board.title}[/bold]  "
                f"[dim]r=refresh  q=back  Enter=open[/dim]"
            )
            yield Label("Loading catalog…", id="loading")
            yield ListView(id="threads")

    async def on_mount(self):
        self._load_catalog()

    @work(thread=False)
    async def _load_catalog(self):
        from termchan.api import fetch_catalog

        lv = self.query_one("#threads", ListView)
        lbl = self.query_one("#loading", Label)

        try:
            threads = await fetch_catalog(self.board.board)
        except Exception as e:
            lbl.update(f"[red]Error: {e}[/red]")
            return

        lbl.display = False
        lv.clear()
        for t in threads:
            lv.append(ThreadItem(t, self.board))

    @on(ListView.Selected, "#threads")
    def _thread_picked(self, ev):
        if isinstance(ev.item, ThreadItem):
            from termchan.screens.thread_view import ThreadViewScreen
            self.app.push_screen(ThreadViewScreen(self.board, ev.item.thread.no))

    def action_back(self):
        self.app.pop_screen()

    def action_reload(self):
        lbl = self.query_one("#loading", Label)
        lbl.update("Refreshing…")
        lbl.display = True
        self._load_catalog()
