"""Converts 4chan HTML comments to Rich Text objects."""

import html, re
from html.parser import HTMLParser
from rich.text import Text

# 4chan's greentext color
GREEN = "#789922"
QUOTE_RED = "#dd0000"


class _Node:
    __slots__ = ("text", "style", "is_quote", "ref")
    def __init__(self, text, style="", is_quote=False, ref=None):
        self.text = text
        self.style = style
        self.is_quote = is_quote
        self.ref = ref


class _Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.nodes = []
        self._stack = []
        self._in_quote = False
        self._ref = None

    def _cur_style(self):
        return " ".join(self._stack) if self._stack else ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        tag = tag.lower()

        if tag == "br":
            self.nodes.append(_Node("\n"))
            return
        if tag == "wbr": return

        if tag == "span":
            cls = a.get("class", "")
            if "quote" in cls and "quotelink" not in cls:
                self._stack.append(f"bold {GREEN}")
            elif "deadlink" in cls:
                self._stack.append("dim strike")
            else:
                self._stack.append("")
        elif tag == "a":
            cls = a.get("class", "")
            href = a.get("href", "")
            if "quotelink" in cls:
                self._in_quote = True
                m = re.search(r"#p(\d+)", href)
                self._ref = int(m.group(1)) if m else None
                self._stack.append(f"bold {QUOTE_RED}")
            else:
                self._stack.append(f"underline {QUOTE_RED}")
        elif tag == "pre" and "prettyprint" in a.get("class", ""):
            self._stack.append("on #2d2d2d")
        elif tag in ("b", "strong"):
            self._stack.append("bold")
        elif tag in ("i", "em"):
            self._stack.append("italic")
        elif tag == "u":
            self._stack.append("underline")
        elif tag == "s":
            self._stack.append("strike")
        else:
            self._stack.append("")

    def handle_endtag(self, tag):
        if tag.lower() in ("br", "wbr"): return
        if tag.lower() == "a":
            self._in_quote = False
            self._ref = None
        if self._stack:
            self._stack.pop()

    def handle_data(self, data):
        s = self._cur_style()
        if self._in_quote:
            self.nodes.append(_Node(data, s, is_quote=True, ref=self._ref))
        else:
            self.nodes.append(_Node(data, s))

    def handle_entityref(self, name):
        self.handle_data(html.unescape(f"&{name};"))

    def handle_charref(self, name):
        self.handle_data(html.unescape(f"&#{name};"))


def parse_comment(raw):
    if not raw: return Text("")
    p = _Parser()
    p.feed(raw)
    out = Text()
    for n in p.nodes:
        out.append(n.text, style=n.style)
    return out


def strip_html(raw):
    if not raw: return ""
    s = raw.replace("<br>", "\n").replace("<br/>", "\n")
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s).strip()


def quote_refs(raw):
    return [int(m.group(1)) for m in re.finditer(r'href="#p(\d+)"[^>]*class="quotelink"', raw)]
