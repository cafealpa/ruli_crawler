

from typing import List, Optional
from .models import Post, Comment

class ConsoleView:
    """콘솔 출력을 담당하는 클래스 (View 역할)"""
    def show_message(self, message: str):
        """콘솔에 메시지를 출력합니다.

        Args:
            message (str): 출력할 메시지.
        """
        print(message)

    def display_post(self, post: Post):
        """게시글 정보를 콘솔에 출력합니다.

        Args:
            post (Post): 출력할 Post 객체.
        """
        print("-" * 20)
        print(f"제목: {post.title}")
        print(f"URL: {post.url}")
        print(f"내용: {post.content[:200]}...") # 내용이 길 경우 일부만 표시
        print(f"생성일: {post.post_created}")
        if post.image_urls:
            print("이미지 URL:")
            for url in post.image_urls:
                print(f"- {url}")

    def display_comments(self, comments: List[Comment]):
        """댓글 정보를 콘솔에 출력합니다.

        Args:
            comments (List[Comment]): 출력할 Comment 객체 리스트.
        """
        if comments:
            print("댓글:")
            for comment in comments:
                print(f"- {comment.text[:100]}... (생성일: {comment.comment_created})") # 댓글 HTML이 길 수 있으므로 일부만 출력
        print("-" * 20)

    def display_search_results(self, posts: List[Post], start_date: str, end_date: str, keyword: Optional[str] = None):
        """
        검색 결과를 콘솔에 출력합니다.

        Args:
            posts (List[Post]): 검색된 Post 객체 리스트.
            start_date (str): 검색 시작 날짜.
            end_date (str): 검색 종료 날짜.
            keyword (Optional[str]): 검색 키워드.
        """
        print("\n" + "=" * 30)
        print("검색 결과")
        print(f"기간: {start_date} ~ {end_date}")
        if keyword:
            print(f"키워드: {keyword}")
        print("=" * 30)

        if not posts:
            print("검색 조건에 맞는 게시글이 없습니다.")
            return

        for i, post in enumerate(posts):
            print(f"\n--- 게시글 {i+1} ---")
            print(f"제목: {post.title}")
            print(f"URL: {post.url}")
            print(f"생성일: {post.post_created}")
            print(f"내용: {post.content[:150]}...") # 내용이 길 경우 일부만 표시

