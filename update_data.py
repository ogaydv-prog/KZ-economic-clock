import json
import urllib.request
import xml.etree.ElementTree as ET

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def get_nbrk_usd_rate():
    """ Скачивает официальный курс USD/KZT с Нацбанка, при сбое ставит 456.00 """
    url = "https://www.nationalbank.kz/rss/rates_all.xml"
    req = urllib.request.Request(url, headers=HEADERS)
    usd_rate = "456.00"

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            for item in root.findall('.//item'):
                title = item.find('title')
                desc = item.find('description')
                if title is not None and title.text == 'USD' and desc is not None:
                    usd_rate = desc.text.replace(',', '.').strip()
                    break
    except Exception as e:
        print("Ошибка загрузки курса USD, используем резерв 456.00:", e)

    return usd_rate

def update_json():
    usd_kzt = get_nbrk_usd_rate()

    # Жестко зафиксированные параметры
    data = {
        # Нацбанк РК
        "usd_kzt": usd_kzt,         # Скачанный курс или 456.00
        "base_rate": "16.25",       # Базовая ставка НБРК
        "tonia_rate": "16.06",      # Ставка TONIA
        "inflation_target": "5.00", # Таргет по инфляции

        # Бюро национальной статистики РК (stat.gov.kz)
        "inflation_main": "9.8",    # Годовая инфляция
        "inflation_food": "9.5",
        "inflation_nonfood": "11.4",
        "inflation_services": "8.7",
        "unemployment_rate": "4.70",
        "employed_count": "9410000",
        "unemployed_count": "461000",
        "youth_unemployment": "3.1%"
    }

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\n--- data.json успешно обновлен! ---")
    print(f"Базовая ставка: {data['base_rate']}%")
    print(f"Ставка TONIA:    {data['tonia_rate']}%")
    print(f"Курс USD/KZT:    {data['usd_kzt']} ₸")
    print(f"Инфляция:        {data['inflation_main']}%")

if __name__ == "__main__":
    update_json()
