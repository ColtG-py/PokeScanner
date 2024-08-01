import tkinter as tk
from PIL import Image, ImageTk
import os
import threading
import numpy as np
from image_processing import select_region, capture_region, extract_text_from_image
from ai import get_corrected_name_and_level
from utils import process_image_and_get_moveset
import time

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Pokémon Moveset OCR")

        self.select_name_button = tk.Button(root, text="Select Pokémon Name Region", command=self.select_name_region)
        self.select_name_button.pack(pady=10)

        self.select_level_button = tk.Button(root, text="Select Pokémon Level Region", command=self.select_level_region)
        self.select_level_button.pack(pady=10)

        self.monitor_button = tk.Button(root, text="Start Monitoring", command=self.start_monitoring)
        self.monitor_button.pack(pady=10)

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

        self.name_region = None
        self.level_region = None
        self.monitoring = False
        self.monitor_thread = None

    def select_name_region(self):
        self.name_region = select_region()

    def select_level_region(self):
        self.level_region = select_region()

    def start_monitoring(self):
        if self.name_region and self.level_region:
            if self.monitoring:
                self.stop_monitoring()
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_regions, args=(self.name_region, self.level_region))
            self.monitor_thread.start()

    def stop_monitoring(self):
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
            self.monitor_thread = None

    def monitor_regions(self, name_region, level_region):
        prev_screenshot_name = None
        prev_screenshot_level = None
        while self.monitoring:
            screenshot_name = capture_region(name_region)
            screenshot_level = capture_region(level_region)
            screenshot_name_np = np.array(screenshot_name)
            screenshot_level_np = np.array(screenshot_level)
            if (prev_screenshot_name is None or not np.array_equal(screenshot_name_np, prev_screenshot_name)) or \
               (prev_screenshot_level is None or not np.array_equal(screenshot_level_np, prev_screenshot_level)):
                result = self.process_images_and_get_moveset(screenshot_name, screenshot_level)
                prev_screenshot_name = screenshot_name_np
                prev_screenshot_level = screenshot_level_np
                if isinstance(result, dict):
                    self.update_gui(result)
                else:
                    print(result)

    def process_images_and_get_moveset(self, name_image, level_image):
        name_text = extract_text_from_image(name_image)
        level_text = extract_text_from_image(level_image)
        
        name = name_text.split()[0] if name_text else ""
        level = 0
        if level_text:
            level_parts = level_text.split()
            if len(level_parts) > 1:
                try:
                    level = int(level_parts[1].replace('Lv', '').replace('Lv.', ''))
                except ValueError:
                    level = 0

        if not name or not level:
            if name == "NULL":
                time.sleep(10)
                return
            corrected_text = get_corrected_name_and_level(name_text + " " + level_text)
            corrected_parts = corrected_text.split()
            if len(corrected_parts) >= 2:
                name = corrected_parts[0]
                level = int(corrected_parts[-1].replace('Lv', '').replace('Lv.', ''))

        if name and level:
            return process_image_and_get_moveset(name, level)
        else:
            return "Failed to extract Pokémon name or level."

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

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
