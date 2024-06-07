# -*- coding: utf-8 -*-

import re
from typing import List

import requests


def download_files(file_names_list: List[str], url: str, headers: dict) -> None:
    for file_name in file_names_list:
        download_file(file_name, url, headers)


def download_file(file_name: str, url: str, headers: dict) -> None:
    response2 = requests.get(url=url + file_name, headers=headers)
    js_content = response2.content.decode('utf-8')

    unicode_escaped_strings = re.findall(r'\\u[0-9A-Fa-f]{4}', js_content)

    for escaped_string in unicode_escaped_strings:
        decoded_string = decode_unicode_escapes(escaped_string)
        js_content = js_content.replace(escaped_string, decoded_string)

    with open(f"js/{file_name}", "w", encoding='utf-8') as file:
        file.write(js_content)


def decode_unicode_escapes(string: str) -> str:
    return string.encode('latin1').decode('unicode_escape')
