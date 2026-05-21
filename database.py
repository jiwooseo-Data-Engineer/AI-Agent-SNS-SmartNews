# database.py
import sqlite3
from pathlib import Path

# 프로젝트 루트 경로에 tech_trends.db 라는 파일 형태로 가상 데이터베이스를 생성합니다.
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "tech_trends.db"


def init_db():
    """서버가 켜질 때 뉴스 데이터를 저장할 테이블을 자동으로 생성합니다."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 뉴스 메타데이터를 저장할 테이블 설계 (스키마 정의)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            link TEXT UNIQUE,          -- 중복 수집을 방지하기 위해 링크를 유니크 키로 설정합니다.
            collected_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Gemini가 생성한 리포트 이력을 저장할 테이블 설계
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("[DB 인프라] SQLite 로컬 데이터베이스 테이블 초기화 완료.")


def save_articles(articles):
    """수집된 뉴스 중 처음 보는 신규 뉴스만 DB에 저장하고, 이번에 새로 저장된 뉴스의 개수를 반환합니다."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    new_articles_count = 0

    for article in articles:
        try:
            # INSERT OR IGNORE를 사용해 이미 링크가 존재(중복)하면 튕겨내고 새 데이터만 적재합니다. (Data Engineering의 Idempotency 확보)
            cursor.execute(
                "INSERT OR IGNORE INTO articles (title, link) VALUES (?, ?)",
                (article.title, article.link)
            )
            if cursor.rowcount > 0:
                new_articles_count += 1
        except Exception as e:
            print(f"[DB 에러] 뉴스 적재 중 예외 발생: {e}")

    conn.commit()
    conn.close()
    return new_articles_count


def save_report(title, content):
    """Gemini가 생성한 최종 리포트 원본을 히스토리 관리를 위해 DB에 저장합니다."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO reports (title, content) VALUES (?, ?)",
        (title, content)
    )

    conn.commit()
    conn.close()
    print("[DB 인프라] Gemini 분석 리포트 로컬 가상 DB 적재 완료.")