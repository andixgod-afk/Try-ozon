import asyncio
from playwright.async_api import async_playwright

async def parse_ozon():
    SEARCH_QUERY = "Смартфоны"
    
    url = f"https://www.ozon.ru/search/?sorting=price_asc&text={SEARCH_QUERY.replace(' ', '+')}"
    
    print(f">>> Открываю: {url}")
    
    try:
        async with async_playwright() as p:
            print(">>> Playwright запущен")
            
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
            print(">>> Браузер запущен")
            
            page = await browser.new_page()
            print(">>> Страница создана")
            
            print(">>> Загружаю страницу...")
            await page.goto(url, timeout=30000)
            print(">>> Страница загружена!")
            
            await page.wait_for_timeout(5000)
            
            # Просто сохраняем всю страницу как есть
            html = await page.content()
            
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(html)
            
            print(f">>> HTML сохранён! Размер: {len(html)} символов")
            
            # Выводим заголовок страницы для проверки
            title = await page.title()
            print(f">>> Заголовок страницы: {title}")
            
            # Выводим первые 500 символов body
            body = await page.inner_text("body")
            print(f">>> Начало страницы: {body[:500]}")
            
            await browser.close()
            print(">>> Готово!")
            
    except Exception as e:
        print(f">>> ОШИБКА: {e}")

if __name__ == "__main__":
    asyncio.run(parse_ozon())
