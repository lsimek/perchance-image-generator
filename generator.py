from wordlist import MyWordlist
from key_finder import get_key
import random
import requests
from styles import styles
from logging_settings import network_logger, info_logger
from urllib.parse import quote, urlencode
from time import sleep
from os.path import exists
from os import makedirs

def encode(prompt):
    replacement_dict = {
        ' ': r'%20',
        ',': r'%2C',
    }
    translation_table = str.maketrans(replacement_dict)
    output_string = r'%27' + prompt.translate(translation_table)
    return output_string


def image_generator(
        base_filename='',
        amount=1,
        prompt='RANDOM',
        prompt_size=10,
        negative_prompt='',
        style='RANDOM',
        resolution='512x768',
        guidance_scale=7
):
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
        style_pair = styles[style_choice]
    else:
        try:
            style_choice = style
            style_pair = styles[style_choice]
        except KeyError:
            raise Exception(f'Style choice {style} was not recognized. Check styles.py.')

    prompt_style = styles[style_choice][0]
    negative_prompt_style = styles[style_choice][1]

    prompt_query = quote('\'' + prompt_base + ', ' + prompt_style)
    negative_prompt_query = quote('\'' + negative_prompt + ', ' + negative_prompt_style)
    info_logger.info(f'Selected prompt {prompt_base} and style {style_choice}')

    for idx in range(1, amount+1):
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
                info_logger.info('Waiting for previous request to finish...')
                sleep(8)
                create_response = requests.get(create_url, params=create_params_str)

        download_params = {
            'imageId': image_id
        }
        download_response = requests.get(download_url, params=download_params)

        generated_dir = 'generated-pictures'
        if not exists(generated_dir):
            makedirs(generated_dir)
        filename = f'{generated_dir}/{base_filename}{idx}.jpeg' if base_filename else f'{generated_dir}/{image_id}.jpeg'
        with open(filename, 'wb') as file:
            file.write(download_response.content)

        info_logger.info(f'Created picture {idx}/{amount} ({filename=})')
        yield {
            'filename': filename,
            'prompt': prompt_base,
            'negative_prompt': negative_prompt
        }
