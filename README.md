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

## usage Guide
```
usage: python gui.py

Then type your user input, select resolution, guidance scale and prefered style and his generate. really easy to use.

```
