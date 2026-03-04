from rich.text import Text
from termchan.html_parser import parse_comment, strip_html, quote_refs


class TestParse:
    def test_empty(self):
        assert str(parse_comment("")) == ""

    def test_plain(self):
        assert str(parse_comment("hello")) == "hello"

    def test_br(self):
        assert str(parse_comment("a<br>b")) == "a\nb"

    def test_greentext(self):
        assert ">implying" in str(parse_comment('<span class="quote">&gt;implying</span>'))

    def test_quotelink(self):
        assert ">>123" in str(parse_comment('<a href="#p123" class="quotelink">&gt;&gt;123</a>'))

    def test_entities(self):
        r = str(parse_comment("&gt; &lt; &amp; &#039; &quot;"))
        assert ">" in r and "<" in r and "&" in r

    def test_complex(self):
        html = (
            '<a href="#p11" class="quotelink">&gt;&gt;11</a><br>'
            '<span class="quote">&gt;be me</span><br>'
            'Normal <b>bold</b>'
        )
        r = str(parse_comment(html))
        assert ">>11" in r and ">be me" in r and "bold" in r


class TestStrip:
    def test_empty(self):
        assert strip_html("") == ""

    def test_tags(self):
        assert "bold" in strip_html("<b>bold</b>")
        assert "<" not in strip_html("<b>bold</b>")

    def test_entities(self):
        assert strip_html("&gt;hi") == ">hi"


class TestRefs:
    def test_none(self):
        assert quote_refs("plain") == []

    def test_single(self):
        assert quote_refs('<a href="#p123" class="quotelink">x</a>') == [123]

    def test_multi(self):
        h = '<a href="#p1" class="quotelink">x</a><a href="#p2" class="quotelink">y</a>'
        assert quote_refs(h) == [1, 2]
