
import asyncio
import os
import sys

# src 디렉토리를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.controller import CrawlerController

if __name__ == "__main__":
    # 환경 변수나 설정 파일에서 값을 가져오도록 확장할 수 있습니다.
    POST_LIMIT = 5
    HEADLESS_MODE = False

    # UTF-8 인코딩 설정 (Windows 콘솔 출력용)
    if sys.platform == "win32":
        os.environ["PYTHONIOENCODING"] = "utf-8"

    controller = CrawlerController(limit=POST_LIMIT, headless=HEADLESS_MODE)
    asyncio.run(controller.run())
