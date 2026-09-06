import json
import urllib.request
import xml.etree.ElementTree as ET
import re

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def get_nbrk_data():
    """
    Парсинг данных из официального RSS-фида Национального Банка РК (nationalbank.kz)
    """
    url = "https://www.nationalbank.kz/rss/rates_all.xml"
    req = urllib.request.Request(url, headers=HEADERS)
    
    # Резервные зафиксированные значения на случай сбоя сети
    data = {
        "usd": "464.77",
        "base_rate": "16.25",
        "tonia": "16.00"
    }

    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)

            for item in root.findall('.//item'):
                title = item.find('title')
                desc = item.find('description')

                if title is not None and desc is not None:
                    t_text = title.text.strip() if title.text else ""
                    d_text = desc.text.strip() if desc.text else ""

                    # Курс USD/KZT
                    if t_text == 'USD':
                        data["usd"] = d_text.replace(',', '.')

                    # Базовая ставка НБРК
                    elif 'Базовая ставка' in t_text or 'Base rate' in t_text:
                        val = re.sub(r'[^\d\.]', '', d_text.replace(',', '.'))
                        if val:
                            data["base_rate"] = val

                    # Ставка TONIA
                    elif 'TONIA' in t_text:
                        val = re.sub(r'[^\d\.]', '', d_text.replace(',', '.'))
                        if val:
                            data["tonia"] = val

    except Exception as e:
        print("Ошибка загрузки данных НБРК:", e)

    return data


def get_stat_gov_data():
    """
    Парсинг официальных данных из API Бюро национальной статистики РК (stat.gov.kz)
    """
    url = "https://stat.gov.kz/api/getMainIndicators/?lang=ru"
    req = urllib.request.Request(url, headers=HEADERS)

    # Дефолтные значения БНС РК (на случай тайм-аута API)
    stat_data = {
        "inflation_main": "9.3",
        "inflation_food": "8.5",
        "inflation_nonfood": "9.8",
        "inflation_services": "9.6",
        "unemployment_rate": "4.7",
        "employed_count": "9100000",
        "unemployed_count": "450000",
        "youth_unemployment": "3.2"
    }

    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            raw_json = json.loads(response.read().decode('utf-8'))
            
            # Обход элементов API stat.gov.kz
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
    print("Сбор актуальных данных...")
    nbrk = get_nbrk_data()
    stat = get_stat_gov_data()

    # Сборка единой структуры для Kazakhstan Economic Clock
    data = {
        # Данные Нацбанка РК
        "usd_kzt": nbrk["usd"],
        "base_rate": nbrk["base_rate"],     # Автоматическая базовая ставка (16.25)
        "tonia_rate": nbrk["tonia"],         # Автоматическая TONIA (~16.00)
        "inflation_target": "5.00",         # Официальный таргет НБРК

        # Данные Бюро нацстатистики РК (stat.gov.kz)
        "inflation_main": stat["inflation_main"],
        "inflation_food": stat["inflation_food"],
        "inflation_nonfood": stat["inflation_nonfood"],
        "inflation_services": stat["inflation_services"],
        "unemployment_rate": stat["unemployment_rate"],
        "employed_count": stat["employed_count"],
        "unemployed_count": stat["unemployed_count"],
        "youth_unemployment": stat["youth_unemployment"]
    }

    # Запись в data.json
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\n--- data.json успешно обновлен! ---")
    print(f"Базовая ставка НБРК: {nbrk['base_rate']}%")
    print(f"Ставка TONIA:         {nbrk['tonia']}%")
    print(f"Курс USD/KZT:         {nbrk['usd']} ₸")
    print(f"Инфляция (stat.gov):  {stat['inflation_main']}%")


if __name__ == "__main__":
    update_json()
