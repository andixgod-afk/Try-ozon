import asyncio
from playwright.async_api import async_playwright

async def main():
    print(">>> СТАРТ НОВОГО СКРИПТА")
    
    try:
        async with async_playwright() as p:
            print(">>> Playwright запущен")
            
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
            print(">>> Браузер открыт")
            
            page = await browser.new_page()
            
            url = "https://www.ozon.ru/search/?sorting=price_asc&text=Смартфоны"
            print(f">>> Загружаю: {url}")
            
            await page.goto(url, timeout=30000)
            print(">>> Страница загружена!")
            
            await page.wait_for_timeout(5000)
            
            html = await page.content()
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(html)
            print(f">>> HTML сохранён: {len(html)} символов")
            
            title = await page.title()
            print(f">>> Заголовок: {title}")
            
            body = await page.inner_text("body")
            print(f">>> Начало body: {body[:300]}")
            
            await browser.close()
            print(">>> ГОТОВО")
            
    except Exception as e:
        print(f">>> ОШИБКА: {type(e).__name__}: {e}")

asyncio.run(main())
