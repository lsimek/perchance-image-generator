# perchance-image-generator
perchange.org offers various free generators, but has no API. This is confirmed [here](https://perchance.org/diy-perchance-api) where a DIY solution is suggested with a Node.js server. This DIY API is Python-based and dedicated specificallyto the AI image generator.

Use these capabilities modestly and with good intentions, without putting excessive strain on the website. 

This repository is not affiliated with perchance.org.

## Dependencies
Check `requirements.txt`. 

It is encouraged to write your own `wordlist.py` wordlist and styles in `styles.py` to creatively explore the many available possibilities. 10 words and 1 style are required and already available.

## About
This project enables automatic usage of [Perchance's free AI image generator](https://perchance.org/ai-text-to-image-generator), also enabling some features not available through the GUI. The generator `generator.image_generator` can itself be used, but user-friendly access through a CLI is given by `main.py`. Example call
```
python main.py -f newimage -n 3 --style traditional-japanese
```
It is recommended to create an alias in `~/.bash_aliases` or equivalent, e.g.
```
alias image-generator='python ~/perchance-image-generator/main.py'
```

## CLI Guide
```
usage: main.py [-h] [-f FILENAME] [-n NUMBER] [-p PROMPT] [-ps PROMPT_SIZE] [-np NEGATIVE_PROMPT] [-st STYLE] [-r RESOLUTION] [-gs GUIDANCE_SCALE]

CLI Interface for Perchance's image generation.

options:
  -h, --help            show this help message and exit
  -f FILENAME, --filename FILENAME
                        Base filename for output images. Example: "new_picture".
  -n NUMBER, --number NUMBER
                        Number of images to generate.
  -p PROMPT, --prompt PROMPT
                        Prompt. Separate words with commas and spaces. Random by default.
  -ps PROMPT_SIZE, --prompt-size PROMPT_SIZE
                        Number of words to include in prompt. Applies only if random.
  -np NEGATIVE_PROMPT, --negative-prompt NEGATIVE_PROMPT
                        Negative prompt. Separate words with spaces. Includes "nudity" and "text" by default.
  -st STYLE, --style STYLE
                        Style. Random by default.
  -r RESOLUTION, --resolution RESOLUTION
                        Resolution. Example "512x768".
  -gs GUIDANCE_SCALE, --guidance-scale GUIDANCE_SCALE
                        Guidance scale for AI image generation. Float from 1 to 20.

```
