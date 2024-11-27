import requests
import xml.etree.ElementTree as ET
from PIL import Image, ImageTk
from io import BytesIO
import random
import os
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog


class ImageViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Viewer")
        self.root.config(bg="#f1c0a7")  # bg kolor

        # Vars
        self.images = []
        self.current_index = 0
        self.current_image_data = None  # Save raw img data

        # Set window rozmiar
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # Center 
        self.center_window()

        #  widgets
        self.main_frame = tk.Frame(self.root, bg="#f1c0a7")
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")  # Center the frame

        # GUI set up 
        self._setup_gui()

        # ctrl + s bind
        self.root.bind("<Control-s>", self.save_current_image)

    def center_window(self):
        """Center the window on the screen."""
        window_width = 900
        window_height = 700

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        position_top = int(screen_height / 2 - window_height / 2)
        position_left = int(screen_width / 2 - window_width / 2)

        self.root.geometry(f'{window_width}x{window_height}+{position_left}+{position_top}')

    def _setup_gui(self):
        """Todo: upgrade gui (estetycznie)"""
        
        # Title l
        self.author_label = tk.Label(
            self.main_frame, text="Welcome to Image Viewer!", font=("Comic Sans MS", 18, 'bold'), bg="#f1c0a7", fg="#800000"
        )
        self.author_label.grid(row=0, column=0, columnspan=3, pady=20)

        # Rating 
        self.rating_label = tk.Label(
            self.main_frame, text="Minimum Rating:", font=("Arial", 12), bg="#f1c0a7", fg="#800000"
        )
        self.rating_label.grid(row=1, column=0, padx=15, sticky="w")

        self.rating_slider = tk.Scale(
            self.main_frame, from_=0, to=10, orient=tk.HORIZONTAL, sliderlength=30, length=400,
            bg="#fff", fg="#800000", font=("Arial", 12)
        )
        self.rating_slider.grid(row=1, column=1, padx=15)

        # Frame 
        self.image_frame = tk.Frame(self.main_frame, bg="#f1c0a7")
        self.image_frame.grid(row=2, column=0, columnspan=3, pady=30)

        # Previous 
        self.prev_button = tk.Button(
            self.image_frame, text="Previous", command=self.show_previous_image, state=tk.DISABLED,
            font=("Arial", 12, 'bold'), bg="#ff7f7f", fg="#fff", relief="solid", height=2, width=10
        )
        self.prev_button.grid(row=0, column=0, padx=10)

        # Image display
        self.image_label = tk.Label(self.image_frame, bg="#f1c0a7")
        self.image_label.grid(row=0, column=1, padx=20)

        # Next 
        self.next_button = tk.Button(
            self.image_frame, text="Next", command=self.show_next_image, state=tk.DISABLED,
            font=("Arial", 12, 'bold'), bg="#ff7f7f", fg="#fff", relief="solid", height=2, width=10
        )
        self.next_button.grid(row=0, column=2, padx=10)

        # Fetch 
        self.fetch_button = tk.Button(
            self.main_frame, text="Fetch Images", command=self.fetch_and_display_images,
            font=("Arial", 14, 'bold'), bg="#ff4040", fg="#fff", relief="solid", height=2, width=15
        )
        self.fetch_button.grid(row=3, column=0, padx=10, pady=10, sticky="ew")  # Left-aligned

        # Save 
        self.save_button = tk.Button(
            self.main_frame, text="Save Image", command=self.save_current_image, state=tk.DISABLED,
            font=("Arial", 14, 'bold'), bg="#4CAF50", fg="#fff", relief="solid", height=2, width=15
        )
        self.save_button.grid(row=3, column=2, padx=10, pady=10, sticky="ew")  

        
        self.main_frame.update_idletasks()

    def fetch_images_by_tag(self, tag, total_limit=100):
        """Fetch przez tagi"""
        api_url = "https://api.rule34.xxx/index.php?page=dapi&s=post&q=index"
        images = []
        page = 0
        per_page_limit = 100  # Rule34 limit to 1000 zmniejszone dla lepszej optymalnosci

        while len(images) < total_limit:
            params = {
                'limit': per_page_limit,
                'pid': page,
                'tags': tag  # tag filter
            }

            try:
                response = requests.get(api_url, params=params)
                response.raise_for_status()

                root = ET.fromstring(response.content)
                posts = root.findall("post")

                if not posts:  # no img dostepne
                    break

                # Extract img data!
                for post in posts:
                    if len(images) >= total_limit:
                        break
                    image_url = post.get("file_url")
                    author = post.get("creator_id", "Unknown")
                    score = int(post.get("score", 0))

                    if image_url:
                        images.append((image_url, author, score))

                page += 1

            except requests.RequestException as e:
                messagebox.showerror("Error", f"Network error: {e}")
                break
            except ET.ParseError:
                messagebox.showerror("Error", "parase Api nie zadziałał")
                break

        return images

    def fetch_and_display_images(self):
        """Fetch and display img na bazie"""
        # Get the tag from the user
        tag = simpledialog.askstring("Daj tag", "daj tag(my fav 'bondage,mommy asmr,sigma')").strip()

        if not tag:
            messagebox.showerror("Daj tag error", "Dobry tag ale go nie ma.")
            return

        try:
            limit = simpledialog.askinteger("Liczba obrazków", "Ile potrzeba do goonowania?", minvalue=1, maxvalue=1000)
            if not limit:
                return  # Cancer f usr
        except ValueError:
            messagebox.showerror("Retard", "debilu daj pomiedzy 1-1000 anie jakies misz masz")
            return

        min_score = self.rating_slider.get()
        self.images = self.fetch_images_by_tag(tag, total_limit=1000)  # Fetch obrazki
        # Filter obrazku
        self.images = [img for img in self.images if img[2] >= min_score]  #filtruje ci rating

        # Shuffle 
        random.shuffle(self.images)

        # Limit obrazków
        self.images = self.images[:limit]

        # display 1st
        if self.images:
            self.show_image(self.current_index)
            self.update_buttons()
        else:
            messagebox.showinfo("ni ma obrazu", "Ni ma tego tagu goonerze")

    def show_image(self, index):
        """display specialnego indexu"""
        try:
            image_url, author, score = self.images[index]

            # Fetch i display
            response = requests.get(image_url)
            response.raise_for_status()
            self.current_image_data = response.content  # Save raw img

            img = Image.open(BytesIO(self.current_image_data))
            img.thumbnail((600, 600))  # Resize dla thumbnail
            img_tk = ImageTk.PhotoImage(img)

            self.image_label.configure(image=img_tk)
            self.image_label.image = img_tk  # Optimize img ref

            self.author_label.configure(text=f"By: {author} | Rating: {score}")
            self.save_button.config(state=tk.NORMAL)  # save img
        except Exception as e:
            messagebox.showerror("Error", f"TO by nic nie dało: {e}")

    def save_current_image(self, event=None):
        """zapis obrazu"""
        if not self.current_image_data:
            messagebox.showwarning("nie ma obrazu", "No imga nie ma do zapisu ")
            return

        # nowy folder
        save_folder = os.path.join(os.path.expanduser("~"), "GooningFolder")
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        # uniq file nazwa nigg
        save_path = os.path.join(save_folder, f"image_{self.current_index+1}.png")

        try:
            with open(save_path, "wb") as file:
                file.write(self.current_image_data)

            messagebox.showinfo("Success", f"Image saved to {save_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {e}")

    def show_previous_image(self):
        """poprzedni"""
        if self.current_index > 0:
            self.current_index -= 1
            self.show_image(self.current_index)
            self.update_buttons()

    def show_next_image(self):
        """next"""
        if self.current_index < len(self.images) - 1:
            self.current_index += 1
            self.show_image(self.current_index)
            self.update_buttons()

    def update_buttons(self):
        """navigacja ."""
        if self.current_index == 0:
            self.prev_button.config(state=tk.DISABLED)
        else:
            self.prev_button.config(state=tk.NORMAL)

        if self.current_index == len(self.images) - 1:
            self.next_button.config(state=tk.DISABLED)
        else:
            self.next_button.config(state=tk.NORMAL)


# Okienko <3
root = tk.Tk()
app = ImageViewerApp(root)
root.mainloop()
