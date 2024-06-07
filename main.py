# -*- coding: utf-8 -*-

import re
from pathlib import Path

import site_parser
import file_downloader
import file_parser

url = "http://rsl.nstu.ru"
add_data_url = "/data"
add_pages_url = "/index/Metadata_page/"
add_video_url = "/video/"

with open("cookie.txt", "r") as cookie_file:
    cookie = cookie_file.readline().strip()
headers = {
    "Cookie": cookie
}

page_search_pattern = re.compile(r"/data/index/Metadata_page/(\d+)")

files_folder_name = "js"
target_folder_name = "data_sets"


def download_target_files() -> None:
    html_content = site_parser.fetch_html(url=url + add_data_url, headers=headers)
    pages = site_parser.parse_pages_html(html_content=html_content)
    max_page_number = site_parser.extract_max_page_number(hrefs=pages, pattern=page_search_pattern)

    file_names_list = []
    for page in range(1, max_page_number + 1):
        file_names_list.extend([f"{file_name}.js" for file_name
                                in site_parser.extract_file_names(url=url + add_data_url + add_pages_url + str(page),
                                                                  headers=headers)])
    file_downloader.download_files(list(set(file_names_list)), url=url + add_video_url, headers=headers)


def analyze_target_files() -> None:
    files_directory = Path(files_folder_name)
    # Перебираем все файлы в папке
    for file_path in files_directory.iterdir():
        if file_path.is_file():
            results = file_parser.parse_file(f"{files_folder_name}/{file_path.name}")
            with (open('data_sets/translations.txt', 'a', encoding='utf-8') as trans_file,
                  open('data_sets/combined_gloss.txt', 'a', encoding='utf-8') as gloss_file):
                for trans_text, combined_words in results.items():
                    if len(combined_words) == 0 or len(trans_text) == 0:
                        continue
                    trans_file.write(f"{trans_text}\n")
                    gloss_file.write(f"{combined_words}\n")


if __name__ == '__main__':
    # download_target_files()
    analyze_target_files()