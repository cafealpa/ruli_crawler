from typing import Optional, Any
import threading
import asyncio

from .database import DatabaseManager
from .scraper import RuliwebScraper
from .view import ConsoleView

CONCURRENT_TASKS = 5 # 동시에 처리할 게시글 수

class CrawlerController:
    """크롤러의 동작을 제어하는 클래스 (Controller 역할)"""
    def __init__(self, limit: int, headless: bool, db_path: str, view: Any = None):
        """초기화 메서드"""
        self.limit = limit
        self.headless = headless
        self.db_manager = DatabaseManager(db_path)
        self.view = view if view else ConsoleView()
        self.stop_event = threading.Event()

    def request_stop(self):
        """크롤링 중지를 요청합니다."""
        self.stop_event.set()

    def reset_stop(self):
        """중지 요청 플래그를 초기화합니다."""
        self.stop_event.clear()

    async def run(self):
        """크롤링 작업을 실행하는 메인 비동기 메서드"""
        self.reset_stop()
        self.view.show_message("Ruliweb 크롤러를 시작합니다.")
        self.db_manager.create_tables()

        async with RuliwebScraper(headless=self.headless) as scraper:
            self.view.show_message("최신 게시글 URL을 수집합니다...")
            all_post_urls = []
            page = 1
            while len(all_post_urls) < self.limit and not self.stop_event.is_set():
                board_url = f"https://m.ruliweb.com/best/humor_only?page={page}"
                self.view.show_message(f"{page} 페이지에서 URL 수집 중...")
                post_urls_on_page = await scraper.get_post_urls(board_url)

                if not post_urls_on_page:
                    self.view.show_message("더 이상 게시글이 없어 URL 수집을 중단합니다.")
                    break

                all_post_urls.extend(post_urls_on_page)
                all_post_urls = list(dict.fromkeys(all_post_urls))

                if len(all_post_urls) >= self.limit:
                    all_post_urls = all_post_urls[:self.limit]
                    break
                
                page += 1

            if self.stop_event.is_set():
                self.view.show_message("사용자 요청에 의해 크롤링이 중단되었습니다. (URL 수집 단계)")
                return

            self.view.show_message(f"총 {len(all_post_urls)}개의 게시글 URL을 수집했습니다.")

            semaphore = asyncio.Semaphore(CONCURRENT_TASKS)
            async def fetch_and_process(url, index):
                async with semaphore:
                    if self.stop_event.is_set():
                        return None # 중지 요청 시 작업 중단
                    self.view.show_message(f"게시글 {index+1}/{len(all_post_urls)} 처리 중: {url}")
                    post, comments = await scraper.get_post_details(url)
                    return post, comments

            tasks = [fetch_and_process(url, i) for i, url in enumerate(all_post_urls)]
            results = await asyncio.gather(*tasks)

            # 결과 처리 및 DB 저장 (순차적으로 진행)
            for i, result in enumerate(results):
                if self.stop_event.is_set():
                    self.view.show_message("사용자 요청에 의해 크롤링이 중단되었습니다. (상세 정보 저장 단계)")
                    break
                if result:
                    post, comments = result
                    post_id = self.db_manager.insert_post(post)
                    if post_id:
                        for comment in comments:
                            comment.post_id = post_id
                            self.db_manager.insert_comment(comment)

                    self.view.display_post(post)
                    self.view.display_comments(comments)

        if not self.stop_event.is_set():
            self.view.show_message("크롤링이 완료되었습니다.")

    def search_posts(self, start_date: str, end_date: str, keyword: Optional[str] = None):
        """
        지정된 기간과 키워드로 게시글을 검색하고 결과를 반환합니다.

        Args:
            start_date (str): 검색 시작 날짜 (YYYY-MM-DD 형식).
            end_date (str): 검색 종료 날짜 (YYYY-MM-DD 형식).
            keyword (Optional[str]): 제목 또는 내용에서 검색할 키워드.
        Returns:
            List[Post]: 검색된 게시글 리스트.
        """
        posts = self.db_manager.search_posts(start_date, end_date, keyword)
        return posts


    def search_posts(self, start_date: str, end_date: str, keyword: Optional[str] = None):
        """
        지정된 기간과 키워드로 게시글을 검색하고 결과를 반환합니다.

        Args:
            start_date (str): 검색 시작 날짜 (YYYY-MM-DD 형식).
            end_date (str): 검색 종료 날짜 (YYYY-MM-DD 형식).
            keyword (Optional[str]): 제목 또는 내용에서 검색할 키워드.
        Returns:
            List[Post]: 검색된 게시글 리스트.
        """
        posts = self.db_manager.search_posts(start_date, end_date, keyword)
        return posts

