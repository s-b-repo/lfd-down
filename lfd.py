#!/usr/bin/env python3
"""lfd — a tiny tkinter GUI that shells out to aria2c to download a batch
of URLs (one per line) into a chosen directory."""

import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


def ensure_aria2_installed():
    """Return True if aria2c is on PATH; otherwise show a message and return False.

    The old version tried to `sudo pacman -S aria2` unconditionally, which
    is Arch-only and blocks the GUI. Now we just tell the user what to
    install and let them handle it.
    """
    if shutil.which("aria2c"):
        return True
    messagebox.showerror(
        "aria2 not found",
        "aria2c is required but was not found on your PATH.\n\n"
        "Install it with your package manager, e.g.:\n"
        "  Arch:   sudo pacman -S aria2\n"
        "  Debian: sudo apt install aria2\n"
        "  Fedora: sudo dnf install aria2\n"
        "  macOS:  brew install aria2",
    )
    return False


def download_one(link, save_path):
    """Blocking single-URL download. Returns aria2c's exit code."""
    return subprocess.run(
        ["aria2c", "-d", save_path, link],
        check=False,
    ).returncode


def start_download(root, links_input, save_path, progress_bar, status_var):
    """Kick off one worker thread per non-empty URL.

    Everything that touches the tk widgets from the worker thread is
    marshalled back onto the main loop via ``root.after(0, …)`` — tkinter
    is not thread-safe and the old code stepped the progress bar
    directly from the worker.
    """
    raw = links_input.get("1.0", "end-1c").splitlines()
    links = [line.strip() for line in raw if line.strip()]

    if not links:
        messagebox.showwarning("Nothing to do", "Paste at least one URL first.")
        return
    if not save_path:
        messagebox.showwarning("No destination", "Pick a download folder first.")
        return

    progress_bar["maximum"] = len(links)
    progress_bar["value"] = 0
    remaining = {"n": len(links)}

    def mark_done(link, rc):
        progress_bar["value"] += 1
        remaining["n"] -= 1
        status_var.set(
            f"{link}  →  exit={rc}    ({remaining['n']} remaining)"
        )
        if remaining["n"] == 0:
            status_var.set(f"Done — {len(links)} URL(s) processed.")

    def worker(link):
        rc = download_one(link, save_path)
        root.after(0, mark_done, link, rc)

    for link in links:
        threading.Thread(target=worker, args=(link,), daemon=True).start()


def choose_folder(save_path_var):
    path = filedialog.askdirectory()
    if path:
        save_path_var.set(path)


def main():
    root = tk.Tk()
    root.title("lfd — bulk aria2 downloader")
    root.geometry("560x420")

    save_path_var = tk.StringVar(value="")
    status_var = tk.StringVar(value="Idle.")

    tk.Label(root, text="One URL per line:").pack(anchor="w", padx=10, pady=(10, 0))
    links_input = tk.Text(root, height=12)
    links_input.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    row = tk.Frame(root)
    row.pack(fill="x", padx=10)
    tk.Button(row, text="Choose folder…", command=lambda: choose_folder(save_path_var)).pack(side="left")
    tk.Label(row, textvariable=save_path_var, anchor="w").pack(side="left", fill="x", expand=True, padx=(8, 0))

    progress_bar = ttk.Progressbar(root, mode="determinate")
    progress_bar.pack(fill="x", padx=10, pady=(10, 0))

    tk.Label(root, textvariable=status_var, anchor="w").pack(fill="x", padx=10, pady=(4, 0))

    tk.Button(
        root,
        text="Start Download",
        command=lambda: start_download(
            root, links_input, save_path_var.get(), progress_bar, status_var
        ),
    ).pack(pady=10)

    if not ensure_aria2_installed():
        root.destroy()
        return

    root.mainloop()


if __name__ == "__main__":
    main()
