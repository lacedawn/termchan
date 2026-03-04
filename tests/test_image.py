from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image as PILImage

from termchan.image import make_widget, open_data_external, _tempfiles


def _make_png():
    """10x10 red square as PNG bytes"""
    img = PILImage.new("RGB", (10, 10), "red")
    buf = BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


class TestMakeWidget:
    def test_valid_png(self):
        # should get an actual widget back, not None
        w = make_widget(_make_png())
        assert w is not None

    def test_garbage_data(self):
        assert make_widget(b"this is not an image file") is None

    def test_empty_bytes(self):
        assert make_widget(b"") is None


class TestOpenExternal:
    def test_writes_temp_file(self):
        before = len(_tempfiles)
        with patch("termchan.image._open_in_viewer"):
            open_data_external(b"fake image data", ".jpg")

        assert len(_tempfiles) == before + 1
        p = Path(_tempfiles[-1])
        assert p.exists()
        assert p.read_bytes() == b"fake image data"
        p.unlink()    # don't leave garbage

    def test_respects_extension(self):
        with patch("termchan.image._open_in_viewer"):
            open_data_external(b"x", ".png")
        assert _tempfiles[-1].endswith(".png")
        Path(_tempfiles[-1]).unlink(missing_ok=True)
