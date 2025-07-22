
# Ruliweb Humor Board Crawler (루리웹 유머 게시판 크롤러)

## 1. 프로그램 소개

이 프로그램은 Python과 Playwright 라이브러리를 사용하여 루리웹(Ruliweb)의 모바일 유머 게시판 베스트 글을 크롤링하는 스크립트입니다.

## 2. 주요 기능

- **게시글 정보 추출**: 유머 게시판의 베스트 글 목록에서 각 게시글의 제목과 원본 링크(URL)를 가져옵니다.
- **상세 내용 추출**: 각 게시글 링크로 접속하여 본문 내용과 이미지 URL을 추출합니다.
- **콘솔 출력**: 추출된 모든 정보를 실시간으로 콘솔에 출력하여 진행 상황을 확인할 수 있습니다.

## 3. 준비 사항

- **Python 3**: 프로그램 실행을 위해 Python 3가 설치되어 있어야 합니다.
- **Playwright 라이브러리**: 웹 자동화 및 크롤링을 위한 Playwright 라이브러리가 필요합니다.

## 4. 설치 방법

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

## 5. 사용 방법

프로젝트 디렉토리에서 다음 명령어를 실행하여 크롤러를 시작합니다.

```bash
python ruli_crawler.py
```

- 스크립트가 실행되면, 자동으로 브라우저가 열리고(현재 `headless=False` 설정) 크롤링 과정이 진행됩니다.
- 각 게시글의 제목, URL, 본문 내용, 이미지 주소가 순서대로 콘솔에 출력됩니다.
- 모든 게시글 크롤링이 완료되면 프로그램은 자동으로 종료됩니다.

---
*이 README 파일은 Gemini에 의해 생성되었습니다.*
