import tkinter as tk
from tkinter import ttk
import threading
import asyncio
from datetime import datetime, timedelta
from tkcalendar import DateEntry # tkcalendar 임포트 추가

from src.controller import CrawlerController
from src.models import Post, Comment # Post, Comment 임포트 추가

# Tkinter UI에 메시지를 표시하기 위한 View 클래스
class TkinterView:
    def __init__(self, text_widget, master_after_method):
        self.text_widget = text_widget
        self.master_after_method = master_after_method

    def show_message(self, message):
        self.master_after_method(0, lambda: self._insert_text(message + "\n"))

    def display_post(self, post: Post):
        message = f"\n--- 새 게시글 ---\n제목: {post.title}\nURL: {post.url}\n생성일: {post.post_created}\n내용: {post.content[:100]}...\n"
        self.master_after_method(0, lambda: self._insert_text(message))

    def display_comments(self, comments: list[Comment]):
        if comments:
            message = "댓글:\n"
            for comment in comments:
                message += f"- {comment.text[:50]}... (생성일: {comment.comment_created})\n"
            self.master_after_method(0, lambda: self._insert_text(message))

    def _insert_text(self, text):
        self.text_widget.insert(tk.END, text)
        self.text_widget.see(tk.END) # 스크롤을 항상 아래로

class RuliCrawlerUI:
    def __init__(self, master, db_path):
        self.master = master
        master.title("Ruliweb Crawler UI")

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill="both", padx=5, pady=5)

        self.crawl_tab = ttk.Frame(self.notebook)
        self.data_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.crawl_tab, text="크롤링")
        self.notebook.add(self.data_tab, text="데이터 확인")

        # UI 요소 배치
        self.create_widgets()

        # TkinterView 인스턴스 생성
        self.tkinter_view = TkinterView(self.results_text, self.master.after)

        # Controller 초기화 (db_path는 실제 경로로 설정 필요)
        self.controller = CrawlerController(limit=10, headless=True, db_path=db_path, view=self.tkinter_view)

    def create_widgets(self):
        # 크롤링 탭 UI 요소
        # 크롤링 시작 버튼
        self.crawl_button = ttk.Button(self.crawl_tab, text="크롤링 시작", command=self.on_crawl_button_click)
        self.crawl_button.grid(row=0, column=0, padx=5, pady=5)

        # 결과 표시 텍스트 영역
        self.results_text = tk.Text(self.crawl_tab, wrap=tk.WORD, width=80, height=20)
        self.results_text.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # 스크롤바 추가
        self.scrollbar = ttk.Scrollbar(self.crawl_tab, command=self.results_text.yview)
        self.scrollbar.grid(row=1, column=2, sticky="ns")
        self.results_text.config(yscrollcommand=self.scrollbar.set)

        # 그리드 가중치 설정 (창 크기 조절 시 위젯 크기 조절)
        self.crawl_tab.grid_rowconfigure(1, weight=1)
        self.crawl_tab.grid_columnconfigure(0, weight=1)

        # 데이터 확인 탭 UI 요소
        self.create_data_tab_widgets()

    def create_data_tab_widgets(self):
        """
        데이터 확인 탭의 위젯들을 생성하고 배치합니다.
        """
        # 상단 검색/필터 프레임
        self.top_frame = ttk.LabelFrame(self.data_tab, text="조회 조건", padding="10 10 10 10")
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # 날짜 범위 선택
        ttk.Label(self.top_frame, text="기간:").pack(side=tk.LEFT, padx=(0, 5))
        today = datetime.now()
        one_month_ago = today - timedelta(days=30) # 대략 한 달 전

        self.start_date_entry_data = DateEntry(self.top_frame, width=12, background='darkblue',
                                          foreground='white', borderwidth=2, year=one_month_ago.year,
                                          month=one_month_ago.month, day=one_month_ago.day,
                                          date_pattern='yyyy-MM-dd', locale='ko_KR')
        self.start_date_entry_data.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(self.top_frame, text="~").pack(side=tk.LEFT, padx=(0, 5))
        self.end_date_entry_data = DateEntry(self.top_frame, width=12, background='darkblue',
                                        foreground='white', borderwidth=2, year=today.year,
                                        month=today.month, day=today.day,
                                        date_pattern='yyyy-MM-dd', locale='ko_KR')
        self.end_date_entry_data.pack(side=tk.LEFT, padx=(0, 15))

        # 제목 + 내용 검색 입력 필드
        ttk.Label(self.top_frame, text="제목 + 내용:").pack(side=tk.LEFT, padx=(0, 5))
        self.title_content_search_entry = ttk.Entry(self.top_frame, width=50)
        self.title_content_search_entry.pack(side=tk.LEFT, padx=(0, 15))

        # 조회 버튼
        self.query_button_data = ttk.Button(self.top_frame, text="조회", command=self.perform_query)
        self.query_button_data.pack(side=tk.LEFT)

        # 메인 콘텐츠 및 댓글 프레임
        self.main_content_frame = ttk.Frame(self.data_tab, padding="10 0 10 10")
        self.main_content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        # PanedWindow 생성: 제시글 목록과 내용/댓글 창 사이의 크기를 조절할 수 있도록 합니다.
        self.left_paned_window = ttk.PanedWindow(self.main_content_frame, orient=tk.HORIZONTAL)
        self.left_paned_window.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 제시글 목록 프레임 (왼쪽 영역)
        self.post_list_frame = ttk.LabelFrame(self.left_paned_window, text="제시글 (0)", padding="10")
        self.left_paned_window.add(self.post_list_frame, weight=1)
        self.post_list_frame.config(width=200)
        self.post_list_frame.pack_propagate(False)

        # 제시글 목록을 표시하는 Listbox 위젯
        self.post_listbox = tk.Listbox(self.post_list_frame, height=20)
        self.post_listbox.pack(fill=tk.BOTH, expand=True)

        # 제시글 목록 스크롤바
        post_list_scrollbar = ttk.Scrollbar(self.post_list_frame, orient="vertical", command=self.post_listbox.yview)
        post_list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.post_listbox.config(yscrollcommand=post_list_scrollbar.set)

        # 내용 영역과 댓글 영역을 포함하는 PanedWindow (중앙-오른쪽 영역)
        self.right_paned_window = ttk.PanedWindow(self.left_paned_window, orient=tk.HORIZONTAL)
        self.left_paned_window.add(self.right_paned_window, weight=3)

        # 내용 영역 프레임 (중앙 영역)
        self.content_frame = ttk.LabelFrame(self.right_paned_window, text="내용 (HTML)", padding="10")
        self.right_paned_window.add(self.content_frame, weight=3)

        # 게시글 내용을 표시하는 Text 위젯 (HTML 내용을 가정)
        self.content_text = tk.Text(self.content_frame, wrap=tk.WORD)
        self.content_text.pack(fill=tk.BOTH, expand=True, pady=(0, 0))
        content_text_scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.content_text.yview)
        content_text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.content_text.config(yscrollcommand=content_text_scrollbar.set)

        # 댓글 영역 프레임 (오른쪽 영역)
        self.comment_frame = ttk.LabelFrame(self.right_paned_window, text="댓글 (0)", padding="10")
        self.right_paned_window.add(self.comment_frame, weight=1)
        self.comment_frame.config(width=200)
        self.comment_frame.pack_propagate(False)

        # 댓글 목록을 표시하는 Listbox 위젯
        self.comment_listbox = tk.Listbox(self.comment_frame, height=20)
        self.comment_listbox.pack(fill=tk.BOTH, expand=True)

        # 댓글 목록 스크롤바
        comment_list_scrollbar = ttk.Scrollbar(self.comment_frame, orient="vertical", command=self.comment_listbox.yview)
        comment_list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.comment_listbox.config(yscrollcommand=comment_list_scrollbar.set)

    def perform_query(self):
        """
        '조회' 버튼 클릭 시 호출되는 메서드입니다.
        현재는 선택된 날짜와 검색어를 콘솔에 출력하는 더미 기능만 포함합니다.
        실제 애플리케이션에서는 이 부분에 데이터 조회 및 UI 업데이트 로직이 구현됩니다.
        """
        start_date = self.start_date_entry_data.get_date()
        end_date = self.end_date_entry_data.get_date()
        search_text = self.title_content_search_entry.get()
        print(f"조회 시작: {start_date} ~ {end_date}, 검색어: '{search_text}'")
        # 여기에 실제 데이터 조회 로직을 추가합니다.
        # 예: 데이터베이스 쿼리, API 호출 등

    def on_crawl_button_click(self):
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "크롤링을 시작합니다...\n")
        self.crawl_button.config(state=tk.DISABLED) # 버튼 비활성화

        # 크롤링 작업을 별도의 스레드에서 실행
        crawl_thread = threading.Thread(target=self._perform_crawl)
        crawl_thread.start()

    def _perform_crawl(self):
        try:
            # asyncio 이벤트 루프를 새 스레드에서 실행
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.controller.run())
            loop.close()
            self.master.after(0, lambda: self.results_text.insert(tk.END, "크롤링이 완료되었습니다.\n"))
        except Exception as e:
            self.master.after(0, lambda e=e: self.results_text.insert(tk.END, f"크롤링 중 오류 발생: {e}\n"))
        finally:
            self.master.after(0, lambda: self.crawl_button.config(state=tk.NORMAL)) # 버튼 다시 활성화

if __name__ == "__main__":
    root = tk.Tk()
    app = RuliCrawlerUI(root)
    root.mainloop()
