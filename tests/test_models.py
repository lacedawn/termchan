from termchan.models import Board, CatalogThread, Post


class TestBoard:
    def test_basic(self):
        b = Board.from_json({"board": "g", "title": "Technology", "ws_board": 1})
        assert b.board == "g"
        assert b.title == "Technology"
        assert b.ws_board is True

    def test_slug(self):
        b = Board.from_json({"board": "pol", "title": "Politics", "ws_board": 0})
        assert b.slug == "/pol/"

    def test_defaults(self):
        b = Board.from_json({"board": "x", "title": "X"})
        assert b.ws_board is False
        assert b.pages == 10


class TestPost:
    SAMPLE = {
        "no": 123, "now": "01/15/26(Thu)12:34:56", "name": "Anonymous",
        "com": '<span class="quote">&gt;implying</span>',
        "sub": "Test", "tim": 170531249, "ext": ".png", "filename": "shot",
        "w": 1920, "h": 1080, "fsize": 131072, "resto": 0,
        "trip": "!abc", "capcode": "mod", "country": "US",
        "country_name": "United States", "id": "AbC",
    }

    def test_parse(self):
        p = Post.from_json(self.SAMPLE)
        assert p.no == 123
        assert p.has_image
        assert "shot.png" in p.file_info
        assert "1920x1080" in p.file_info

    def test_urls(self):
        p = Post.from_json(self.SAMPLE)
        assert p.image_url("g") == "https://i.4cdn.org/g/170531249.png"
        assert p.thumb_url("g") == "https://i.4cdn.org/g/170531249s.jpg"

    def test_no_image(self):
        p = Post.from_json({"no": 1})
        assert not p.has_image
        assert p.image_url("g") is None
        assert p.file_info == ""

    def test_defaults(self):
        p = Post.from_json({"no": 42})
        assert p.name == "Anonymous"
        assert p.com == ""


class TestCatalogThread:
    SAMPLE = {
        "no": 999, "sub": "Test Thread", "replies": 42, "images": 7,
        "tim": 170531249, "ext": ".jpg", "sticky": 1, "closed": 0,
        "last_replies": [{"no": 1000, "com": "Reply"}],
    }

    def test_parse(self):
        t = CatalogThread.from_json(self.SAMPLE)
        assert t.no == 999
        assert t.replies == 42
        assert t.sticky is True
        assert t.closed is False

    def test_replies(self):
        t = CatalogThread.from_json(self.SAMPLE)
        assert len(t.last_replies) == 1
        assert t.last_replies[0].no == 1000

    def test_title(self):
        t = CatalogThread.from_json(self.SAMPLE)
        assert t.title == "Test Thread"

    def test_title_fallback(self):
        d = {**self.SAMPLE, "sub": "", "com": "Hello <b>world</b>"}
        t = CatalogThread.from_json(d)
        assert "Hello" in t.title
        assert "<b>" not in t.title

    def test_defaults(self):
        t = CatalogThread.from_json({"no": 1})
        assert t.replies == 0
        assert t.last_replies == []
