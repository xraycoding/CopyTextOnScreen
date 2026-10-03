import os
import sys
import tkinter as tk
from PIL import ImageGrab
import pytesseract
import pyperclip
from pynput import keyboard
import threading
import queue
import time
import shutil

def resource_path(path):
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), path)

def find_tesseract():
    bundled = resource_path(
        os.path.join(
            "tesseract",
            "tesseract.exe" if sys.platform == "win32" else "tesseract"
        )
    )

    if os.path.isfile(bundled):
        return bundled

    system = shutil.which("tesseract")

    if system:
        return system

    mac_paths = [
        "/opt/homebrew/bin/tesseract",
        "/usr/local/bin/tesseract"
    ]

    for path in mac_paths:
        if os.path.isfile(path):
            return path

    return None

tesseract = find_tesseract()

if not tesseract:
    raise RuntimeError("Tesseract OCR was not found.")

pytesseract.pytesseract.tesseract_cmd = tesseract

hotkey = "<ctrl>+<alt>+s"
q = queue.Queue()
root = None

def ocr(box):
    time.sleep(0.1)

    try:
        image = ImageGrab.grab(bbox=box)
        text = pytesseract.image_to_string(image).strip()

        if text:
            pyperclip.copy(text)
    except Exception as e:
        print(e)

def select():
    w = tk.Toplevel(root)
    w.attributes("-fullscreen", True)
    w.attributes("-alpha", 0.25)
    w.attributes("-topmost", True)
    w.overrideredirect(True)

    c = tk.Canvas(
        w,
        cursor="cross",
        bg="grey",
        highlightthickness=0
    )
    c.pack(fill="both", expand=True)

    data = [0, 0, None]

    def down(e):
        data[0] = e.x_root
        data[1] = e.y_root
        data[2] = c.create_rectangle(
            e.x,
            e.y,
            e.x,
            e.y,
            outline="red",
            width=2
        )

    def drag(e):
        if data[2]:
            c.coords(
                data[2],
                data[0] - w.winfo_rootx(),
                data[1] - w.winfo_rooty(),
                e.x,
                e.y
            )

    def up(e):
        box = (
            min(data[0], e.x_root),
            min(data[1], e.y_root),
            max(data[0], e.x_root),
            max(data[1], e.y_root)
        )

        w.destroy()
        root.after(100, lambda: ocr(box))

    c.bind("<ButtonPress-1>", down)
    c.bind("<B1-Motion>", drag)
    c.bind("<ButtonRelease-1>", up)
    w.bind("<Escape>", lambda e: w.destroy())

    w.focus_force()
    w.grab_set()

def check():
    try:
        while True:
            if q.get_nowait() == "select":
                select()
    except queue.Empty:
        pass

    root.after(50, check)

def listen():
    def on_activate():
        q.put("select")

    with keyboard.GlobalHotKeys({
        hotkey: on_activate
    }) as h:
        h.join()

root = tk.Tk()
root.withdraw()

threading.Thread(
    target=listen,
    daemon=True
).start()

root.after(50, check)
root.mainloop()

