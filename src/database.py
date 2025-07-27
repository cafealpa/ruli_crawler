
import sqlite3
import json
from typing import List, Optional
from .models import Post, Comment

class DatabaseManager:
    """SQLite 데이터베이스를 관리하는 클래스"""
    def __init__(self, db_path: str):
        """DatabaseManager를 초기화합니다.

        Args:
            db_path (str): SQLite 데이터베이스 파일의 경로.
        """
        self.db_path = db_path

    def _execute(self, query, params=(), fetch=None):
        """데이터베이스 연결, 실행, 커밋 및 연결 닫기를 한 번에 처리합니다."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            if fetch == 'one':
                return cursor.fetchone()
            if fetch == 'all':
                return cursor.fetchall()
            if query.strip().upper().startswith('INSERT'):
                return cursor.lastrowid
            return None

    def create_tables(self):
        """posts 및 comments 테이블을 생성합니다."""
        # DROP 문은 별도로 실행
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS comments;")
            cursor.execute("DROP TABLE IF EXISTS posts;")
            conn.commit()

        create_posts_query = """
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                content TEXT,
                content_html TEXT,
                image_urls TEXT,
                post_created TEXT
            )
        """
        create_comments_query = """
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                html TEXT,
                text TEXT,
                comment_created TEXT,
                FOREIGN KEY (post_id) REFERENCES posts (id)
            )
        """
        self._execute(create_posts_query)
        self._execute(create_comments_query)

    def insert_post(self, post: Post) -> Optional[int]:
        """게시글 데이터를 데이터베이스에 삽입합니다."""
        query = """
            INSERT INTO posts (title, url, content, content_html, image_urls, post_created)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        image_urls_json = json.dumps(post.image_urls)
        params = (post.title, post.url, post.content, post.content_html, image_urls_json, post.post_created)
        try:
            return self._execute(query, params)
        except sqlite3.IntegrityError:
            return None

    def insert_comment(self, comment: Comment):
        """댓글 데이터를 데이터베이스에 삽입합니다."""
        query = """
            INSERT INTO comments (post_id, html, text, comment_created)
            VALUES (?, ?, ?, ?)
        """
        params = (comment.post_id, comment.html, comment.text, comment.comment_created)
        self._execute(query, params)

    def get_all_posts(self) -> List[Post]:
        """데이터베이스에서 모든 게시글을 조회합니다."""
        query = "SELECT id, title, url, content, content_html, image_urls, post_created FROM posts"
        rows = self._execute(query, fetch='all')
        posts = []
        for row in rows:
            post_id, title, url, content, content_html, image_urls_json, post_created = row
            image_urls = json.loads(image_urls_json) if image_urls_json else []
            comments = self.get_comments_for_post(post_id)
            posts.append(Post(id=post_id, title=title, url=url, content=content, content_html=content_html, image_urls=image_urls, post_created=post_created, comments=comments))
        return posts

    def get_comments_for_post(self, post_id: int) -> List[Comment]:
        """특정 게시글의 댓글을 조회합니다."""
        query = "SELECT html, text, comment_created, post_id FROM comments WHERE post_id = ?"
        rows = self._execute(query, (post_id,), fetch='all')
        return [Comment(html=row[0], text=row[1], comment_created=row[2], post_id=row[3]) for row in rows]

    def search_posts(self, start_date: str, end_date: str, keyword: Optional[str] = None) -> List[Post]:
        """지정된 기간과 키워드로 게시글을 검색합니다."""
        query = "SELECT id, title, url, content, content_html, image_urls, post_created FROM posts WHERE post_created BETWEEN ? AND ?"
        params = [start_date, end_date]

        if keyword:
            query += " AND (title LIKE ? OR content LIKE ?)"
            params.extend([f'%{keyword}%', f'%{keyword}%'])

        rows = self._execute(query, tuple(params), fetch='all')
        posts = []
        for row in rows:
            post_id, title, url, content, content_html, image_urls_json, post_created = row
            image_urls = json.loads(image_urls_json) if image_urls_json else []
            comments = self.get_comments_for_post(post_id)
            posts.append(Post(title=title, url=url, content=content, content_html=content_html, image_urls=image_urls, post_created=post_created, comments=comments))
        return posts
