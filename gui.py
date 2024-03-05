import subprocess
import sys
import os

def install(packages):
    subprocess.check_call([sys.executable, "-m", "pip", "install", *packages])

# Example usage:
packages = ['playwright', 'tk',]
install(packages)

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
import threading
from tkinter import Toplevel, Label, StringVar
from tkinter.ttk import Progressbar
import os
import random
import string
import requests
import re
from playwright.async_api import async_playwright
import asyncio
from urllib.parse import quote, urlencode
from time import sleep
import platform
import subprocess

# Simplified logging
def info_logger(info):
    print(info)

# Simplified network logging
def network_logger(info):
    print(info)

# Simplified wordlist for random prompts
class MyWordlist:
    def get_prompt(self, size):
        words = ["abstract", "landscape", "sunset", "ocean", "mountain", "forest", "city", "vintage", "futuristic", "fantasy"]
        return ' '.join(random.choices(words, k=size))

# Styles dictionary for demo purposes
styles = {
    "no-style": ["", ""]
}

# Simplified encode function
def encode(prompt):
    replacement_dict = {' ': r'%20', ',': r'%2C'}
    translation_table = str.maketrans(replacement_dict)
    return r'%27' + prompt.translate(translation_table)

async def get_url_data():
    url_data = []
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        page = await browser.new_page()

        def request_handler(request):
            request_info = f'{request.method} {request.url} \n'
            network_logger(request_info)
            url_data.append(request.url)

        page.on("request", request_handler)  # capture traffic
        await page.goto('https://perchance.org/ai-text-to-image-generator')
        iframe_element = await page.query_selector('xpath=//iframe[@src]')
        frame = await iframe_element.content_frame()
        await frame.click('xpath=//button[@id="generateButtonEl"]')
        key = None
        while key is None:
            pattern = r'userKey=([a-f\d]{64})'
            all_urls = ''.join(url_data)
            keys = re.findall(pattern, all_urls)
            if keys:
                key = keys[0]
            url_data = []
            await asyncio.sleep(1)
        await browser.close()
    return key

def get_key():
    key = None
    try:
        with open('last-key.txt', 'r') as file:
            line = file.readline()
            if line != '':
                verification_url = 'https://image-generation.perchance.org/api/checkVerificationStatus'
                user_key = line.strip()
                cache_bust = random.random()
                verification_params = {'userKey': user_key, '__cacheBust': cache_bust}
                response = requests.get(verification_url, params=verification_params)
                if 'not_verified' not in response.text:
                    key = user_key
                    info_logger(f'Found working key {key[:10]}... in file.')
                    return key
    except FileNotFoundError:
        pass

    info_logger('Key no longer valid or not found. Looking for a new key...')
    # Modified line: Using asyncio.run() to automatically manage the event loop
    key = asyncio.run(get_url_data())

    info_logger(f'Found key {key[:10]}...')
    with open('last-key.txt', 'w') as file:
        file.write(key)

    return key

def get_pictures_folder():
    """
    Returns the path to the user's Pictures folder depending on the operating system.
    """
    home = os.path.expanduser("~")
    if platform.system() == "Windows":
        return os.path.join(home, "Pictures")
    elif platform.system() == "Linux":
        return os.path.join(home, "Pictures")
    else:
        print("Unsupported OS. Saving to home directory.")
        return home

def image_generator(base_filename='', amount=1, prompt='RANDOM', prompt_size=10, negative_prompt='', style='RANDOM', resolution='512x768', guidance_scale=7):
    create_url = 'https://image-generation.perchance.org/api/generate'
    download_url = 'https://image-generation.perchance.org/api/downloadTemporaryImage'

    if prompt == 'RANDOM':
        wordlist = MyWordlist()
        prompt_base = wordlist.get_prompt(prompt_size)
    else:
        prompt_base = prompt
    if style == 'RANDOM':
        list_of_styles = list(styles.keys())
        style_choice = random.choice(list_of_styles)
    else:
        style_choice = style

    prompt_style = styles[style_choice][0]
    negative_prompt_style = styles[style_choice][1]

    prompt_query = quote('\'' + prompt_base + ', ' + prompt_style)
    negative_prompt_query = quote('\'' + negative_prompt + ', ' + negative_prompt_style)
    info_logger(f'Selected prompt {prompt_base} and style {style_choice}')

    for idx in range(1, amount + 1):
        user_key = get_key()
        request_id = random.random()
        cache_bust = random.random()

        create_params = {
            'prompt': prompt_query,
            'negativePrompt': negative_prompt_query,
            'userKey': user_key,
            '__cache_bust': cache_bust,
            'seed': '-1',
            'resolution': resolution,
            'guidanceScale': str(guidance_scale),
            'channel': 'ai-text-to-image-generator',
            'subChannel': 'public',
            'requestId': request_id
        }
        create_params_str = urlencode(create_params, safe=':%')

        create_response = requests.get(create_url, params=create_params_str)
        if 'invalid_key' in create_response.text:
            raise Exception('Image could not be generated (invalid key).')

        exit_flag = False
        while not exit_flag:
            try:
                image_id = create_response.json()['imageId']
                exit_flag = True
            except KeyError:
                info_logger('Waiting for previous request to finish...')
                sleep(8)
                create_response = requests.get(create_url, params=create_params_str)

        download_params = {'imageId': image_id}
        download_response = requests.get(download_url, params=download_params)

        generated_dir = get_pictures_folder()
        os.makedirs(generated_dir, exist_ok=True)

        for idx in range(1, amount + 1):
            # The image generation logic remains unchanged...

            # Modify the filename path to use the generated_dir
            filename = os.path.join(generated_dir, f'{base_filename}{idx}.jpeg' if base_filename else f'{image_id}.jpeg')
            with open(filename, 'wb') as file:
                file.write(download_response.content)

            info_logger(f'Created picture {idx}/{amount} ({filename=})')
            yield {'filename': filename, 'prompt': prompt_base, 'negative_prompt': negative_prompt}

class GeneratingPopup(Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Generating")
        
        # Set the dimensions of the popup
        popup_width = 300
        popup_height = 100
        self.geometry(f"{popup_width}x{popup_height}")
        
        # Find the center position of the master window
        master_width = master.winfo_width()
        master_height = master.winfo_height()
        master_x = master.winfo_x()
        master_y = master.winfo_y()
        
        # Calculate position for the popup to be centered over the master window
        center_x = int(master_x + (master_width - popup_width) / 2)
        center_y = int(master_y + (master_height - popup_height) / 2)
        
        # Position the window at the center of the master window
        self.geometry(f"+{center_x}+{center_y}")
        
        self.label = Label(self, text="Generating image...")
        self.label.pack(pady=10)

        self.progress = Progressbar(self, orient="horizontal", length=200, mode="indeterminate")
        self.progress.pack(pady=10)
        self.progress.start()

    def close(self):
        self.progress.stop()
        self.destroy()

# GUI Application
class ImageGeneratorGUI:
    def __init__(self, master):
        self.master = master
        master.title("MakuluLinux Image Generator")
        master.geometry("950x600")  # Adjusted window size as needed

        # Initialize the canvas
        self.image_canvas = tk.Canvas(master, width=500, height=500)
        self.image_canvas.place(x=350, y=50)
        self.image_canvas.bind('<Button-1>', self.open_image)

        # Prompt input
        self.prompt_label = ttk.Label(master, text="Prompt:")
        self.prompt_label.place(x=20, y=20)
        self.prompt_entry = ttk.Entry(master, width=50)
        self.prompt_entry.place(x=120, y=20, width=200)  # Added width

        # Resolution dropdown
        self.resolution_label = ttk.Label(master, text="Resolution:")
        self.resolution_label.place(x=20, y=60)
        self.resolution_var = tk.StringVar(master)
        resolutions = ["512x512", "512x768", "768x1024", "1280x720", "1920x1080"]
        self.resolution_var.set(resolutions[0])  # default value
        self.resolution_dropdown = ttk.OptionMenu(master, self.resolution_var, *resolutions)
        self.resolution_dropdown.place(x=120, y=60, width=200)  # Added width

        # Guidance scale slider
        self.guidance_scale_label = ttk.Label(master, text="Guidance:")
        self.guidance_scale_label.place(x=20, y=100)
        self.guidance_scale_slider = ttk.Scale(master, from_=1, to_=20, orient='horizontal', value=7)
        self.guidance_scale_slider.place(x=120, y=100, width=200)  # Added width

        # Generate button
        self.generate_button = ttk.Button(master, text="Generate", command=self.generate_image)
        self.generate_button.place(x=20, y=140, width=200)  # Added width

        # Image display area
        self.image_frame = ttk.Label(master)
        self.image_frame.place(x=300, y=180)  # Specified position and 

    def generate_image(self):

        self.generate_button.config(state="disabled")

        # Start the generating popup and the image generation in a separate thread
        self.popup = GeneratingPopup(self.master)
        threading.Thread(target=self.run_image_generation, daemon=True).start()

    def run_image_generation(self):
        prompt = self.prompt_entry.get()
        resolution = self.resolution_var.get()
        guidance_scale = self.guidance_scale_slider.get()
        base_filename = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

        generator = image_generator(
            base_filename=base_filename,
            amount=1,
            prompt=prompt,
            resolution=resolution,
            guidance_scale=guidance_scale
        )

        for generated in generator:
            self.display_image(generated['filename'])
        
        # Close the popup and re-enable the generate button
        self.popup.close()
        self.generate_button.config(state="normal")

    def display_image(self, path):
        img = Image.open(path)
        img.thumbnail((500, 500), Image.LANCZOS)  # Resize to fit within the display area, maintaining aspect ratio
        self.photo = ImageTk.PhotoImage(img)  # This needs to be stored as an instance attribute

        self.image_canvas.delete("all")  # Clear any existing content on the canvas
        self.image_canvas.create_image(250, 250, image=self.photo, anchor="center")

        self.current_image_path = path  # Update the current image path for opening functionality 

    def open_image(self, event=None):
        if self.current_image_path:  # Check if there is an image path set
            if platform.system() == "Windows":
                os.startfile(self.current_image_path)  # Opens the file in the default app on Windows
            else:
                opener = "open" if platform.system() == "Darwin" else "xdg-open"  # For macOS, use "open"
                subprocess.run([opener, self.current_image_path])  # For Linux (and macOS), use subprocess to open

if __name__ == "__main__":
    root = tk.Tk()

    # Setup theme
    style = ttk.Style()
    print("Available themes: ", style.theme_names())
    chosen_theme = 'clam'  # Or another theme from the list
    style.theme_use(chosen_theme)

    gui = ImageGeneratorGUI(root)
    root.mainloop()