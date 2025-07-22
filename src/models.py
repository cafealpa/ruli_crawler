
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Comment:
    """댓글 데이터를 저장하는 데이터 클래스"""
    text: str  # 댓글 내용 (HTML 포함)
    post_id: Optional[int] = None  # 댓글이 속한 게시글의 ID (외래 키)

@dataclass
class Post:
    """게시글 데이터를 저장하는 데이터 클래스"""
    title: str  # 게시글 제목
    url: str  # 게시글 URL
    content: Optional[str] = None  # 게시글 내용 (HTML 포함)
    image_urls: List[str] = field(default_factory=list)  # 게시글 내 이미지 URL 리스트
