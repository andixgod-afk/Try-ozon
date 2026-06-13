import asyncio
from playwright.async_api import async_playwright
import csv
import re
import json

async def parse_ozon():
    SEARCH_QUERY = "Смартфоны"  # <-- ТВОЙ ЗАПРОС
    
    # Используем мобильную версию — её проще парсить
    url = f"https://www.ozon.ru/search/?sorting=price_asc&text={SEARCH_QUERY.replace(' ', '+')}"
    
    print(f">>> Открываю: {url}")
    
    async with async_playwright() as p:
        # Запускаем с мобильным viewport
        browser = await p.chromium.launch(headless=True, args=[
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-blink-features=AutomationControlled'
        ])
        
        context = await browser.new_context(
            viewport={"width": 430, "height": 932},  # iPhone 15 Pro
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            locale="ru-RU"
        )
        
        page = await context.new_page()
        
        # Убираем признаки автоматизации
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['ru-RU', 'ru'] });
        """)
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            print(f">>> Ошибка загрузки: {e}")
            await browser.close()
            return
        
        await page.wait_for_timeout(5000)
        
        # Проверяем, что страница загрузилась
        body_text = await page.inner_text("body")
        if len(body_text) < 100:
            print(">>> Страница пустая — Ozon заблокировал запрос")
            await browser.close()
            return
        
        print(f">>> Страница загружена, символов: {len(body_text)}")
        
        # Скроллим
        for i in range(5):
            await page.evaluate("window.scrollBy(0, 800)")
            await page.wait_for_timeout(2000)
        
        # Пробуем найти данные через API Ozon (самый надёжный способ)
        # Сначала попробуем найти JSON-данные прямо на странице
        page_content = await page.content()
        
        # Ищем window.__NUXT__ или window.__INITIAL_STATE__
        products = []
        
        # Способ 1: Ищем JSON в тегах script
        script_tags = page.locator("script#__NEXT_DATA__")
        if await script_tags.count() > 0:
            json_text = await script_tags.first.inner_text()
            try:
                data = json.loads(json_text)
                print(">>> Нашли данные через __NEXT_DATA__")
            except:
                data = None
        else:
            data = None
        
        # Способ 2: Обычный парсинг карточек
        if not data:
            print(">>> Ищем карточки товаров...")
            
            # Разные варианты селекторов
            selectors = [
                "div[class*='widget-search-result'] div[class*='item']",
                "div[class*='tile-root']",
                "a[href*='/product/']",
                "div[data-widget='searchResultsV2'] div",
            ]
            
            # Сохраняем HTML для отладки
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(page_content)
            print(">>> HTML сохранён в debug_page.html")
            
            # Пробуем найти хоть что-то
            for sel in selectors:
                cards = page.locator(sel)
                count = await cards.count()
                print(f"    Селектор '{sel[:50]}...' → найдено: {count}")
                if count > 0:
                    # Парсим
                    for i in range(min(count, 40)):
                        try:
                            card = cards.nth(i)
                            text = await card.inner_text()
                            text = text.strip()
                            if text and len(text) > 10:
                                # Ищем цену в тексте
                                prices = re.findall(r'(\d[\d\s]*)\s*₽', text)
                                price = prices[0].replace(' ', '') if prices else ""
                                
                                # Первая строка как название
                                lines = [l.strip() for l in text.split('\n') if l.strip()]
                                name = lines[0] if lines else text[:100]
                                
                                if price:
                                    products.append({
                                        "Название": name[:150],
                                        "Цена (руб)": price,
                                        "Старая цена (руб)": "",
                                        "Ссылка": url
                                    })
                        except:
                            pass
                    if products:
                        break
        
        await browser.close()
        
        if products:
            filename = f"ozon_{SEARCH_QUERY.replace(' ', '_')}_low_price.csv"
            with open(filename, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["Название", "Цена (руб)", "Старая цена (руб)", "Ссылка"], delimiter=';')
                writer.writeheader()
                writer.writerows(products)
            print(f"\n>>> ГОТОВО! Сохранено {len(products)} товаров в: {filename}")
        else:
            print("\n>>> Ничего не собрано. HTML страницы сохранён в debug_page.html")

if __name__ == "__main__":
    asyncio.run(parse_ozon())         
