
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Post:
    """게시글 데이터를 저장하는 클래스"""
    title: str
    url: str
    content: Optional[str] = None
    image_urls: List[str] = field(default_factory=list)
