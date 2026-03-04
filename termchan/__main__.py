"""Entry point for `python -m termchan`."""

# must happen before textual boots so it can probe for kitty/sixel
import textual_image.renderable  # noqa: F401

from termchan.app import TermchanApp


def main():
    TermchanApp().run()


if __name__ == "__main__":
    main()
