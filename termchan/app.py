from textual.app import App
from termchan.screens.splash import SplashScreen


class TermchanApp(App):
    TITLE = "termchan"
    COMMANDS = set()     # don't need the command palette

    def on_mount(self):
        self.dark = True
        self.push_screen(SplashScreen())

    async def on_unmount(self):
        # clean up the shared http client
        from termchan.api import close_client
        await close_client()
