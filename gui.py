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

def image_generator(base_filename='', amount=1, prompt='RANDOM', prompt_size=10, negative_prompt='', style='no style', resolution='512x768', guidance_scale=7):
    create_url = 'https://image-generation.perchance.org/api/generate'
    download_url = 'https://image-generation.perchance.org/api/downloadTemporaryImage'

    if prompt == 'RANDOM':
        wordlist = MyWordlist()
        prompt_base = wordlist.get_prompt(prompt_size)
    else:
        prompt_base = prompt

    if style == 'RANDOM':
        # Pick a random style from the list excluding the first 'NONE' option
        _, style_description = random.choice(styles[1:])
    else:
        # Find the style description by the style name; default to empty string if not found
        style_description = next((desc for name, desc in styles if name == style), "")

    # Correctly use style_description for the prompt query
    prompt_query = quote('\'' + prompt_base + ', ' + style_description)
    negative_prompt_query = quote('\'' + negative_prompt)  # Assuming negative_prompt is used differently

    # Logging information
    info_logger(f'Selected prompt: {prompt_base}, Style: {style}')
    info_logger(f'Encoded prompt: {prompt_query}, Encoded negative prompt: {negative_prompt_query}')

 

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

        # Log the request parameters being sent
        info_logger(f'Sending parameters: {create_params}')

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

        filename = os.path.join(generated_dir, f'{base_filename}{idx}.jpeg' if base_filename else f'{image_id}.jpeg')
        with open(filename, 'wb') as file:
            file.write(download_response.content)

        info_logger(f'Created picture {idx}/{amount} ({filename})')
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

styles = [
    ("NONE", ""),
    ("ANIME", "anime atmospheric, atmospheric anime, anime character; full body art, digital anime art, beautiful anime art style, anime picture, anime arts, beautiful anime style, digital advanced anime art, anime painting, anime artwork, beautiful anime art, detailed digital anime art, anime epic artwork"),
    ("CARTOON", "cartoon style, children's cartoons shown on TV networks, playful and entertaining cartoons, bold outlines, bright colors, and exaggerated features, oversized eyes, face and feature, playful energy to a colorful world"),
    ("CINEMATIC_RENDER", "detailed hands, realistic skin, focused subject, cinematic, breathtaking colors, CGSociety, computer rendering, by Mike Winkelmann, UHD, rendered in Cinema4D, surface modeling, 8k, render Octane, inspired by Beksinski"),
    ("CYBERPUNK", "synthwave image, (neotokyo), dreamy colorful cyberpunk colors, cyberpunk Blade Runner art, retrofuturism, cyberpunk, beautiful cyberpunk style, CGSociety 9"),
    ("DISNEY", "disney animation, disney splash art, disney color palette, disney renaissance film, disney pixar movie still, disney art style, disney concept art :: nixri, realistic, cinematic composition, wonderful compositions, pixar, disney concept artists, 2d character design"),
    ("DYSTOPIAN", "cifi world, cybernetic civilizations, peter gric and dan mumford, brutalist dark futuristic, dystopian brutalist atmosphere, dark dystopian world, cinematic 8k, end of the world, doomsday"),
    ("GRAFFITI", "graffiti background, colorful graffiti, graffiti art style, colorful mural, ravi supa, symbolic mural, juxtapoz, pablo picasso, street art"),
    ("GTA", "gta iv art style, gta art, gta loading screen art, gta chinatown art style, gta 5 loading screen poster, grand theft auto 5, grand theft auto video game"),
    ("HIGH_QUALITY", "High Quality, 8K, Cinematic Lighting, Stunning background, focused subject, high detail, realistic, incredible 16k resolution produced in Unreal Engine 5 and Octane Render for background, sunshafts"),
    ("MAGICAL", "magical, magical world, magical realism, magical atmosphere, in a magical world, magical fantasy art"),
    ("NEON", "neon art style, night time dark with neon colors, blue neon lighting, violet and aqua neon lights, blacklight neon colors, rococo cyber neon lighting"),
    ("ORIGAMI", "polygonal art, layered paper art, paper origami, wonderful compositions, folded geometry, paper craft, made from paper"),
    ("PAINTING", "atmospheric dreamscape painting, by Mac Conner, vibrant gouache painting scenery, vibrant painting, vivid painting, a beautiful painting, dream scenery art, Instagram art, psychedelic painting, lo-fi art, bright art"),
    ("PASTEL_DREAM", "pastel colors, dreamy atmosphere, soft and gentle, whimsical, fantasy world, delicate brushstrokes, light and airy, tranquil, serene, peaceful, nostalgic"),
    ("PHOTO_REALISTIC", "realistic image, realistic shadows, realistic dramatic lighting, Photo Realistic, 4k, 8k, high resolution, highly detailed, ultra-detailed image, subject focussed, natural beauty, extremely detailed realistic background"),
    ("PICASO", "painting, by Pablo Picasso, cubism"),
    ("PIXEL", "pixel art, pixelated, pixel-style, 8-bit style, pixel game, pixel"),
    ("POP_ART", "Pop art, Roy Lichtenstein, Andy Warhol, pop art style, comic book, pop"),
    ("RENAISSANCE", "Renaissance period, neo-classical painting, Italian Renaissance workshop, pittura metafisica, Raphael high Renaissance, ancient Roman painting, Michelangelo painting, Leonardo da Vinci, Italian Renaissance architecture"),
    ("ROCOCO", "François Boucher oil painting, rococo style, rococo lifestyle, a Flemish Baroque, by Karel Dujardin, vintage look, cinematic hazy lighting"),
    ("THE_1990s", "Technology - Desktop computers, bulky CRT televisions, portable CD players, the early internet, or videogame consoles like the Game Boy or PlayStation, Fashion - High-waisted jeans, bright neon colors, plaid flannel shirts, snapback hats, or the grunge look, Entertainment - Influential 90s movies or TV series like Friends or The Matrix, popular toys like Beanie Babies or Tamagotchis, or recognizable music like Britney Spears or Nirvana, Social Events - Major events like the fall of the Berlin Wall, the Y2K scare, or the rise of hip-hop culture"),
    ("TROPICAL", "tropical, tropical landscape, tropical beach, paradise, tropical paradise, vibrant colors"),
    ("URBAN_GRAFFITI", "urban graffiti art, street culture, vibrant tags and murals, rebellious expression, urban decay"),
    ("VAN_GOGH", "painting, by Van Gogh"),
    ("VICTORIAN", "Victorian, 19th century, period piece, antique, vintage, historical"),
    ("VIBRANT", "Psychedelic, watercolor spots, vibrant color scheme, highly detailed, romanticism style, cinematic, ArtStation, Greg Rutkowski"),
    ("WESTERN", "western, wild west, cowboy, American frontier, rustic, vintage")
]

# GUI Application
class ImageGeneratorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Image Generator")
        master.geometry("950x600")  # Adjusted window size as needed

        self.image_positions = []  # To store the positions and paths of images
        self.generated_images = []  # To store generated image paths
        self.photo = []  # To keep references to PhotoImage objects

        # Initialize the canvas
        self.image_canvas = tk.Canvas(master, width=500, height=500)
        self.image_canvas.place(x=350, y=50)
        self.image_canvas.bind('<Button-1>', self.on_canvas_click)

        # Prompt input
        self.prompt_label = ttk.Label(master, text="Prompt:")
        self.prompt_label.place(x=20, y=20)
        self.prompt_entry = ttk.Entry(master, width=200)
        self.prompt_entry.place(x=120, y=20, width=800)  # Added width

        # Resolution dropdown
        self.resolution_label = ttk.Label(master, text="Resolution:")
        self.resolution_label.place(x=20, y=60)
        self.resolution_var = tk.StringVar(master)
        resolutions = ["512x512", "512x768", "512x768", "768x512"]
        self.resolution_var.set(resolutions[0])  # default value
        self.resolution_dropdown = ttk.OptionMenu(master, self.resolution_var, *resolutions)
        self.resolution_dropdown.place(x=120, y=60, width=200)  # Added width

        # Guidance scale slider
        self.guidance_scale_label = ttk.Label(master, text="Guidance:")
        self.guidance_scale_label.place(x=20, y=100)
        self.guidance_scale_slider = ttk.Scale(master, from_=1, to_=20, orient='horizontal', value=7)
        self.guidance_scale_slider.place(x=120, y=100, width=200)  # Added width

        # Style dropdown
        # Correctly create a list of style names for the dropdown
        style_names = [name for name, _ in styles]
        self.style_var = tk.StringVar(master)
        self.style_var.set(style_names[0])  # Set default value to the first style name


        # Initialize the style dropdown with the list of style names
        self.style__label = ttk.Label(master, text="Styles:")
        self.style__label.place(x=20, y=140)
        self.style_dropdown = ttk.OptionMenu(master, self.style_var, style_names[0], *style_names)
        self.style_dropdown.place(x=120, y=140, width=200)

        # Initialize the number of images dropdown
        self.number_of_images_label = ttk.Label(master, text="Num of images:")
        self.number_of_images_label.place(x=20, y=185)
        self.number_of_images_var = tk.StringVar(master)
        number_of_images_options = ["1", "3", "6"]
        self.number_of_images_var.set(number_of_images_options[0])  # default value 1
        self.number_of_images_dropdown = ttk.OptionMenu(
            master, self.number_of_images_var, *number_of_images_options
        )
        self.number_of_images_dropdown.place(x=120, y=180, width=200)

        # Generate button
        self.generate_button = ttk.Button(master, text="Generate", command=self.generate_image)
        self.generate_button.place(x=50, y=280, width=200)  # Added width

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

        selected_style = next((description for name, description in styles if name == self.style_var.get()), "")
        prompt += f', {selected_style}' if selected_style else ''

        # Prepare for new generation
        self.generated_images.clear()
        self.photo.clear()

        amount = int(self.number_of_images_var.get())  # Update the amount based on user selection
        generator = image_generator(
            base_filename=base_filename,
            amount=amount,  # Use the selected amount
            prompt=prompt,
            resolution=resolution,
            guidance_scale=guidance_scale
        )

        # Collect generated images
        for generated in generator:
            self.generated_images.append(generated['filename'])

        self.display_images()  # Update the canvas with new images

        # Close the popup and re-enable the generate button
        self.popup.close()
        self.generate_button.config(state="normal")

    def display_images(self):
        self.image_canvas.delete("all")  # Clear any existing content on the canvas
        self.image_positions.clear()  # Clear previous positions
        self.photo.clear()  # Clear previous photo references to prevent garbage collection

        canvas_width = self.image_canvas.winfo_width()
        canvas_height = self.image_canvas.winfo_height()

        # Check how many images we need to display
        number_of_images = int(self.number_of_images_var.get())
        if number_of_images == 1:
            # If there's only one image, use the whole canvas
            img = Image.open(self.generated_images[0])
            img.thumbnail((canvas_width, canvas_height), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.image_canvas.create_image(
                canvas_width // 2, canvas_height // 2, image=photo
            )
            self.image_positions.append(
                ((canvas_width // 2 - img.size[0] // 2, canvas_height // 2 - img.size[1] // 2, img.size[0], img.size[1]), self.generated_images[0])
            )
            self.photo.append(photo)
        else:
            # Otherwise, we're using the grid layout
            columns = 3
            rows = (number_of_images - 1) // columns + 1
            img_width, img_height = canvas_width // columns, canvas_height // rows

            for idx, img_path in enumerate(self.generated_images):
                img = Image.open(img_path)
                img.thumbnail((img_width, img_height), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)

                # Calculate position
                column = idx % columns
                row = idx // columns
                x = column * img_width + img_width // 2
                y = row * img_height + img_height // 2

                # Display image on canvas
                self.image_canvas.create_image(x, y, image=photo)
                self.image_positions.append(((x, y, img.size[0], img.size[1]), img_path))
                self.photo.append(photo)

    def on_canvas_click(self, event):
        # Determine which image was clicked
        for position, img_path in self.image_positions:
            x, y, width, height = position
            if x - width // 2 < event.x < x + width // 2 and y - height // 2 < event.y < y + height // 2:
                self.open_image(img_path)
                break

    def open_image(self, img_path=None):
        if img_path:  # Check if a specific path is provided
            if platform.system() == "Windows":
                os.startfile(img_path)
            else:
                opener = "open" if platform.system() == "Darwin" else "xdg-open"
                subprocess.run([opener, img_path])

# If any tkinter operations throw an error outside of the main thread, show an error dialog
def show_error(err):
    messagebox.showerror("Error", str(err))

if __name__ == "__main__":
    root = tk.Tk()

    # Setup theme
    style = ttk.Style()
    print("Available themes: ", style.theme_names())
    chosen_theme = 'clam'  # Or another theme from the list
    style.theme_use(chosen_theme)

    gui = ImageGeneratorGUI(root)
    root.mainloop()