
import asyncio
from .scraper import RuliwebScraper
from .view import ConsoleView

class CrawlerController:
    """크롤러의 전체 동작을 제어하는 컨트롤러 클래스"""

    def __init__(self, limit: int = 5, headless: bool = False):
        self.limit = limit
        self.headless = headless
        self.view = ConsoleView()

    async def run(self):
        self.view.display_progress("크롤링을 시작합니다...")
        board_url = "https://m.ruliweb.com/best/humor_only"

        try:
            async with RuliwebScraper(headless=self.headless) as scraper:
                self.view.display_progress(f"{board_url} 에서 게시글 URL을 수집합니다.")
                post_urls = await scraper.get_post_urls(board_url, self.limit)
                self.view.display_progress(f"총 {len(post_urls)}개의 게시글을 찾았습니다.")

                for i, url in enumerate(post_urls):
                    try:
                        self.view.display_progress(f"{i+1}번째 게시글의 상세 정보를 가져옵니다...")
                        post = await scraper.get_post_details(url)
                        self.view.display_post(post, i + 1)
                    except Exception as e:
                        self.view.display_error(f"게시글({url}) 처리 중 오류: {e}")

        except Exception as e:
            self.view.display_error(f"크롤링 중 심각한 오류 발생: {e}")
        finally:
            self.view.display_progress("크롤링이 완료되었습니다.")
