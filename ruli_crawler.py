
import asyncio
from playwright.async_api import async_playwright

async def main():
    print("크롤링을 시작합니다...")
    async with async_playwright() as p:
        print("브라우저를 실행합니다.")
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print("Ruliweb 유머 게시판으로 이동합니다...")
        await page.goto("https://m.ruliweb.com/best/humor_only")

        print("게시글 목록을 찾고 있습니다...")
        await page.wait_for_selector("tr.table_body.blocktarget")
        posts = await page.query_selector_all("tr.table_body.blocktarget")
        print(f"총 {len(posts)}개의 게시글을 찾았습니다.")

        for i, post in enumerate(posts):
            print(f"\n--- {i+1}번째 게시글 처리 중 ---")
            title_element = await post.query_selector("a.subject_link")
            if title_element:
                title = await title_element.inner_text()
                url = await title_element.get_attribute("href")
                if url and not url.startswith('http'):
                    url = "https://m.ruliweb.com" + url

                print(f"제목: {title.strip()}")
                print(f"URL: {url}")

                print(f"게시글 페이지로 이동합니다: {url}")
                post_page = await browser.new_page()
                try:
                    await post_page.goto(url)
                    await post_page.wait_for_load_state('domcontentloaded')
                    print("게시글 페이지 로드 완료.")

                    print("게시글 내용을 가져옵니다...")
                    content_element = await post_page.query_selector(".view_content")
                    if content_element:
                        content = await content_element.inner_text()
                        print(f"내용: {content.strip()}")
                    else:
                        print("내용을 찾을 수 없습니다.")

                    print("이미지 URL을 가져옵니다...")
                    # Corrected image selector
                    images = await post_page.query_selector_all(".view_content img")
                    if images:
                        image_urls = []
                        for img in images:
                            img_url = await img.get_attribute("src")
                            if img_url and not img_url.startswith('http'):
                                img_url = "https:" + img_url
                            image_urls.append(img_url)
                        
                        if image_urls:
                            print(f"이미지 URL: {', '.join(image_urls)}")
                        else:
                            print("이미지를 찾을 수 없습니다.")
                    else:
                        print("게시글에 이미지가 없습니다.")

                except Exception as e:
                    print(f"게시글 페이지({url})를 여는 중 오류 발생: {e}")
                finally:
                    print("게시글 페이지를 닫습니다.")
                    await post_page.close()

            print("-" * 20)

        print("브라우저를 닫습니다.")
        await browser.close()
    print("크롤링이 완료되었습니다.")

if __name__ == "__main__":
    asyncio.run(main())
