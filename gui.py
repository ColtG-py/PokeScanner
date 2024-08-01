import tkinter as tk
import numpy as np
from PIL import Image, ImageTk
import os
import threading
from image_processing import select_region, capture_region, extract_text_from_image
from utils import process_image_and_get_moveset
from ai import get_corrected_name_and_level

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Pokémon Moveset OCR")
        self.screenshot_button = tk.Button(root, text="Select Region and Monitor", command=self.select_region)
        self.screenshot_button.pack(pady=20)

        self.info_frame = tk.Frame(root)
        self.info_frame.pack(pady=10)
        
        self.sprite_label = tk.Label(root)
        self.sprite_label.pack(pady=10)
        
        self.name_frame = tk.Frame(self.info_frame, bg="#F0F0F0", bd=2, relief="groove")
        self.name_frame.grid(row=0, column=0, padx=5)
        self.name_label = tk.Label(self.name_frame, text="Pokémon: ", font=("Helvetica", 16), bg="#F0F0F0")
        self.name_label.pack(side=tk.LEFT, padx=5)
        self.name_value = tk.Label(self.name_frame, text="", font=("Helvetica", 16), bg="#F0F0F0")
        self.name_value.pack(side=tk.LEFT, padx=5)
        
        self.level_frame = tk.Frame(self.info_frame, bg="#F0F0F0", bd=2, relief="groove")
        self.level_frame.grid(row=0, column=1, padx=5)
        self.level_label = tk.Label(self.level_frame, text="Level: ", font=("Helvetica", 16), bg="#F0F0F0")
        self.level_label.pack(side=tk.LEFT, padx=5)
        self.level_value = tk.Label(self.level_frame, text="", font=("Helvetica", 16), bg="#F0F0F0")
        self.level_value.pack(side=tk.LEFT, padx=5)

        self.types_frame = tk.Frame(self.info_frame, bg="#F0F0F0", bd=2, relief="groove")
        self.types_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        self.types_label = tk.Label(self.types_frame, text="Types: ", font=("Helvetica", 16), bg="#F0F0F0")
        self.types_label.pack(side=tk.LEFT, padx=5)
        self.types_value = tk.Label(self.types_frame, text="", font=("Helvetica", 16), bg="#F0F0F0")
        self.types_value.pack(side=tk.LEFT, padx=5)
        
        self.moves_frame = tk.Frame(root, bg="#F0F0F0", bd=2, relief="groove")
        self.moves_frame.pack(pady=20)

        self.monitoring = False
        self.monitor_thread = None

    def select_region(self):
        self.region = select_region()
        if self.region:
            self.start_monitoring(self.region)

    def start_monitoring(self, region):
        if self.monitoring:
            self.stop_monitoring()
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_region, args=(region,))
        self.monitor_thread.start()

    def stop_monitoring(self):
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
            self.monitor_thread = None

    def monitor_region(self, region):
        prev_screenshot = None
        while self.monitoring:
            screenshot = capture_region(region)
            screenshot_np = np.array(screenshot)
            if prev_screenshot is None or not np.array_equal(screenshot_np, prev_screenshot):
                result = process_image_and_get_moveset(screenshot)
                prev_screenshot = screenshot_np
                if isinstance(result, dict):
                    self.update_gui(result)
                else:
                    print(result)

    def update_gui(self, result):
        self.name_value.config(text=result['pokemon_name'])
        self.level_value.config(text=result['level'])
        self.types_value.config(text=', '.join(result['types']))

        # Load and display the sprite
        sprite_path = f"sprites/pokemon/versions/generation-iii/emerald/{result['pokedex_number']}.png"
        if os.path.exists(sprite_path):
            sprite_image = Image.open(sprite_path)
            sprite_image = sprite_image.resize((100, 100), Image.LANCZOS)
            sprite_photo = ImageTk.PhotoImage(sprite_image)
            self.sprite_label.config(image=sprite_photo)
            self.sprite_label.image = sprite_photo
        
        # Clear previous moves
        for widget in self.moves_frame.winfo_children():
            widget.destroy()
        
        for i, (move, power) in enumerate(result['moveset']):
            move_frame = tk.Frame(self.moves_frame, bg="#F0F0F0", bd=2, relief="groove")
            move_frame.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="nsew")
            power_label = tk.Label(move_frame, text=str(power), font=("Helvetica", 16), bg="#F0F0F0")
            power_label.pack(side=tk.LEFT, padx=5)
            move_label = tk.Label(move_frame, text=move.capitalize(), font=("Helvetica", 16), bg="#F0F0F0")
            move_label.pack(side=tk.LEFT, padx=5)

    def on_closing(self):
        self.stop_monitoring()
        self.root.destroy()
