from logging_settings import network_logger, info_logger
from playwright.async_api import async_playwright
import requests
import re
from random import random as uniform
import asyncio


async def get_url_data():
    url_data = []
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        page = await browser.new_page()

        def request_handler(request):
            request_info = f'{request.method} {request.url} \n'
            network_logger.info(request_info)
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
    """
    1. verify key in last_key.txt if there is one
    2. if not, find one through sending a request
    """

    key = None
    with open('last-key.txt', 'a+') as file:
        file.seek(0)
        line = file.readline()

    if line != '':
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
    key = loop.run_until_complete(get_url_data())

    info_logger.info(f'Found key {key[:10]}...')
    with open('last-key.txt', 'w') as file:
        file.write(key)

    return key


