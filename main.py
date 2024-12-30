import json
import requests
from bs4 import BeautifulSoup
import re
from utils import logger

cookies = {
    "__ddg8_": "VXfJHnDCsUzER0vK",
    "__ddg9_": "178.45.226.214",
    "__ddg10_": "1734118938",
    "__ddg1_": "TMP39U8apaanYfSU3SvX",
    "_ym_uid": "1734118940893690869",
    "_ym_d": "1734118940",
    "_ym_isad": "1",
    "tildauid": "1734118940970.648942",
    "tildasid": "1734118940970.232001",
    "previousUrl": "grdtrm.ru%2Fafisha",
}

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "cache-control": "max-age=0",
    # 'cookie': '__ddg8_=VXfJHnDCsUzER0vK; __ddg9_=178.45.226.214; __ddg10_=1734118938; __ddg1_=TMP39U8apaanYfSU3SvX; _ym_uid=1734118940893690869; _ym_d=1734118940; _ym_isad=1; tildauid=1734118940970.648942; tildasid=1734118940970.232001; previousUrl=grdtrm.ru%2Fafisha',
    "if-modified-since": "Fri, 13 Dec 2024 14:24:18 GMT",
    "if-none-match": '"15e7c4-62927960cf273-gzip"',
    "priority": "u=0, i",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}


def get_first_new():
    response = requests.get(
        "https://grdtrm.ru/afisha", cookies=cookies, headers=headers
    )

    soup = BeautifulSoup(response.text, "html5lib")

    artboards = soup.find_all(
        "div", class_="t396__artboard", attrs={"data-artboard-upscale": "grid"}
    )

    concerts_html = []
    concerts_data = []
    concerts = {}
    pattern = r"radario\.Widgets\.Event\(\{.*?\}\)"

    for artboard in artboards:
        if len(artboard) == 27 or len(artboard) == 29:
            for item in artboard:
                try:
                    text_for_check = item.find("div", class_="tn-atom").text
                    if re.search(pattern, text_for_check):
                        concerts_html.append(artboard)
                except:
                    pass

    for concert_html in concerts_html:
        concerts_data2 = []
        for item in concert_html:
            try:
                text_for_check = item.find("div", class_="tn-atom").text.strip()
                if (text_for_check):
                    if re.search(pattern, text_for_check):
                        pass
                    else: concerts_data2.append(text_for_check)
                try:
                    link_tag = item.find('div', class_='tn-atom').find('a')
                    href_value = link_tag['href']
                    concerts_data2.append(href_value)
                except:
                    pass
            except:
                pass
        concerts_data.append(concerts_data2)

    # for data in concerts_data:
    #     if len(data) == 7:
    #         concerts[data[0] + data[5]] = {
    #             'title': data[5],
    #             'date': f'{data[0]} {data[1]} {data[2]}',
    #             'link': data[6],
    #             'author': data[4],
    #             'info': data[3],
    #         }
    #     elif len(data) == 8:
    #         concerts[data[0] + data[8]] = {
    #             'title': f'{data[5]} {data[8]}',
    #             'date': f'{data[0]} {data[1]} {data[2]}',
    #             'link': data[6],
    #             'author': data[4],
    #             'info': data[3],
    #         }
            
    with open('concerts_data.json', 'w', encoding="UTF-8") as file:
        json.dump(concerts_data, file, indent=4, ensure_ascii=False)
    
    return concerts_data


def chek_news_update():
    logger.info('Получаю новые концерты')
    # Считываем старые данные
    try:
        with open('concerts_data.json', encoding="UTF-8") as file:
            old_concerts_data = json.load(file)
    except FileNotFoundError:
        old_concerts_data = []

    # Получаем новые данные
    new_concerts_data = get_first_new()

    # Проверка, что данные не None
    if new_concerts_data is None:
        print("Ошибка: новые данные не были получены.")
        return []

    # Сравниваем новые данные со старыми, фильтруем только новые
    new_entries = []

    for new_data in new_concerts_data:
        # Находим ссылку в новом массиве
        new_link = None
        for value in new_data:
            if isinstance(value, str) and value.startswith("https://grdtrm.ru/"):
                new_link = value
                break

        # Если ссылка не найдена, пропускаем этот элемент
        if new_link is None:
            continue

        # Получаем дату (первый элемент массива) и время (третий элемент массива)
        new_date_time = new_data[0]  # дата
        new_time = new_data[2]       # время

        # Сравниваем с данными из старого списка
        is_new = True  # Initialize `is_new` for each new_data
        for old_data in old_concerts_data:
            # Ищем ссылку в старом массиве
            old_link = None
            for value in old_data:
                if isinstance(value, str) and value.startswith("https://grdtrm.ru/"):
                    old_link = value
                    break

            if old_link is None:
                continue  # Пропускаем элемент без ссылки

            # Получаем дату (первый элемент массива) и время (третий элемент массива)
            old_date_time = old_data[0]  # дата
            old_time = old_data[2]       # время

            # Сначала проверяем ссылку
            if new_link != old_link:
                continue  # Если ссылка не совпадает, это новый концерт

            # Если ссылка совпала, проверяем дату
            if new_date_time != old_date_time:
                continue  # Если дата не совпала, это новый концерт

            # Если дата совпала, проверяем время
            if new_time != old_time:
                continue  # Если время не совпало, это новый концерт

            # Если все совпало, концерт уже существует
            is_new = False
            break

        if is_new:
            logger.info('Найден новый концерт!')
            logger.info(new_data)
            new_entries.append(new_data)

    # No need for `if is_new == False` since it's per-item logic
    if not new_entries:
        logger.info('Новых концертов не найдено')

    return new_entries


def main():
    new_entries = chek_news_update()
    if new_entries:
        print("Новые данные:", new_entries)
    else:
        print("Новых данных нет.")


if __name__ == "__main__":
    main()
