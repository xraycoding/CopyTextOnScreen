import tkinter as tk
from PIL import ImageGrab
import pytesseract, pyperclip, keyboard, threading, queue, time

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

hotkey = "ctrl+alt+s"
q = queue.Queue()
root = None

def ocr(box):
    time.sleep(.1)
    text = pytesseract.image_to_string(ImageGrab.grab(bbox=box)).strip()
    if text:
        pyperclip.copy(text)
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()

def select():
    w = tk.Toplevel(root)
    w.attributes("-fullscreen", True)
    w.attributes("-alpha", .25)
    w.attributes("-topmost", True)
    w.overrideredirect(True)

    c = tk.Canvas(w, cursor="cross", bg="grey", highlightthickness=0)
    c.pack(fill="both", expand=True)

    data = [0, 0, None]

    def down(e):
        data[0], data[1] = e.x_root, e.y_root
        data[2] = c.create_rectangle(e.x, e.y, e.x, e.y, outline="red", width=2)

    def drag(e):
        if data[2]:
            c.coords(data[2], data[0]-w.winfo_rootx(), data[1]-w.winfo_rooty(), e.x, e.y)

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
    keyboard.add_hotkey(hotkey, lambda: q.put("select"))
    keyboard.wait()

root = tk.Tk()
root.withdraw()
threading.Thread(target=listen, daemon=True).start()
root.after(50, check)
root.mainloop()
