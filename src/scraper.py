
import asyncio
from playwright.async_api import async_playwright, Page
from typing import List, Optional
from .models import Post

class RuliwebScraper:
    """Playwright를 사용하여 Ruliweb 게시글을 스크랩하는 클래스"""
    BASE_URL = "https://m.ruliweb.com"

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def get_post_urls(self, board_url: str, limit: int) -> List[str]:
        page = await self.browser.new_page()
        await page.goto(board_url)
        await page.wait_for_selector("tr.table_body.blocktarget")
        
        posts = await page.query_selector_all("tr.table_body.blocktarget")
        urls = []
        for i, post in enumerate(posts):
            if i >= limit:
                break
            title_element = await post.query_selector("a.subject_link")
            if title_element:
                url = await title_element.get_attribute("href")
                if url and not url.startswith('http'):
                    url = self.BASE_URL + url
                urls.append(url)
        await page.close()
        return urls

    async def get_post_details(self, url: str) -> Post:
        page = await self.browser.new_page()
        await page.goto(url)
        await page.wait_for_load_state('domcontentloaded')

        title = await page.locator(".subject_inner_text").inner_text()
        content = await page.locator(".view_content").inner_text()
        
        comments_elements = await page.query_selector_all(".comment_view .text_content")
        comments = [await comment.inner_text() for comment in comments_elements]

        images = await page.query_selector_all(".view_content img")
        image_urls = []
        if images:
            for img in images:
                img_url = await img.get_attribute("src")
                if img_url and not img_url.startswith('http'):
                    img_url = "https:" + img_url
                image_urls.append(img_url)

        await page.close()
        return Post(title=title.strip(), url=url, content=content.strip(), image_urls=image_urls, comments=comments)
