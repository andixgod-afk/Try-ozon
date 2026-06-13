import requests
import csv
import re

API_KEY = "Q50U3MU0682PXVFSGQPT85HCWY2ILY3236OPSC1RVZEVDQKDGAF0Z77EAJEINXQM3UE1JVSZMJJWAVV4"  # <-- ВСТАВЬ СЮДА
SEARCH_QUERY = "Смартфоны"

url = f"https://www.ozon.ru/search/?sorting=price_asc&text={SEARCH_QUERY.replace(' ', '+')}"

print(f">>> Запрашиваю через ScrapingBee: {url}")

response = requests.get(
    "https://app.scrapingbee.com/api/v1/",
    params={
        "api_key": API_KEY,
        "url": url,
        "render_js": True,
        "wait": 5000,
        "country_code": "ru"
    },
    timeout=120
)

print(f">>> Статус: {response.status_code}")
print(f">>> Размер: {len(response.text)} символов")

html = response.text

# Сохраняем HTML для отладки
with open("debug_page.html", "w", encoding="utf-8") as f:
    f.write(html)

# Ищем товары
products = []

# Ищем все ссылки на товары
product_links = re.findall(r'href="(/product/[^"]+)"', html)
product_links = list(set(product_links))  # убираем дубли

print(f">>> Найдено ссылок на товары: {len(product_links)}")

# Ищем цены
prices = re.findall(r'(\d[\d\s]*)\s*₽', html)
print(f">>> Найдено цен: {len(prices)}")

# Собираем всё вместе
for i, link in enumerate(product_links[:40]):
    full_link = f"https://www.ozon.ru{link}"
    price = prices[i].replace(" ", "") if i < len(prices) else "0"
    
    products.append({
        "Название": f"Товар {i+1}",
        "Цена (руб)": price,
        "Старая цена (руб)": "",
        "Ссылка": full_link
    })

if products:
    filename = f"ozon_{SEARCH_QUERY.replace(' ', '_')}_low_price.csv"
    with open(filename, mode='w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["Название", "Цена (руб)", "Старая цена (руб)", "Ссылка"], delimiter=';')
        writer.writeheader()
        writer.writerows(products)
    print(f"\n>>> ГОТОВО! Сохранено {len(products)} товаров в: {filename}")
else:
    print(">>> Ничего не собрано")
