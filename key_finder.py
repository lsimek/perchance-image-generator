from logging_settings import network_logger, info_logger
from playwright.async_api import async_playwright
import requests
import re
from random import random as uniform
from time import sleep
import asyncio


async def get_url_data():
    url_data = []
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=False)
        page = await browser.new_page()

        def request_handler(request):
            request_info = f'{request.method} {request.url} \n'
            network_logger.log(5, request_info)
            url_data.append(request.url)

        page.on("request", request_handler)  # capture traffic

        await page.goto('https://perchance.org/ai-text-to-image-generator')

        iframe_element = await page.query_selector('xpath=//iframe[@src]')
        frame = await iframe_element.content_frame()
        await frame.click('xpath=//button[@id="generateButtonEl"]')
        sleep(10)

        await browser.close()

    return url_data


def get_key():
    """
    1. verify key in last_key.txt if there is one
    2. if not, find one through sending a request
    """

    key = None
    with open('last_key.txt', 'r') as file:
        line = file.readline()

    if line is not None:
        verification_url = 'https://image-generation.perchance.org/api/checkVerificationStatus'
        user_key = line
        cache_bust = uniform()
        verification_params = {
            'userKey': user_key,
            '__cacheBust': cache_bust
        }

        response = requests.get(verification_url, params=verification_params)
        if 'not_verified' not in response.text:
            key = line

    if key is not None:
        info_logger.info(f'Found working key {key[:10]}... in file.')
        return key

    info_logger.info(f'Key no longer valid. Looking for a new key...')
    loop = asyncio.get_event_loop()
    url_data = loop.run_until_complete(get_url_data())

    url_data = [url for url in url_data if 'generate?prompt' in url]
    all_text = ''.join(url_data)
    pattern = r'userKey=([a-f\d]{64})'
    keys = re.findall(pattern, all_text)

    key = keys[0]
    info_logger.info(f'Found key {key[:10]}...')
    with open('last_key.txt', 'w') as file:
        file.write(key)

    return key


