import argparse

from key_finder import get_key
from generator import image_generator

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CLI Interface for Perchance\'s image generation.')
    parser.add_argument(
        '-f', '--filename',
        type=str,
        default='',
        help='Base filename for output images. Example: "new_picture"'
    )

    parser.add_argument(
        '-n', '--number',
        type=int,
        default=1,
        help='Number of images to generate.'
    )

    parser.add_argument(
        '-p', '--prompt',
        type=str,
        default='RANDOM',
        help='Prompt. Separate words with spaces. Random by default.'
    )

    parser.add_argument(
        '-ps', '--prompt-size',
        type=int,
        default=10,
        help='Number of words to include in prompt. Applies only if random.'
    )

    parser.add_argument(
        '-np', '--negative-prompt',
        type=str,
        default='nudity text',
        help='Negative prompt. Separate words with spaces. Includes "nudity" and "text" by default.'
    )

    parser.add_argument(
        '-st', '--style',
        type=str,
        default='RANDOM',
        help='Style. Random by default.'
    )

    parser.add_argument(
        '-gs', '--guidance-scale',
        type=int,
        default=7,
        help='Guidance scale for AI image generation.'
    )

    args = parser.parse_args()

    generator = image_generator(
        base_filename=args.filename,
        amount=args.number,
        prompt=args.prompt.replace(' ', ', '),
        prompt_size=args.prompt_size,
        negative_prompt=args.negative_prompt.replace(' ', ', '),
        style=args.style,
        guidance_scale=args.guidance_scale
    )

    for _ in generator:
        pass


    # generator = image_generator(
    #     base_filename= 'newgroup',
    #     amount=5,
    #     style='RANDOM',
    #     negative_prompt='nudity, text',
    #     guidance_scale = 7
    # )
    # for X in generator:
    #     pass



