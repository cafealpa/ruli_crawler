

import asyncio
from .scraper import RuliwebScraper
from .database import DatabaseManager
from .view import ConsoleView

class CrawlerController:
    """크롤러의 동작을 제어하는 클래스 (Controller 역할)"""
    def __init__(self, limit: int, headless: bool, db_path: str):
        """초기화 메서드

        Args:
            limit (int): 크롤링할 게시글의 최대 개수.
            headless (bool): Playwright 브라우저를 헤드리스 모드로 실행할지 여부.
            db_path (str): SQLite 데이터베이스 파일 경로.
        """
        self.limit = limit
        self.headless = headless
        self.db_manager = DatabaseManager(db_path)
        self.view = ConsoleView()

    async def run(self):
        """크롤링 작업을 실행하는 메인 비동기 메서드"""
        self.view.show_message("Ruliweb 크롤러를 시작합니다.")
        self.db_manager.connect()
        self.db_manager.create_tables() # create_table -> create_tables

        async with RuliwebScraper(headless=self.headless) as scraper:
            self.view.show_message("최신 게시글 URL을 수집합니다...")
            board_url = "https://m.ruliweb.com/best/humor_only"
            post_urls = await scraper.get_post_urls(board_url, self.limit)
            self.view.show_message(f"{len(post_urls)}개의 게시글 URL을 수집했습니다.")

            for i, url in enumerate(post_urls):
                self.view.show_message(f"게시글 {i+1}/{len(post_urls)} 처리 중: {url}")
                post, comments = await scraper.get_post_details(url)
                
                # 데이터베이스에 게시글 저장 후, 저장된 게시글의 ID를 가져옵니다.
                post_id = self.db_manager.insert_post(post)
                if post_id:
                    # 게시글 ID를 사용하여 댓글을 저장합니다.
                    for comment in comments:
                        comment.post_id = post_id
                        self.db_manager.insert_comment(comment)

                # 콘솔에 게시글 및 댓글 정보를 출력합니다.
                self.view.display_post(post)
                self.view.display_comments(comments)

        self.db_manager.close()
        self.view.show_message("크롤링이 완료되었습니다.")

