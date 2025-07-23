
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
        self.conn = None
        self.cursor = None

    def connect(self):
        """데이터베이스에 연결합니다."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def close(self):
        """데이터베이스 연결을 닫습니다."""
        if self.conn:
            self.conn.close()

    def create_tables(self):
        """posts 및 comments 테이블을 생성합니다.
        기존 테이블이 있다면 삭제 후 새로 생성합니다.
        comments 테이블은 posts 테이블의 id를 외래 키로 참조합니다.
        """
        self.cursor.execute("DROP TABLE IF EXISTS posts;")
        self.cursor.execute("DROP TABLE IF EXISTS comments;")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                content TEXT,
                image_urls TEXT,
                post_created TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                html TEXT,
                text TEXT,
                comment_created TEXT,
                FOREIGN KEY (post_id) REFERENCES posts (id)
            )
        """)
        self.conn.commit()

    def insert_post(self, post: Post) -> Optional[int]:
        """게시글 데이터를 데이터베이스에 삽입합니다.

        Args:
            post (Post): 삽입할 게시글 Post 객체.

        Returns:
            Optional[int]: 삽입된 게시글의 ID (Primary Key). 이미 존재하는 경우 None을 반환합니다.
        """
        try:
            image_urls_json = json.dumps(post.image_urls)
            self.cursor.execute("""
                INSERT INTO posts (title, url, content, image_urls, post_created)
                VALUES (?, ?, ?, ?, ?)
            """, (post.title, post.url, post.content, image_urls_json, post.post_created))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            # URL이 이미 존재하는 경우 (UNIQUE 제약 조건 위반)
            return None # 이미 존재하는 게시글은 무시

    def insert_comment(self, comment: Comment):
        """댓글 데이터를 데이터베이스에 삽입합니다.

        Args:
            comment (Comment): 삽입할 댓글 Comment 객체. post_id를 포함해야 합니다.
        """
        self.cursor.execute("""
            INSERT INTO comments (post_id, html, text, comment_created)
            VALUES (?, ?, ?, ?)
        """, (comment.post_id, comment.html, comment.text, comment.comment_created))
        self.conn.commit()

    def get_all_posts(self) -> List[Post]:
        """데이터베이스에서 모든 게시글을 조회합니다.

        Returns:
            List[Post]: 조회된 Post 객체 리스트.
        """
        self.cursor.execute("SELECT title, url, content, image_urls, post_created FROM posts")
        rows = self.cursor.fetchall()
        posts = []
        for row in rows:
            title, url, content, image_urls_json, post_created = row
            image_urls = json.loads(image_urls_json) if image_urls_json else []
            posts.append(Post(title=title, url=url, content=content, image_urls=image_urls, post_created=post_created))
        return posts

    def get_comments_for_post(self, post_url: str) -> List[Comment]:
        """특정 게시글의 댓글을 조회합니다.

        Args:
            post_url (str): 댓글을 조회할 게시글의 URL.

        Returns:
            List[Comment]: 조회된 Comment 객체 리스트.
        """
        self.cursor.execute("""
            SELECT
                c.html,
                c.text,
                c.comment_created,
                c.post_id
            FROM
                comments c
            JOIN
                posts p ON c.post_id = p.id
            WHERE
                p.url = ?
        """, (post_url,))
        rows = self.cursor.fetchall()
        comments = [Comment(html=row[0], text=row[1], comment_created=row[2], post_id=row[3]) for row in rows]

    def search_posts(self, start_date: str, end_date: str, keyword: Optional[str] = None) -> List[Post]:
        """
        지정된 기간 내에 생성된 게시글을 검색하고, 선택적으로 키워드를 사용하여 제목 또는 내용으로 필터링합니다.

        Args:
            start_date (str): 검색 시작 날짜 (YYYY-MM-DD 형식).
            end_date (str): 검색 종료 날짜 (YYYY-MM-DD 형식).
            keyword (Optional[str]): 제목 또는 내용에서 검색할 키워드.

        Returns:
            List[Post]: 검색 조건에 맞는 Post 객체 리스트.
        """
        query = "SELECT title, url, content, image_urls, post_created FROM posts WHERE post_created BETWEEN ? AND ?"
        params = (start_date, end_date)

        if keyword:
            query += " AND (title LIKE ? OR content LIKE ?)"
            params += (f'%{keyword}%', f'%{keyword}%')

        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        posts = []
        for row in rows:
            title, url, content, image_urls_json, post_created = row
            image_urls = json.loads(image_urls_json) if image_urls_json else []
            posts.append(Post(title=title, url=url, content=content, image_urls=image_urls, post_created=post_created))
        return posts
        return comments
