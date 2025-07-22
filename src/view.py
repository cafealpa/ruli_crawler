

from typing import List
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
                print(f"- {comment.text[:100]}...") # 댓글 HTML이 길 수 있으므로 일부만 출력
        print("-" * 20)

