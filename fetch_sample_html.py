import asyncio
from playwright.async_api import async_playwright
import sys

async def fetch_html(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_load_state('domcontentloaded')
        html_content = await page.content()
        await browser.close()
        return html_content

if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
    sample_url = "https://m.ruliweb.com/best/board/300143/read/66700000" # 샘플 게시글 URL
    print(asyncio.run(fetch_html(sample_url)))
