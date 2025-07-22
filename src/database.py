
import sqlite3
import json
from typing import List
from .models import Post

class DatabaseManager:
    """SQLite 데이터베이스를 관리하는 클래스"""
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def close(self):
        if self.conn:
            self.conn.close()

    def create_table(self):
        self.cursor.execute("DROP TABLE IF EXISTS posts;")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                content TEXT,
                image_urls TEXT,
                comments TEXT
            )
        """)
        self.conn.commit()

    def insert_post(self, post: Post):
        try:
            image_urls_json = json.dumps(post.image_urls)
            comments_json = json.dumps(post.comments)
            self.cursor.execute("""
                INSERT INTO posts (title, url, content, image_urls, comments)
                VALUES (?, ?, ?, ?, ?)
            """, (post.title, post.url, post.content, image_urls_json, comments_json))
            self.conn.commit()
        except sqlite3.IntegrityError:
            # URL이 이미 존재하는 경우 (UNIQUE 제약 조건 위반)
            pass # 이미 존재하는 게시글은 무시

    def get_all_posts(self) -> List[Post]:
        self.cursor.execute("SELECT title, url, content, image_urls, comments FROM posts")
        rows = self.cursor.fetchall()
        posts = []
        for row in rows:
            title, url, content, image_urls_json, comments_json = row
            image_urls = json.loads(image_urls_json) if image_urls_json else []
            comments = json.loads(comments_json) if comments_json else []
            posts.append(Post(title=title, url=url, content=content, image_urls=image_urls, comments=comments))
        return posts
