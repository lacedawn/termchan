import logging
from textual import work
from textual.app import ComposeResult
from textual.containers import Container, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Label, Static
from rich.text import Text

from termchan.html_parser import parse_comment

log = logging.getLogger(__name__)


class PostWidget(Vertical, can_focus=True):

    DEFAULT_CSS = """
    PostWidget {
        width: 100%;
        margin: 0 0 1 0;
        padding: 1 2;
        border: solid $secondary;
        height: auto;
    }
    PostWidget:focus {
        border: solid $accent;
    }
    PostWidget .post-img {
        width: 80;
        height: 40;
        margin: 1 0;
    }
    """

    BINDINGS = [
        ("i", "show_inline", "Image"),
        ("o", "open_ext", "Open"),
    ]

    def __init__(self, post, board_name, is_op=False, **kw):
        super().__init__(**kw)
        self.post = post
        self.board_name = board_name
        self.is_op = is_op
        self._img_visible = False
        self._cached_img = None     # raw bytes, so we don't re-download

    def compose(self) -> ComposeResult:
        yield Static("", classes="post-text")

    def on_mount(self):
        self.query_one(".post-text", Static).update(self._format_post())

    def on_enter(self):
        self.focus(scroll_visible=False)

    def _format_post(self):
        p = self.post
        out = Text()

        out.append(f"No.{p.no}", style="bold cyan")
        out.append("  ")
        out.append(p.name, style="bold red" if p.capcode else "bold green")
        if p.trip: out.append(f" {p.trip}", style="green")
        if p.id: out.append(f" ID:{p.id}", style="bold yellow")
        if p.country_name: out.append(f" [{p.country_name}]", style="dim")
        if p.capcode: out.append(f" ## {p.capcode.capitalize()}", style="bold red")
        out.append(f"  {p.now}", style="dim")
        if self.is_op: out.append("  [OP]", style="bold magenta")
        out.append("\n")

        if p.sub:
            out.append(p.sub, style="bold red")
            out.append("\n")

        if p.has_image:
            out.append(f"📎 {p.file_info}", style="dim")
            out.append("  [i=view / o=open]", style="dim italic")
            out.append("\n")

        out.append("─" * 50, style="dim")
        out.append("\n")
        out.append_text(parse_comment(p.com))
        return out

    def action_show_inline(self):
        if self.post.has_image:
            self._toggle_image()
        else:
            self.app.notify("No image on this post", timeout=2)

    def action_open_ext(self):
        if self.post.has_image:
            self._save_and_open()
        else:
            self.app.notify("No image on this post", timeout=2)

    @work(thread=False)
    async def _toggle_image(self):
        # toggle off if already showing
        if self._img_visible:
            for w in self.query(".post-img"):
                w.remove()
            self._img_visible = False
            return

        from termchan.api import download
        from termchan.image import make_widget

        url = self.post.image_url(self.board_name)
        if not url: return

        self.app.notify("Loading image…", timeout=2)
        if self._cached_img is None:
            self._cached_img = await download(url)

        w = make_widget(self._cached_img)
        if w:
            w.add_class("post-img")
            await self.mount(w)
            self._img_visible = True
        else:
            self.app.notify("Image rendering not available", timeout=3)

    @work(thread=False)
    async def _save_and_open(self):
        from termchan.api import download
        from termchan.image import open_data_external

        url = self.post.image_url(self.board_name)
        if not url: return

        self.app.notify("Downloading…", timeout=2)
        data = await download(url)
        open_data_external(data, self.post.ext or ".jpg")


class ThreadViewScreen(Screen):
    BINDINGS = [
        ("escape", "back", "Back"),
        ("q", "back", "Back"),
        ("r", "reload", "Refresh"),
    ]

    def __init__(self, board, thread_no):
        super().__init__()
        self.board = board
        self.thread_no = thread_no
        self._post_widgets = []

    def compose(self) -> ComposeResult:
        with Container():
            yield Static(
                f"[bold]/{self.board.board}/ — No.{self.thread_no}[/bold]  "
                f"[dim]click post → i=image  o=open  r=refresh  q=back[/dim]"
            )
            yield Label("Loading…", id="loading")
            yield VerticalScroll(id="posts")

    async def on_mount(self):
        self._load_thread()

    @work(thread=False)
    async def _load_thread(self):
        from termchan.api import fetch_thread, ThreadNotFound

        scroll = self.query_one("#posts", VerticalScroll)
        lbl = self.query_one("#loading", Label)

        try:
            posts = await fetch_thread(self.board.board, self.thread_no)
        except ThreadNotFound:
            lbl.update("[red]Thread not found — pruned or archived.[/red]")
            return
        except Exception as e:
            lbl.update(f"[red]Error: {e}[/red]")
            return

        lbl.display = False
        self._post_widgets = []

        for i, post in enumerate(posts):
            pw = PostWidget(post, self.board.board, is_op=(i == 0), id=f"p-{post.no}")
            self._post_widgets.append(pw)
            await scroll.mount(pw)

        if self._post_widgets:
            self._post_widgets[0].focus()

    def action_back(self):
        self.app.pop_screen()

    def action_reload(self):
        lbl = self.query_one("#loading", Label)
        lbl.update("Refreshing…")
        lbl.display = True
        self.query_one("#posts", VerticalScroll).remove_children()
        self._post_widgets = []
        self._load_thread()
