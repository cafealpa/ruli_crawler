import asyncio
import re
from typing import List, Tuple

from playwright.async_api import async_playwright

from .models import Post, Comment


class RuliwebScraper:
    """Playwright를 사용하여 Ruliweb 게시글을 스크랩하는 클래스"""
    BASE_URL = "https://m.ruliweb.com"

    def __init__(self, headless: bool = True):
        """RuliwebScraper를 초기화합니다.

        Args:
            headless (bool): 브라우저를 헤드리스 모드로 실행할지 여부 (기본값: True).
        """
        self.headless = headless
        self.playwright = None
        self.browser = None

    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입 시 Playwright를 시작하고 브라우저를 실행합니다."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료 시 브라우저와 Playwright를 종료합니다."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def get_post_urls(self, board_url: str, limit: int) -> List[str]:
        """주어진 게시판 URL에서 게시글 URL 목록을 스크랩합니다.

        Args:
            board_url (str): 게시글 URL을 수집할 게시판의 URL.
            limit (int): 수집할 게시글 URL의 최대 개수.

        Returns:
            List[str]: 수집된 게시글 URL 문자열 리스트.
        """
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

    async def get_post_details(self, url: str) -> Tuple[Post, List[Comment]]:
        """주어진 게시글 URL에서 게시글의 상세 내용과 댓글을 스크랩합니다.

        Args:
            url (str): 상세 내용을 스크랩할 게시글의 URL.

        Returns:
            Tuple[Post, List[Comment]]: 스크랩된 Post 객체와 Comment 객체 리스트.
        """
        page = await self.browser.new_page()

        try:
            await page.goto(url)
            await page.wait_for_load_state('domcontentloaded')

            # 게시글 제목과 내용을 추출합니다.
            title = await page.locator(".subject_inner_text").inner_text()
            content = await page.locator(".view_content").inner_text()

            # 게시글 생성일 추출 (가정: .regdate 클래스를 가진 요소에 날짜 정보가 있음)
            post_created_element = await page.query_selector(".regdate") # 실제 웹사이트의 선택자에 따라 변경 필요
            post_created = await post_created_element.inner_text() if post_created_element else None
            if post_created:
                post_created = post_created.strip()

            # 댓글을 추출합니다.
            comments = []
            try:
                # 댓글 영역이 로드될 때까지 최대 5초 대기
                await page.wait_for_selector(".comment_view", timeout=5000)
                comments_elements = await page.query_selector_all(".comment_view.normal .comment_element.normal")

                for comment in comments_elements:
                    # HTML 정제: 모든 공백(탭, 줄바꿈 등)을 하나의 공백으로 변경
                    raw_html = await comment.inner_html()
                    comment_html = re.sub(r'\s+', ' ', raw_html).strip()

                    comment_p_text = await comment.query_selector("p.text")
                    comment_text = await comment_p_text.inner_text()

                    comment_created_element = await comment.query_selector(".comment_info .date") # 실제 웹사이트의 선택자에 따라 변경 필요
                    comment_created = await comment_created_element.inner_text() if comment_created_element else None
                    if comment_created:
                        comment_created = comment_created.strip()

                    print(Comment(html=comment_html, text=comment_text, comment_created=comment_created))

                    comments.append(Comment(html=comment_html, text=comment_text, comment_created=comment_created))

            except Exception:
                # 댓글이 없거나 로드에 실패하면 무시하고 계속 진행
                pass

            # 이미지 URL을 추출합니다.
            images = await page.query_selector_all(".view_content img")
            image_urls = []
            if images:
                for img in images:
                    img_url = await img.get_attribute("src")
                    if img_url and not img_url.startswith('http'):
                        img_url = "https://" + img_url.lstrip('/')
                    image_urls.append(img_url)

            # Post 객체를 생성하여 반환합니다.
            post = Post(title=title.strip(), url=url, content=content.strip(), image_urls=image_urls, post_created=post_created)
        finally:
            await page.close()

        return post, comments


async def main():
    """스크래퍼의 테스트를 위한 메인 함수 (실제 크롤링은 Controller에서 담당)"""
    scraper = RuliwebScraper()
    async with scraper:
        print("게시글 URL 수집 중...")
        post_urls = await scraper.get_post_urls("https://m.ruliweb.com/best/humor_only", 5)
        print(f"수집된 게시글 URL: {post_urls}")

        for url in post_urls:
            print()
            print(f"게시글 상세 정보 스크랩 중: {url}")
            post, comments = await scraper.get_post_details(url)
            print(f"제목: {post.title}")
            print(f"URL: {post.url}")
            print(f"내용: {post.content[:200]}...")
            print(f"이미지 URL: {post.image_urls}")
            print(f"생성일: {post.post_created}")
            print("댓글:")
            for comment in comments:
                print(f"- {comment.text} (생성일: {comment.comment_created})")  # 댓글 HTML이 길 수 있으므로 일부만 출력
            print("-" * 20)


if __name__ == "__main__":
    asyncio.run(main())
