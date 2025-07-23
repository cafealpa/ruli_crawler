import tkinter as tk
import os
import sys

# src 디렉토리를 Python 경로에 추가
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(PROJECT_ROOT, 'src'))

from src.UI.ui_test import RuliCrawlerUI
from src.controller import CrawlerController

if __name__ == "__main__":
    # Tkinter UI 실행
    root = tk.Tk()

    # Controller 인스턴스 생성 (UI에 전달)
    # db_path는 프로젝트 루트 기준으로 설정
    db_relative_path = 'ruliweb_posts.db'
    DB_PATH = os.path.join(PROJECT_ROOT, db_relative_path)
    
    # UI에서 직접 Controller를 생성하도록 변경되었으므로, 여기서는 Controller를 직접 전달하지 않습니다.
    # RuliCrawlerUI 내부에서 Controller를 초기화합니다.
    app = RuliCrawlerUI(root, db_path=DB_PATH)
    root.mainloop()