

import asyncio
import os
import sys

# src 디렉토리를 Python 경로에 추가
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(PROJECT_ROOT, 'src'))

from src.controller import CrawlerController

if __name__ == "__main__":
    # 환경 변수나 설정 파일에서 값을 가져오도록 확장할 수 있습니다.
    POST_LIMIT = 5
    HEADLESS_MODE = False

    # 데이터베이스 파일 경로
    db_relative_path = './ruliweb_posts.db'
    DB_PATH = os.path.join(PROJECT_ROOT, db_relative_path)

    print(f"DB_PATH: {DB_PATH}")

    # UTF-8 인코딩 설정 (Windows 콘솔 출력용)
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    controller = CrawlerController(limit=POST_LIMIT, headless=HEADLESS_MODE, db_path=DB_PATH)
    asyncio.run(controller.run())

    # 검색 기능 예시 (필요에 따라 주석 처리하거나 사용자 입력으로 확장 가능)
    print("\n" + "#" * 30)
    print("게시글 검색 기능 테스트")
    print("#" * 30)

    # 예시 1: 특정 기간 내 모든 게시글 검색
    controller.search_and_display_posts(start_date="2023-01-01", end_date="2024-12-31")

    # 예시 2: 특정 기간 내 특정 키워드를 포함하는 게시글 검색
    controller.search_and_display_posts(start_date="2023-01-01", end_date="2024-12-31", keyword="유머")

