import json
import urllib.request
import xml.etree.ElementTree as ET

def get_nbrk_rate():
    url = "https://www.nationalbank.kz/rss/rates_all.xml"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            for item in root.findall('.//item'):
                if item.find('title').text == 'USD':
                    return item.find('description').text
    except Exception as e:
        print("Ошибка загрузки курса Нацбанка:", e)
    return "464.77"

def update_json():
    usd_rate = get_nbrk_rate()
    
    data = {
        "usd_kzt": usd_rate,
        "base_rate": "16.75%",
        "tonia_rate": "16.50%",
        "inflation_main": "10.20",
        "inflation_food": "10.1%",
        "inflation_nonfood": "11.7%",
        "inflation_services": "9.2%",
        "unemployment_rate": "4.50",
        "employed_count": "9410000",
        "unemployed_count": "445000",
        "youth_unemployment": "3.1%"
    }

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    update_json()
