from pathlib import Path
from textual.app import ComposeResult
from textual.containers import Center, Middle
from textual.screen import Screen
from textual.widgets import Static

_FALLBACK_ART = r"""
  ,--.                                ,--.
,-'  '-. ,---. ,--.--.,--,--,--. ,---.|  ,---.  ,--,--.,--,--,
'-.  .-'| .-. :|  .--'|        || .--'|  .-.  |' ,-.  ||      \
  |  |  \   --.|  |   |  |  |  |\ `--.|  | |  |\ '-'  ||  ||  |
  `--'   `----'`--'   `--`--`--' `---'`--' `--' `--`--'`--''--'
""".strip()

# load art from repo root (two levels up from this file)
try:
    _art_path = Path(__file__).resolve().parent.parent.parent / "art.txt"
    _ART = _art_path.read_text().strip() or _FALLBACK_ART
except Exception:
    _ART = _FALLBACK_ART

CONTROLS = (
    "[bold]Controls[/bold]\n"
    "  Enter  Select / Open       q/Esc  Back\n"
    "  r      Refresh             i      Inline image\n"
    "  o      Open image\n"
    "\n[dim]Press Enter to continue[/dim]"
)


class SplashScreen(Screen):

    BINDINGS = [
        ("enter", "go", "Continue"),
        ("escape", "go", "Continue"),
        ("space", "go", "Continue"),
    ]

    def compose(self) -> ComposeResult:
        with Middle():
            with Center():
                yield Static(_ART)
            with Center():
                yield Static("[dim]terminal 4chan browser[/dim]")
            with Center():
                yield Static(CONTROLS)

    def action_go(self):
        from termchan.screens.board_select import BoardSelectScreen
        self.app.switch_screen(BoardSelectScreen())
