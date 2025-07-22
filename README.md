# Ruliweb Humor Board Crawler (루리웹 유머 게시판 크롤러)

## 1. 프로그램 소개

이 프로그램은 Python과 Playwright 라이브러리를 사용하여 루리웹(Ruliweb)의 모바일 유머 게시판 베스트 글을 크롤링하고, 추출된 데이터를 SQLite 데이터베이스에 저장하는 스크립트입니다. 확장성과 유지보수성을 고려하여 MVC(Model-View-Controller) 패턴으로 설계되었습니다.

## 2. 주요 기능

- **게시글 정보 추출**: 유머 게시판의 베스트 글 목록에서 각 게시글의 제목과 원본 링크(URL)를 가져옵니다.
- **상세 내용 추출**: 각 게시글 링크로 접속하여 본문 내용, 이미지 URL, 그리고 댓글을 추출합니다.
- **데이터베이스 저장**: 추출된 모든 게시글 정보(제목, URL, 내용, 이미지 URL, 댓글)를 SQLite 데이터베이스에 저장합니다.
- **콘솔 출력**: 추출된 모든 정보를 실시간으로 콘솔에 출력하여 진행 상황을 확인할 수 있습니다.

## 3. 프로젝트 구조

프로젝트는 MVC 패턴에 따라 다음과 같이 구성됩니다.

```
ruli_crawler/
├── src/
│   ├── __init__.py       # Python 패키지 초기화 파일
│   ├── models.py         # (Model) 게시글 데이터 구조 정의 (Post 클래스)
│   ├── view.py           # (View) 데이터 표시 로직 (콘솔 출력)
│   ├── scraper.py        # Ruliweb에서 데이터를 스크랩하는 로직
│   ├── controller.py     # (Controller) 전체 크롤링 흐름 제어 및 데이터베이스 연동
│   └── database.py       # SQLite 데이터베이스 연결 및 관리 로직
├── main.py               # 프로그램 시작점
└── README.md             # 프로젝트 설명 파일
```

## 4. 준비 사항

- **Python 3**: 프로그램 실행을 위해 Python 3가 설치되어 있어야 합니다.
- **Playwright 라이브러리**: 웹 자동화 및 크롤링을 위한 Playwright 라이브러리가 필요합니다.

## 5. 설치 방법

1. **가상 환경 설정 (권장)**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate  # Windows
   ```

2. **필요한 라이브러리 설치**:
   ```bash
   pip install playwright
   ```

3. **Playwright용 브라우저 설치**:
   Playwright는 자동화를 위해 실제 브라우저를 사용합니다. 다음 명령어로 필요한 브라우저(Chromium 등)를 설치합니다.
   ```bash
   playwright install
   ```

## 6. 사용 방법

프로젝트 디렉토리에서 다음 명령어를 실행하여 크롤러를 시작합니다.

```bash
python main.py
```

- 스크립트가 실행되면, 자동으로 브라우저가 열리고(현재 `headless=False` 설정) 크롤링 과정이 진행됩니다.
- 각 게시글의 제목, URL, 본문 내용, 이미지 주소, 댓글이 순서대로 콘솔에 출력됩니다.
- 크롤링된 데이터는 `./ruliweb_posts.db` 파일에 SQLite 데이터베이스 형태로 저장됩니다.
- 현재는 테스트를 위해 5개의 게시글만 크롤링하도록 `main.py`에 `POST_LIMIT = 5`로 설정되어 있습니다. 모든 게시글을 크롤링하려면 이 값을 수정하거나 주석 처리할 수 있습니다.

---
*이 README 파일은 Gemini에 의해 생성되었습니다.*