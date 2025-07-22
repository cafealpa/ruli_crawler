import sqlite3
import sys

# UTF-8 인코딩 설정
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = 'ruliweb_posts.db'

def inspect_database():
    """데이터베이스의 내용을 확인하여 출력합니다."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        print("--- Comments Table ---")
        cursor.execute("SELECT id, post_id, text FROM comments LIMIT 5")
        comments = cursor.fetchall()

        if not comments:
            print("저장된 댓글이 없습니다.")
        else:
            for comment in comments:
                print(f"Comment ID: {comment[0]}, Post ID: {comment[1]}")
                print(f"Saved HTML: {comment[2]}\n")

        conn.close()
    except sqlite3.OperationalError as e:
        print(f"데이터베이스 확인 중 오류가 발생했습니다: {e}")
    except Exception as e:
        print(f"알 수 없는 오류 발생: {e}")

if __name__ == "__main__":
    inspect_database()
