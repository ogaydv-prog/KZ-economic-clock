import json
import urllib.request
import xml.etree.ElementTree as ET

def get_nbrk_data():
    # Запрос курса USD к KZT из API Национального Банка РК
    url = "https://www.nationalbank.kz/rss/rates_all.xml"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            for item in root.findall('.//item'):
                if item.find('title').text == 'USD':
                    return item.find('description').text
    except Exception as e:
        print("Error fetching NBRK rates:", e)
    return "475.00"

# Формируем структуру данных
data = {
    "usd_kzt": get_nbrk_data(),
    "base_rate": "14.25%",
    "tonia_rate": "13.75%",
    "inflation_main": "8.40",
    "inflation_food": "8.1%",
    "inflation_nonfood": "8.6%",
    "inflation_services": "8.7%",
    "unemployment_rate": "4.70",
    "employed_count": "9410000",
    "unemployed_count": "461000",
    "youth_unemployment": "3.1%"
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("data.json successfully updated!")
