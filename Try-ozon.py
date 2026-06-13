import asyncio
from playwright.async_api import async_playwright
import csv
import re
import os

async def parse_ozon():
    SEARCH_QUERY = "Смартфоны"  # <-- ЗАМЕНИ НА СВОЙ ЗАПРОС
    
    url = f"https://www.ozon.ru/search/?sorting=price_asc&text={SEARCH_QUERY.replace(' ', '+')}"
    
    print(f">>> Открываю: {url}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(3000)
        
        try:
            close_btn = page.locator("button:has-text('Закрыть')")
            if await close_btn.count() > 0:
                await close_btn.first.click()
        except:
            pass
        
        print(">>> Скроллю страницу...")
        for i in range(5):
            await page.evaluate("window.scrollBy(0, 1500)")
            await page.wait_for_timeout(2000)
        
        product_cards = page.locator("div[data-widget='searchResultsV2'] >> div.tile-root")
        total = await product_cards.count()
        print(f">>> Найдено товаров: {total}")
        
        products = []
        
        for i in range(total):
            card = product_cards.nth(i)
            if not await card.is_visible():
                continue
            
            try:
                name_locator = card.locator("a.tile-hover-target span")
                if await name_locator.count() == 0:
                    name_locator = card.locator("span.tsBody500Medium")
                name = await name_locator.first.inner_text() if await name_locator.count() > 0 else "Нет названия"
                name = name.strip()
                
                price_locator = card.locator("span.c3g1-a2")
                if await price_locator.count() == 0:
                    price_locator = card.locator("span[style*='color'] >> span")
                price_text = await price_locator.first.inner_text() if await price_locator.count() > 0 else "0"
                
                old_price_locator = card.locator("span.c3g1-a5")
                if await old_price_locator.count() == 0:
                    old_price_locator = card.locator("s span")
                old_price_text = await old_price_locator.first.inner_text() if await old_price_locator.count() > 0 else ""
                
                link_locator = card.locator("a.tile-hover-target")
                href = await link_locator.get_attribute("href") if await link_locator.count() > 0 else ""
                full_link = f"https://www.ozon.ru{href}" if href else ""
                
                def clean_price(text):
                    return re.sub(r'[^\d]', '', text)
                
                products.append({
                    "Название": name,
                    "Цена (руб)": clean_price(price_text),
                    "Старая цена (руб)": clean_price(old_price_text) if old_price_text else "",
                    "Ссылка": full_link
                })
                
                print(f"[{i+1}/{total}] {name[:80]}... - {clean_price(price_text)} руб.")
                
            except Exception as e:
                print(f"Ошибка в карточке {i}: {e}")
                continue
        
        await browser.close()
        
        if products:
            filename = f"ozon_{SEARCH_QUERY.replace(' ', '_')}_low_price.csv"
            with open(filename, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["Название", "Цена (руб)", "Старая цена (руб)", "Ссылка"], delimiter=';')
                writer.writeheader()
                writer.writerows(products)
            print(f"\n>>> Готово! Сохранено {len(products)} товаров в: {filename}")
            print(f">>> Скачай файл через вкладку Files на Render")
        else:
            print("\n>>> Ничего не собрано.")

if __name__ == "__main__":
    asyncio.run(parse_ozon())
