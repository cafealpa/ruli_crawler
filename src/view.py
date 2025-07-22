

from .models import Post

class ConsoleView:
    """콘솔에 크롤링 진행 상황과 결과를 출력하는 클래스"""

    def display_progress(self, message: str):
        print(message)

    def display_post(self, post: Post, index: int):
        print(f"\n--- {index}번째 게시글 처리 중 ---")
        print(f"제목: {post.title}")
        print(f"URL: {post.url}")
        if post.content:
            print(f"내용: {post.content}")
        if post.image_urls:
            print(f"이미지 URL: {', '.join(post.image_urls)}")
        print("-" * 20)

    def display_error(self, message: str):
        print(f"오류: {message}")

