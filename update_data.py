import json
import urllib.request
import xml.etree.ElementTree as ET
import re

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def get_nbrk_data():
    """
    1. Парсит базовую ставку и TONIA с главной страницы Нацбанка (nationalbank.kz/ru)
    2. Забирает официальный курс USD/KZT из RSS-фида (rates_all.xml)
    """
    nbrk_data = {
        "usd": "456.00",            # Резервное значение курса USD
        "base_rate": "16.25",       # Актуальная базовая ставка НБРК
        "tonia": "16.00",           # Актуальная TONIA
        "inflation_target": "5.00"  # Таргет по инфляции
    }

    # А. Парсинг базовой ставки и TONIA с главной страницы НБРК
    try:
        url_main = "https://www.nationalbank.kz/ru"
        req_main = urllib.request.Request(url_main, headers=HEADERS)
        with urllib.request.urlopen(req_main, timeout=12) as response:
            html = response.read().decode('utf-8')

            base_match = re.search(r'Базовая\s+ставка[^\d]*([\d[\.,]+)\s*%', html, re.IGNORECASE)
            if base_match:
                nbrk_data["base_rate"] = base_match.group(1).replace(',', '.')

            tonia_match = re.search(r'TONIA[^\d]*([\d[\.,]+)\s*%', html, re.IGNORECASE)
            if tonia_match:
                nbrk_data["tonia"] = tonia_match.group(1).replace(',', '.')

    except Exception as e:
        print("Ошибка загрузки главной страницы НБРК:", e)

    # Б. Парсинг официального курса USD из RSS-фида Нацбанка
    try:
        url_rss = "https://www.nationalbank.kz/rss/rates_all.xml"
        req_rss = urllib.request.Request(url_rss, headers=HEADERS)
        with urllib.request.urlopen(req_rss, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            for item in root.findall('.//item'):
                title = item.find('title')
                desc = item.find('description')
                if title is not None and title.text == 'USD' and desc is not None:
                    nbrk_data["usd"] = desc.text.replace(',', '.').strip()
                    break
    except Exception as e:
        print("Ошибка загрузки курса USD с НБРК:", e)

    return nbrk_data


def get_stat_gov_data():
    """
    Парсинг официальных данных из API Бюро национальной статистики РК (stat.gov.kz)
    """
    url = "https://stat.gov.kz/api/getMainIndicators/?lang=ru"
    req = urllib.request.Request(url, headers=HEADERS)

    stat_data = {
        "inflation_main": "9.3",
        "inflation_food": "8.5",
        "inflation_nonfood": "9.8",
        "inflation_services": "9.6",
        "unemployment_rate": "4.70",
        "employed_count": "9410000",
        "unemployed_count": "461000",
        "youth_unemployment": "3.1%"
    }

    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            raw_json = json.loads(response.read().decode('utf-8'))
            
            for item in raw_json:
                name = item.get('name', '').lower()
                val = str(item.get('val', '')).replace(',', '.').strip()

                if 'инфляция' in name or 'индекс потребительских цен' in name:
                    clean_val = re.sub(r'[^\d\.]', '', val)
                    if clean_val:
                        stat_data["inflation_main"] = clean_val

                elif 'безработиц' in name:
                    clean_val = re.sub(r'[^\d\.]', '', val)
                    if clean_val:
                        stat_data["unemployment_rate"] = clean_val

                elif 'занятое население' in name or 'численность занятых' in name:
                    clean_val = re.sub(r'[^\d]', '', val)
                    if clean_val:
                        stat_data["employed_count"] = clean_val

    except Exception as e:
        print("Ошибка загрузки данных stat.gov.kz:", e)

    return stat_data


def update_json():
    print("Запрос свежих данных из НБРК и stat.gov.kz...")
    nbrk = get_nbrk_data()
    stat = get_stat_gov_data()

    data = {
        "usd_kzt": nbrk["usd"],
        "base_rate": nbrk["base_rate"],
        "tonia_rate": nbrk["tonia"],
        "inflation_target": nbrk["inflation_target"],
        "inflation_main": stat["inflation_main"],
        "inflation_food": stat["inflation_food"],
        "inflation_nonfood": stat["inflation_nonfood"],
        "inflation_services": stat["inflation_services"],
        "unemployment_rate": stat["unemployment_rate"],
        "employed_count": stat["employed_count"],
        "unemployed_count": stat["unemployed_count"],
        "youth_unemployment": stat["youth_unemployment"]
    }

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\n--- Файл data.json успешно обновлен! ---")
    print(f"Курс USD/KZT (НБРК):  {nbrk['usd']} ₸")
    print(f"Базовая ставка НБРК: {nbrk['base_rate']}%")
    print(f"Ставка TONIA:         {nbrk['tonia']}%")
    print(f"Инфляция (stat.gov):  {stat['inflation_main']}%")


if __name__ == "__main__":
    update_json()
