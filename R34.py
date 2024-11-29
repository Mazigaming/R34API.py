import requests
import xml.etree.ElementTree as ET
from PIL import Image, ImageTk, ImageSequence
from io import BytesIO
import random
import os
import tkinter as tk
from tkinter import messagebox, simpledialog

class Viewer:
    def __init__(self, root):
        self.root = root
        self.root.geometry("900x700")
        self.imgs, self.curr, self.data = [], 0, None
        self.setup_ui()
        self.setup_bindings()

    def setup_ui(self):
        frm = tk.Frame(self.root, bg="#f1c0a7")
        frm.pack(expand=True)
        tk.Label(frm, text="Viewer", font=("Comic Sans MS", 18, 'bold'), bg="#f1c0a7").pack(pady=20)
        self.rate = tk.Scale(frm, from_=0, to=10, orient=tk.HORIZONTAL, label="Min Rating")
        self.rate.pack()
        self.img_lbl = tk.Label(frm, bg="#f1c0a7")
        self.img_lbl.pack(pady=20)
        btn_frm = tk.Frame(frm, bg="#f1c0a7")
        btn_frm.pack()
        self.prev_btn = tk.Button(btn_frm, text="Prev", command=self.show_prev, state=tk.DISABLED)
        self.prev_btn.grid(row=0, column=0, padx=5)
        self.next_btn = tk.Button(btn_frm, text="Next", command=self.show_next, state=tk.DISABLED)
        self.next_btn.grid(row=0, column=1, padx=5)
        tk.Button(frm, text="Fetch", command=self.fetch_imgs).pack(pady=10)
        self.save_btn = tk.Button(frm, text="Save", command=self.save_img, state=tk.DISABLED)
        self.save_btn.pack()

    def setup_bindings(self):
        self.root.bind("<Left>", self.show_prev)
        self.root.bind("<Right>", self.show_next)
        self.root.bind("<f>", lambda e: self.fetch_imgs())
        self.root.bind("<Control-s>", lambda e: self.save_img())

    def fetch_api(self, tags, limit=100):
        url = "https://api.rule34.xxx/index.php?page=dapi&s=post&q=index"
        res, page = [], 0
        tags_query = '+'.join(tags)  # Join multiple tags with '+'
        while len(res) < limit:
            try:
                r = requests.get(url, params={'limit': 100, 'pid': page, 'tags': tags_query})
                r.raise_for_status()
                for post in ET.fromstring(r.content).findall("post"):
                    if len(res) >= limit: break
                    if img_url := post.get("file_url"): res.append((img_url, int(post.get("score", 0))))
                page += 1
            except Exception as e:
                print(f"Error fetching API: {e}")
                break
        return res

    def fetch_imgs(self):
        tags_input = simpledialog.askstring("Tags", "Enter tags ")
        if not tags_input: return
        tags = [tag.strip() for tag in tags_input.split(',')]  # Split and clean tags
        count = simpledialog.askinteger("Count", "How many images?", minvalue=1, maxvalue=100)
        if not count: return
        self.imgs = [img for img in self.fetch_api(tags, 1000) if img[1] >= self.rate.get()]
        random.shuffle(self.imgs)
        self.imgs = self.imgs[:count]
        self.curr = 0
        if self.imgs: self.show_img()

    def show_img(self):
        if not self.imgs: return
        try:
            r = requests.get(self.imgs[self.curr][0])
            r.raise_for_status()
            content_type = r.headers['Content-Type']

            if 'image' in content_type:
                self.display_image(r.content)
            elif 'gif' in content_type:
                self.display_gif(r.content)
            else:
                self.img_lbl.config(text="Unsupported file format")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")

    def display_image(self, content):
        self.data = content
        img = Image.open(BytesIO(self.data))
        img.thumbnail((600, 600))
        img_tk = ImageTk.PhotoImage(img)
        self.img_lbl.config(image=img_tk)
        self.img_lbl.image = img_tk
        self.save_btn.config(state=tk.NORMAL)
        self.prev_btn.config(state=tk.NORMAL if self.curr > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if self.curr < len(self.imgs) - 1 else tk.DISABLED)

    def display_gif(self, content):
        self.data = content
        gif = Image.open(BytesIO(self.data))
        frames = [ImageTk.PhotoImage(frame.copy()) for frame in ImageSequence.Iterator(gif)]
        self.animate_gif(frames)

    def animate_gif(self, frames, idx=0):
        self.img_lbl.config(image=frames[idx])
        self.img_lbl.image = frames[idx]
        self.root.after(100, self.animate_gif, frames, (idx + 1) % len(frames))

    def save_img(self, event=None):
        if not self.data: return
        save_dir = os.path.expanduser("~/Viewer")
        os.makedirs(save_dir, exist_ok=True)
        with open(os.path.join(save_dir, f"img_{self.curr + 1}.png"), "wb") as f:
            f.write(self.data)

    def show_prev(self, event=None):
        if self.curr > 0: self.curr -= 1; self.show_img()

    def show_next(self, event=None):
        if self.curr < len(self.imgs) - 1: self.curr += 1; self.show_img()

if __name__ == "__main__":
    root = tk.Tk()
    Viewer(root)
    root.mainloop()
