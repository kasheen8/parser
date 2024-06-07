import json
import re


# Прочитать данные из файла JavaScript
def parse_file(file_name: str) -> dict:
    with open(file_name, "r") as file:
        js_data = file.read()

    # Используем регулярное выражение для извлечения нужной части данных из строки
    tiers_pattern = r"document\.elanData\.tiers\s*=\s*(\[.*?\]);"
    tiers_match = re.search(tiers_pattern, js_data, re.DOTALL)

    words_pattern = r"document\.elanData\.words\s*=\s*(\[.*?\]);"
    words_match = re.search(words_pattern, js_data, re.DOTALL)

    # Получаем данные из файла
    try:
        tiers = json.loads(tiers_match.group(1))
    except AttributeError:
        print(f"{type(tiers_match)} object has no attribute 'group'")
        return {}

    right_hand_gloss, left_hand_gloss, translation = tiers[0], tiers[1], tiers[2]
    words = json.loads(words_match.group(1))

    # Создание структуры для хранения данных глосс
    glosses = {}
    for ref in right_hand_gloss['ref']:
        glosses[ref] = {'right': words[ref][0], 'right_start': words[ref][1], 'right_end': words[ref][2]}

    for ref in left_hand_gloss['ref']:
        if ref in glosses:
            glosses[ref]['left'] = words[ref][0]
            glosses[ref]['left_start'] = words[ref][1]
            glosses[ref]['left_end'] = words[ref][2]
        else:
            glosses[ref] = {'left': words[ref][0], 'left_start': words[ref][1], 'left_end': words[ref][2]}

    # Фильтрация и обработка данных
    filtered_glosses = []
    for ref, gloss_data in glosses.items():
        right_word = process_word(gloss_data.get('right', ''))
        left_word = process_word(gloss_data.get('left', ''))

        if right_word and left_word and right_word != left_word:
            continue

        filtered_glosses.append({
            'word': right_word if right_word else left_word,
            'start': gloss_data.get('right_start', gloss_data.get('left_start')),
            'end': gloss_data.get('right_end', gloss_data.get('left_end'))
        })

    # Сопоставление с переводом
    translations = {}
    for ref in translation['ref']:
        translations[ref] = {'text': words[ref][0], 'start': words[ref][1], 'end': words[ref][2]}

    # Объединение результатов
    results = {}
    for trans_ref, trans_data in translations.items():
        trans_text = trans_data['text']
        trans_start = trans_data['start']
        trans_end = trans_data['end']
        trans_words = []
        for gloss in filtered_glosses:
            if gloss['start'] >= trans_start and gloss['end'] <= trans_end:
                trans_words.append(gloss['word'])
        results[trans_text.replace("\n", "").strip()] = remove_consecutive_duplicates(" ".join(trans_words).replace("  ", " ").replace("\n", "").strip())

    return results


# Функция для обработки специальных символов, лишних пробелов и прочих помех в строках
def process_word(word: str) -> str:
    word = word.replace(":PAST", "").replace(":PRES", "").replace(":FUT", "").replace(":DU", "")
    word = word.replace(":1PS", "").replace("CLF:", "").replace("PRTCL1", "").replace(":NEG", "")
    word = word.replace("PRTCL2", "").replace("INDX", "").replace(":REC", "").replace("IMP", "")
    word = word.replace(":Du", "").replace("PRTCL", "").replace(":LOC", "").replace("CL:", "")
    word = word.replace(":Pl", "").replace(":ITER", "").replace("CFL:", "").replace(":PST", "")
    word = word.replace("1PS:", "").replace(":ORD", "").replace(":PRT", "").replace(":PL", "")
    word = word.replace("POSS", "").replace("ХЕЗ", "")
    word = word.replace("#", "")
    word = word.replace("^", " ")
    word = word.rstrip("-=").strip()
    if "-" in word and len(word.split('-')) == 2 and all(len(part) == 1 for part in word.split('-')):
        word = word.replace('-', ' ').upper()
    return word


def remove_consecutive_duplicates(text: str) -> str:
    words = text.split()  # Разбиваем строку на слова
    result = []  # Список для хранения результата

    # Перебираем слова, добавляя в результат только те, которые не повторяют предыдущее слово
    for i, word in enumerate(words):
        if i == 0 or word != words[i - 1]:
            result.append(word)

    return ' '.join(result)
