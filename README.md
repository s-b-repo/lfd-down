# lfd — bulk `aria2c` downloader (GUI)

A tiny tkinter GUI that takes a list of URLs, one per line, and hands
them to `aria2c` — the acceleration/segmentation is aria2's job, this
is just a convenient front-end for batches.

## Requirements

- Python 3.7+
- `aria2c` on `PATH`. The GUI checks at startup and tells you how to
  install it if it's missing.
  - Arch: `sudo pacman -S aria2`
  - Debian/Ubuntu: `sudo apt install aria2`
  - Fedora: `sudo dnf install aria2`
  - macOS: `brew install aria2`
- `tkinter` (usually bundled with Python; on Debian/Ubuntu install
  `python3-tk` if not).

## Usage

```
python3 lfd.py
```

1. Click **Choose folder…** and pick a destination.
2. Paste URLs into the big text box — one per line, blank lines ignored.
3. Click **Start Download**. Each URL runs in its own thread; the
   progress bar advances as each aria2c invocation exits.

## Notes

- Linux is the intended platform, but nothing here is Linux-specific —
  should work on macOS and (in theory) Windows with `aria2c.exe` on
  PATH.
- The status bar shows the last URL to finish and the exit code from
  `aria2c` (0 = success). Non-zero exit codes mean aria2 rejected the
  URL or failed to download; check its stderr in the terminal you
  launched the GUI from.
- Files named `beta version01` (in this repo) are an earlier CLI-only
  prototype. They're kept for history; the current entry point is
  `lfd.py`.

## What changed vs the previous version

- Fixed a `NameError` on `Start Download` — the progress bar was being
  constructed against `root`, which wasn't in scope inside
  `start_download`.
- Removed the `sudo pacman -S aria2` auto-install (Arch-only, ran
  without user consent, and blocked the GUI). Now the GUI just checks
  for `aria2c` and prompts.
- The main window is no longer hidden with `withdraw()` before packing
  widgets into it.
- Progress-bar updates from worker threads are now marshalled through
  `root.after(…)` — tkinter is not thread-safe and the old code stepped
  the bar directly from worker threads.

## License

MIT — see [LICENSE](LICENSE).
