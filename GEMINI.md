
파이썬으로 Playwright를 사용하여 Ruliweb 유머 게시판(https://m.ruliweb.com/best/humor_only)의 최신 게시글 제목과 링크, 게시글의 내용을 크롤링하는 프로그램을 작성해줘. 
각 게시글의 제목과 URL을 콘솔에 출력해야 해.
또한 각 게시글의 이미지 URL과 내용도 콘솔에 출력할 수 있게 해줘

프로그램 실행시 각 단계별 진행상황을 콘솔에 출력하도록 해야해.

일단은 개발단계니까 게시물 조회 수를 5개로 제한하자.

프로젝트의 구조는 MVC 모델에 맞게하고 추후 확장이 가능한 구조로 작성해줘
크롤링한 내용은 sqlite DB에 저장 할 수 있게 기능을 추가해
