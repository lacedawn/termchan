# termchan

```
  ,--.                                ,--.
,-'  '-. ,---. ,--.--.,--,--,--. ,---.|  ,---.  ,--,--.,--,--,
'-.  .-'| .-. :|  .--'|        || .--'|  .-.  |' ,-.  ||      \
  |  |  \   --.|  |   |  |  |  |\ `--.|  | |  |\ '-'  ||  ||  |
  `--'   `----'`--'   `--`--`--' `---'`--' `--' `--`--'`--''--'
```

browse 4chan from your terminal

## demo

<div align="center">
  <video src="https://github.com/user-attachments/assets/2a92f92a-19b5-47ee-b901-8ca4c99c84ec" width="100%" autoplay loop muted playsinline></video>
</div>

## install

```bash
pip install -e .
```

needs python 3.11+ and a terminal with mouse support.
for best image quality, use a terminal with kitty graphics protocol (kitty, wezterm, etc).

## run

```bash
termchan
# or
python -m termchan
```

## keys

| key | what it does |
|-----|-------------|
| `Enter` | select / open |
| `q` / `Esc` | go back |
| `r` | refresh |
| `i` | show image inline |
| `o` | open image externally |

hover over a post to select it, then use `i` / `o`


## dependencies

- [textual](https://github.com/Textualize/textual) — tui framework
- [httpx](https://github.com/encode/httpx) — async http
- [textual-image](https://github.com/lnqs/textual-image) — terminal images
- [Pillow](https://github.com/python-pillow/Pillow) — image processing
