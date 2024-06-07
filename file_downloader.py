# -*- coding: utf-8 -*-
import asyncio
import re
from typing import List

import aiohttp


async def download_files(file_names_list: List[str], url: str, headers: dict) -> None:
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = [download_file(session, file_name, url) for file_name in file_names_list]
        await asyncio.gather(*tasks)


async def download_file(session: aiohttp.ClientSession, file_name: str, url: str) -> None:
    async with session.get(url + file_name) as response:
        js_content = await response.text()
        unicode_escaped_strings = re.findall(r'\\u[0-9A-Fa-f]{4}', js_content)

        for escaped_string in unicode_escaped_strings:
            decoded_string = decode_unicode_escapes(escaped_string)
            js_content = js_content.replace(escaped_string, decoded_string)

        with open(f"js/{file_name}", "w", encoding='utf-8') as file:
            file.write(js_content)


def decode_unicode_escapes(string: str) -> str:
    return string.encode('latin1').decode('unicode_escape')
