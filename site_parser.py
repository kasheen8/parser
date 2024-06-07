# -*- coding: utf-8 -*-

from typing import List

import requests
from bs4 import BeautifulSoup as Bs
import re

unnecessary_types_list = ["диалог", "интервью"]


def fetch_html(url: str, headers: dict) -> str:
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        return response.content.decode("utf-8")
    else:
        raise Exception(f"Failed to fetch the webpage. Status code: {response.status_code}")


def parse_pages_html(html_content: str) -> List[str]:
    soup = Bs(html_content, features="html.parser")
    pages = soup.find_all("a")
    return [a.get("href") for a in pages if a.get("href")]


def extract_max_page_number(hrefs: List[str], pattern: re.Pattern) -> int:
    return max([int(match.group(1)) for href in hrefs for match in [pattern.search(href)] if match])


def extract_file_names(url: str, headers: dict) -> List[str]:
    html_content = fetch_html(url=url, headers=headers)
    soup = Bs(html_content, features="html.parser")
    tr_tags = soup.find_all("tr", class_=["odd", "even"])

    files_name_list = []
    for tr in tr_tags:
        td_tags = tr.find_all_next("td")
        if td_tags[1].text not in unnecessary_types_list:
            files_name_list.append(td_tags[0].text)
    return files_name_list
