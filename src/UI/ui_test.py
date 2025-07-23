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

        # UI 요소 배치
        self.create_widgets()

        # TkinterView 인스턴스 생성
        self.tkinter_view = TkinterView(self.results_text, self.master.after)

        # Controller 초기화 (db_path는 실제 경로로 설정 필요)
        self.controller = CrawlerController(limit=10, headless=True, db_path=db_path, view=self.tkinter_view)

    def create_widgets(self):
        # 검색어 입력 필드
        self.query_label = ttk.Label(self.master, text="검색어:")
        self.query_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.query_entry = ttk.Entry(self.master, width=50)
        self.query_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # 날짜 선택 필드
        self.start_date_label = ttk.Label(self.master, text="시작 날짜:")
        self.start_date_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.start_date_entry = DateEntry(self.master, width=12, background='darkblue',
                                          foreground='white', borderwidth=2, year=datetime.now().year,
                                          month=datetime.now().month, day=datetime.now().day,
                                          date_pattern='yyyy-mm-dd')
        self.start_date_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.end_date_label = ttk.Label(self.master, text="종료 날짜:")
        self.end_date_label.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.end_date_entry = DateEntry(self.master, width=12, background='darkblue',
                                        foreground='white', borderwidth=2, year=datetime.now().year,
                                        month=datetime.now().month, day=datetime.now().day,
                                        date_pattern='yyyy-mm-dd')
        self.end_date_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # 조회 버튼
        self.query_button = ttk.Button(self.master, text="조회", command=self.on_query_button_click)
        self.query_button.grid(row=0, column=2, padx=5, pady=5)

        # 크롤링 시작 버튼
        self.crawl_button = ttk.Button(self.master, text="크롤링 시작", command=self.on_crawl_button_click)
        self.crawl_button.grid(row=0, column=3, padx=5, pady=5)

        # 결과 표시 텍스트 영역
        self.results_text = tk.Text(self.master, wrap=tk.WORD, width=80, height=20)
        self.results_text.grid(row=2, column=0, columnspan=5, padx=5, pady=5, sticky="nsew")

        # 스크롤바 추가
        self.scrollbar = ttk.Scrollbar(self.master, command=self.results_text.yview)
        self.scrollbar.grid(row=2, column=5, sticky="ns")
        self.results_text.config(yscrollcommand=self.scrollbar.set)

        # 그리드 가중치 설정 (창 크기 조절 시 위젯 크기 조절)
        self.master.grid_rowconfigure(2, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_columnconfigure(3, weight=1) # 종료 날짜 필드도 확장되도록 설정

    def on_query_button_click(self):
        query = self.query_entry.get()
        self.results_text.delete(1.0, tk.END) # 기존 내용 삭제
        self.results_text.insert(tk.END, f"'{query}'(으)로 조회합니다...\n")
        self.results_text.insert(tk.END, "검색 중입니다. 잠시 기다려 주세요...\n")

        # 검색 작업을 별도의 스레드에서 실행
        search_thread = threading.Thread(target=self._perform_search, args=(query,))
        search_thread.start()

    def _perform_search(self, keyword):
        start_date = self.start_date_entry.get_date().strftime("%Y-%m-%d")
        end_date = self.end_date_entry.get_date().strftime("%Y-%m-%d")

        try:
            posts = self.controller.search_posts(start_date, end_date, keyword)

            print(posts)

            self.master.after(0, self.display_posts, posts) # UI 업데이트는 메인 스레드에서
        except Exception as e:
            self.master.after(0, lambda e=e: self.results_text.insert(tk.END, f"오류 발생: {e}\n"))

    def display_posts(self, posts):
        self.results_text.delete(1.0, tk.END) # 기존 내용 삭제
        if not posts:
            self.results_text.insert(tk.END, "검색 결과가 없습니다.\n")
            return

        self.results_text.insert(tk.END, f"총 {len(posts)}개의 게시글을 찾았습니다.\n\n")
        for i, post in enumerate(posts):
            self.results_text.insert(tk.END, f"--- 게시글 {i+1} ---\n")
            self.results_text.insert(tk.END, f"제목: {post.title}\n")
            self.results_text.insert(tk.END, f"URL: {post.url}\n")
            self.results_text.insert(tk.END, f"생성일: {post.post_created}\n")
            self.results_text.insert(tk.END, f"내용: {post.content[:200]}...\n") # 내용의 일부만 표시
            if post.image_urls:
                self.results_text.insert(tk.END, f"이미지: {', '.join(post.image_urls[:3])}...\n") # 이미지 URL 일부만 표시
            if post.comments:
                self.results_text.insert(tk.END, f"댓글 수: {len(post.comments)}\n")
            self.results_text.insert(tk.END, "\n")

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