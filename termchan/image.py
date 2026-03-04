import atexit
import logging
import platform
import shutil
import subprocess
import tempfile
from io import BytesIO
from pathlib import Path

from PIL import Image as PILImage

log = logging.getLogger(__name__)

_tempfiles: list[str] = []   # tracked so we can nuke them on exit

def _cleanup_temps():
    for f in _tempfiles:
        try: Path(f).unlink(missing_ok=True)
        except OSError: pass

atexit.register(_cleanup_temps)


def _open_in_viewer(path: str) -> None:
    """Try to open a file with the system's default viewer."""
    system = platform.system()
    if system == "Darwin":
        cmd = ["open", str(path)]
    elif system == "Windows":
        cmd = ["start", "", str(path)]
    else:
        # linux / bsd / etc - need xdg-open
        if not shutil.which("xdg-open"):
            log.error("no xdg-open found, can't open images externally")
            return
        cmd = ["xdg-open", str(path)]

    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        log.error("viewer launch failed: %s", e)


def open_data_external(data: bytes, ext: str = ".jpg") -> None:
    if not ext.startswith("."):
        ext = "." + ext
    tmp = tempfile.NamedTemporaryFile(suffix=ext, prefix="termchan_", delete=False)
    tmp.write(data)
    tmp.close()
    _tempfiles.append(tmp.name)
    _open_in_viewer(tmp.name)


def make_widget(image_bytes: bytes, max_width: int = 600):
    try:
        from textual_image.widget import Image
    except ImportError:
        log.warning("textual-image not installed, no inline images")
        return None

    try:
        img = PILImage.open(BytesIO(image_bytes))
        # some pngs are palette mode which textual-image chokes on
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")
        # scale down so it doesn't eat the whole terminal
        if img.width > max_width:
            ratio = max_width / img.width
            img = img.resize((max_width, int(img.height * ratio)), PILImage.LANCZOS)
        return Image(img)
    except Exception as e:
        log.error("couldn't create image widget: %s", e)
        return None
