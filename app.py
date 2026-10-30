"""Simple window: type a website, choose what to collect, click Start.
Run:  python app.py
"""
import logging, os, subprocess, sys, threading, tkinter as tk
from tkinter import ttk, messagebox
from logger import get_logger
from easy_scrape import scrape

KINDS = [("Headings", "headings"), ("Paragraphs / text", "paragraphs"), ("Links", "links"),
         ("Images", "images"), ("Tables", "tables"), ("Email addresses", "emails")]

class BoxHandler(logging.Handler):
    def __init__(self, app): super().__init__(); self.app = app
    def emit(self, r): self.app.root.after(0, self.app.write, self.format(r))

class App:
    def __init__(self, root):
        self.root, self.last = root, None
        root.title("Web Scraper"); root.geometry("640x560")
        f = ttk.Frame(root, padding=16); f.pack(fill="both", expand=True)
        ttk.Label(f, text="Website to scrape (required)", font=("", 12, "bold")).pack(anchor="w")
        self.url = ttk.Entry(f, font=("", 12)); self.url.pack(fill="x", pady=(4, 12))
        ttk.Label(f, text="What do you want to collect?", font=("", 11, "bold")).pack(anchor="w")
        g = ttk.Frame(f); g.pack(fill="x", pady=4)
        self.vars = {}
        for i, (label, key) in enumerate(KINDS):
            v = tk.BooleanVar(value=key in ("headings", "paragraphs", "links"))
            ttk.Checkbutton(g, text=label, variable=v).grid(row=i // 3, column=i % 3, sticky="w", padx=6, pady=2)
            self.vars[key] = v
        o = ttk.Frame(f); o.pack(fill="x", pady=10)
        ttk.Label(o, text="Pages:").pack(side="left")
        self.pages = ttk.Spinbox(o, from_=1, to=50, width=5); self.pages.set(1); self.pages.pack(side="left", padx=(4, 16))
        ttk.Label(o, text="Save as:").pack(side="left")
        self.fmt = ttk.Combobox(o, values=["csv", "json", "sqlite"], width=8, state="readonly"); self.fmt.set("csv")
        self.fmt.pack(side="left", padx=4)
        b = ttk.Frame(f); b.pack(fill="x")
        self.start = ttk.Button(b, text="Start scraping", command=self.run); self.start.pack(side="left")
        self.openb = ttk.Button(b, text="Open results folder", command=self.open_folder, state="disabled")
        self.openb.pack(side="left", padx=8)
        self.box = tk.Text(f, height=14, wrap="word"); self.box.pack(fill="both", expand=True, pady=(12, 0))
        h = BoxHandler(self); h.setFormatter(logging.Formatter("%(asctime)s  %(message)s", "%H:%M:%S"))
        get_logger().addHandler(h)

    def write(self, msg): self.box.insert("end", msg + "\n"); self.box.see("end")

    def run(self):
        kinds = [k for k, v in self.vars.items() if v.get()]
        url = self.url.get().strip()
        if not url: return messagebox.showwarning("Missing", "Please enter a website.")
        if not kinds: return messagebox.showwarning("Missing", "Tick at least one thing to collect.")
        self.start.config(state="disabled"); self.box.delete("1.0", "end")
        def work():
            try:
                path, n = scrape(url, kinds, int(self.pages.get()), self.fmt.get())
                msg = f"Done! Saved {n} items to:\n{path}" if path else "Finished, but nothing was found."
                self.last = path
            except Exception as e:
                msg = f"Problem: {e}"
            self.root.after(0, self.finish, msg)
        threading.Thread(target=work, daemon=True).start()

    def finish(self, msg):
        self.write(msg); self.start.config(state="normal")
        if self.last: self.openb.config(state="normal")

    def open_folder(self):
        d = os.path.dirname(self.last)
        if sys.platform.startswith("win"): os.startfile(d)
        else: subprocess.run(["open" if sys.platform == "darwin" else "xdg-open", d])

if __name__ == "__main__":
    root = tk.Tk(); App(root); root.mainloop()
