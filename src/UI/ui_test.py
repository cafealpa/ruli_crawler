import tkinter as tk
from tkinter import ttk
import threading
import asyncio
import queue
from datetime import datetime, timedelta
from tkcalendar import DateEntry # tkcalendar 임포트 추가
from tkhtmlview import HTMLLabel # HTMLLabel 임포트 추가

from src.controller import CrawlerController
from src.models import Post, Comment # Post, Comment 임포트 추가

# Tkinter UI에 메시지를 표시하기 위한 View 클래스
class TkinterView:
    def __init__(self, message_queue):
        self.message_queue = message_queue

    def show_message(self, message):
        self.message_queue.put(message + "\n")

    def display_post(self, post: Post):
        message = f"\n--- 새 게시글 ---\n제목: {post.title}\nURL: {post.url}\n생성일: {post.post_created}\n내용: {post.content[:100]}...\n"
        self.message_queue.put(message)

    def display_comments(self, comments: list[Comment]):
        if comments:
            message = "댓글:\n"
            for comment in comments:
                message += f"- {comment.text[:50]}... (생성일: {comment.comment_created})\n"
            self.message_queue.put(message)

class RuliCrawlerUI:
    def __init__(self, master, db_path):
        self.master = master
        master.title("Ruliweb Crawler UI")
        self.is_crawling = False

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill="both", padx=5, pady=5)

        self.crawl_tab = ttk.Frame(self.notebook)
        self.data_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.crawl_tab, text="크롤링")
        self.notebook.add(self.data_tab, text="데이터 확인")

        # 메시지 큐 생성
        self.message_queue = queue.Queue()

        # UI 요소 배치
        self.create_widgets()

        # TkinterView 인스턴스 생성
        self.tkinter_view = TkinterView(self.message_queue)

        # Controller 초기화
        self.controller = CrawlerController(limit=30, headless=False, db_path=db_path, view=self.tkinter_view)

        # 큐 폴링 시작
        self.master.after(100, self.process_queue)

    def create_widgets(self):
        # 크롤링 탭 UI 요소
        self.crawl_button = ttk.Button(self.crawl_tab, text="크롤링 시작", command=self.toggle_crawling)
        self.crawl_button.grid(row=0, column=0, padx=5, pady=5)

        self.results_text = tk.Text(self.crawl_tab, wrap=tk.WORD, width=80, height=20)
        self.results_text.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self.crawl_tab, command=self.results_text.yview)
        self.scrollbar.grid(row=1, column=2, sticky="ns")
        self.results_text.config(yscrollcommand=self.scrollbar.set)

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

        # PanedWindow 생성: 게시글 목록과 내용/댓글 창 사이의 크기를 조절할 수 있도록 합니다.
        self.left_paned_window = ttk.PanedWindow(self.main_content_frame, orient=tk.HORIZONTAL)
        self.left_paned_window.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 게시글 목록 프레임 (왼쪽 영역)
        self.post_list_frame = ttk.LabelFrame(self.left_paned_window, text="게시글 (0)", padding="10")
        self.left_paned_window.add(self.post_list_frame, weight=1)
        self.post_list_frame.config(width=200)
        self.post_list_frame.pack_propagate(False)

        # 게시글 목록을 표시하는 Listbox 위젯
        self.post_listbox = tk.Listbox(self.post_list_frame, height=20)
        self.post_listbox.pack(fill=tk.BOTH, expand=True)
        self.post_listbox.bind('<<ListboxSelect>>', self.on_post_select)

        # 게시글 목록 스크롤바
        post_list_scrollbar = ttk.Scrollbar(self.post_list_frame, orient="vertical", command=self.post_listbox.yview)
        post_list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.post_listbox.config(yscrollcommand=post_list_scrollbar.set)

        # 내용 영역과 댓글 영역을 포함하는 PanedWindow (중앙-오른쪽 영역)
        self.right_paned_window = ttk.PanedWindow(self.left_paned_window, orient=tk.HORIZONTAL)
        self.left_paned_window.add(self.right_paned_window, weight=3)

        # 내용 영역 프레임 (중앙 영역)
        self.content_frame = ttk.LabelFrame(self.right_paned_window, text="내용 (HTML)", padding="10")
        self.right_paned_window.add(self.content_frame, weight=3)

        # 게시글 내용을 표시하는 HTMLLabel 위젯
        self.content_text = HTMLLabel(self.content_frame, html="")
        self.content_text.pack(fill=tk.BOTH, expand=True, pady=(0, 0))

        # 댓글 영역 프레임 (오른쪽 영역)
        self.comment_frame = ttk.LabelFrame(self.right_paned_window, text="댓글 (0)", padding="10")
        self.right_paned_window.add(self.comment_frame, weight=1)
        self.comment_frame.config(width=200)
        self.comment_frame.pack_propagate(False)

        # 댓글 내용을 표시하는 Text 위젯
        self.comment_text_widget = tk.Text(self.comment_frame, wrap=tk.WORD, height=20)
        self.comment_text_widget.pack(fill=tk.BOTH, expand=True)

        # 태그 설정
        self.comment_text_widget.tag_configure("comment_header", font=("맑은 고딕", 9, "bold"))
        self.comment_text_widget.tag_configure("comment_body", font=("맑은 고딕", 9))
        self.comment_text_widget.tag_configure("separator", background="#e0e0e0") # 회색 배경으로 구분선

        # 댓글 내용 스크롤바
        comment_list_scrollbar = ttk.Scrollbar(self.comment_frame, orient="vertical", command=self.comment_text_widget.yview)
        comment_list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.comment_text_widget.config(yscrollcommand=comment_list_scrollbar.set)

    def process_queue(self):
        try:
            message = self.message_queue.get_nowait()
            self.results_text.insert(tk.END, message)
            self.results_text.see(tk.END)
        except queue.Empty:
            pass
        finally:
            self.master.after(100, self.process_queue)

    def perform_query(self):
        """
        '조회' 버튼 클릭 시 호출되는 메서드입니다.
        """
        start_date = self.start_date_entry_data.get_date()
        end_date = self.end_date_entry_data.get_date() + timedelta(days=1)
        search_text = self.title_content_search_entry.get()
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        self.current_posts = self.controller.search_posts(start_date_str, end_date_str, search_text)

        self.post_listbox.delete(0, tk.END)
        for i, post in enumerate(self.current_posts):
            self.post_listbox.insert(tk.END, f"{i+1}. {post.title}")

        self.post_list_frame.config(text=f"게시글 ({len(self.current_posts)})")

    def on_post_select(self, event):
        selected_indices = self.post_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            selected_post = self.current_posts[index]
            self.content_text.set_html(selected_post.content_html)

            self.comment_text_widget.delete(1.0, tk.END) # 기존 댓글 삭제
            if selected_post.comments:
                for i, comment in enumerate(selected_post.comments):
                    self.comment_text_widget.insert(tk.END, f"--- 댓글 {i+1} ---\n", "comment_header")
                    self.comment_text_widget.insert(tk.END, f"작성일: {comment.comment_created}\n", "comment_header")
                    self.comment_text_widget.insert(tk.END, f"{comment.text}\n\n", "comment_body")
                    if i < len(selected_post.comments) - 1:
                        self.comment_text_widget.insert(tk.END, "----------------------------------------\n", "separator")
            else:
                self.comment_text_widget.insert(tk.END, "댓글이 없습니다.\n")
            self.comment_frame.config(text=f"댓글 ({len(selected_post.comments)})")

    def toggle_crawling(self):
        if not self.is_crawling:
            self.start_crawling()
        else:
            self.stop_crawling()

    def start_crawling(self):
        self.is_crawling = True
        self.results_text.delete(1.0, tk.END)
        self.message_queue.put("크롤링을 시작합니다...\n")
        self.crawl_button.config(text="크롤링 중지")

        self.crawl_thread = threading.Thread(target=self._perform_crawl, daemon=True)
        self.crawl_thread.start()

    def stop_crawling(self):
        self.message_queue.put("크롤링 중지를 요청합니다...\n")
        self.controller.request_stop()
        self.crawl_button.config(state=tk.DISABLED) # 중지 요청 후 잠시 비활성화

    def _perform_crawl(self):
        try:
            asyncio.run(self.controller.run())
        except Exception as e:
            self.message_queue.put(f"크롤링 중 오류 발생: {e}\n")
        finally:
            self.master.after(0, self.on_crawl_finished)

    def on_crawl_finished(self):
        self.is_crawling = False
        self.crawl_button.config(text="크롤링 시작", state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    # db_path를 main.py에서처럼 적절히 설정해야 합니다.
    # 이 파일이 직접 실행될 경우를 대비한 임시 경로입니다.
    import os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'ruliweb_posts.db')
    app = RuliCrawlerUI(root, db_path=db_path)
    root.mainloop()
