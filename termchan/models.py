from dataclasses import dataclass, field
import html
import re

from termchan.config import IMAGE_BASE


@dataclass(frozen=True, slots=True)
class Board:
    board: str
    title: str
    ws_board: bool = False
    meta_description: str = ""
    pages: int = 10
    per_page: int = 15

    @classmethod
    def from_json(cls, d: dict) -> "Board":
        return cls(
            board=d["board"], title=d["title"],
            ws_board=bool(d.get("ws_board", 0)),
            meta_description=d.get("meta_description", ""),
            pages=d.get("pages", 10), per_page=d.get("per_page", 15),
        )

    @property
    def slug(self) -> str:
        return f"/{self.board}/"


@dataclass(frozen=True, slots=True)
class Post:
    no: int = 0
    now: str = ""
    name: str = "Anonymous"
    com: str = ""
    sub: str = ""
    tim: int | None = None
    ext: str | None = None
    filename: str | None = None
    w: int = 0
    h: int = 0
    tn_w: int = 0
    tn_h: int = 0
    fsize: int = 0
    resto: int = 0
    trip: str = ""
    capcode: str = ""
    country: str = ""
    country_name: str = ""
    id: str = ""
    md5: str = ""

    @classmethod
    def from_json(cls, d: dict) -> "Post":
        return cls(
            no=d["no"], now=d.get("now", ""), 
            name=html.unescape(d.get("name", "Anonymous")),
            com=d.get("com", ""), 
            sub=html.unescape(d.get("sub", "")),
            tim=d.get("tim"), ext=d.get("ext"), filename=d.get("filename"),
            w=d.get("w", 0), h=d.get("h", 0),
            tn_w=d.get("tn_w", 0), tn_h=d.get("tn_h", 0),
            fsize=d.get("fsize", 0), resto=d.get("resto", 0),
            trip=d.get("trip", ""), capcode=d.get("capcode", ""),
            country=d.get("country", ""), country_name=d.get("country_name", ""),
            id=d.get("id", ""), md5=d.get("md5", ""),
        )

    @property
    def has_image(self) -> bool:
        return self.tim is not None and self.ext is not None

    def image_url(self, board: str) -> str | None:
        if not self.has_image: return None
        return f"{IMAGE_BASE}/{board}/{self.tim}{self.ext}"

    def thumb_url(self, board: str) -> str | None:
        if not self.has_image: return None
        return f"{IMAGE_BASE}/{board}/{self.tim}s.jpg"

    @property
    def file_info(self) -> str:
        if not self.has_image: return ""
        kb = self.fsize / 1024
        size = f"{kb/1024:.1f} MB" if kb >= 1024 else f"{kb:.0f} KB"
        return f"{self.filename}{self.ext} ({size}, {self.w}x{self.h})"


@dataclass(frozen=True, slots=True)
class CatalogThread:
    no: int = 0
    now: str = ""
    name: str = "Anonymous"
    com: str = ""
    sub: str = ""
    replies: int = 0
    images: int = 0
    tim: int | None = None
    ext: str | None = None
    filename: str | None = None
    semantic_url: str = ""
    sticky: bool = False
    closed: bool = False
    last_replies: list[Post] = field(default_factory=list)
    omitted_posts: int = 0
    omitted_images: int = 0

    @classmethod
    def from_json(cls, d: dict) -> "CatalogThread":
        last = [Post.from_json(r) for r in d.get("last_replies", [])]
        return cls(
            no=d["no"], now=d.get("now", ""), 
            name=html.unescape(d.get("name", "Anonymous")),
            com=d.get("com", ""), 
            sub=html.unescape(d.get("sub", "")),
            replies=d.get("replies", 0), images=d.get("images", 0),
            tim=d.get("tim"), ext=d.get("ext"), filename=d.get("filename"),
            semantic_url=d.get("semantic_url", ""),
            sticky=bool(d.get("sticky", 0)), closed=bool(d.get("closed", 0)),
            last_replies=last,
            omitted_posts=d.get("omitted_posts", 0),
            omitted_images=d.get("omitted_images", 0),
        )

    @property
    def has_image(self) -> bool:
        return self.tim is not None and self.ext is not None

    def thumb_url(self, board: str) -> str | None:
        if not self.has_image: return None
        return f"{IMAGE_BASE}/{board}/{self.tim}s.jpg"

    @property
    def title(self) -> str:
        if self.sub:
            return self.sub
        # reuse the html parser instead of rolling our own entity decoding
        from termchan.html_parser import strip_html
        text = strip_html(self.com)
        text = " ".join(text.split())
        return text[:80] + ("…" if len(text) > 80 else "")
