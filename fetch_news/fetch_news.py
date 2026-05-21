import os
import datetime
from pathlib import Path
import feedparser
import requests
import urllib3
from dotenv import load_dotenv
from google import genai
from google.genai import types

# =========================================================================
# [보안 및 환경 변수 설정]
# 현재 파일의 위치를 기준으로 프로젝트 최상위(Root) 폴더에 있는 .env 파일을 로드합니다.
# =========================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=dotenv_path)

# .env 파일에서 키값을 안전하게 꺼내옵니다.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# 만약 .env 파일을 못 읽을 경우를 대비한 하드코딩 2차 안전장치 (테스트용)
if not GEMINI_API_KEY:
    GEMINI_API_KEY = "AIzaSyDbKeXKs7rYzQWLVAm9QRLiStuzXOpFOPw"
# =========================================================================

# 제미나이 클라이언트 초기화
client = genai.Client(api_key=GEMINI_API_KEY)

# SSL 경고 무시 설정
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_tech_news():
    """1단계: 외부 RSS 피드에서 최신 IT 뉴스 5개를 수집합니다."""
    url = "https://www.hani.co.kr/rss/science/"
    print("IT 뉴스 트렌드 수집 시작...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        if response.status_code != 200:
            print(f"데이터 수집 실패. 상태 코드: {response.status_code}")
            return []

        feed = feedparser.parse(response.text)
        return feed.entries[:5]

    except Exception as e:
        print(f"수집 중 에러 발생: {e}")
        return []


def analyze_news_with_gemini(articles):
    """2단계: 수집한 뉴스를 기반으로 Gemini Pro 에이전트가 뉴스레터를 생성합니다."""
    if not articles:
        print("분석할 뉴스가 없습니다.")
        return ""

    print("\nGemini 에이전트가 오늘자 트렌드 분석을 시작합니다...")

    # 뉴스 데이터를 텍스트 컨텍스트로 결합
    news_context = ""
    for i, article in enumerate(articles, 1):
        news_context += f"[{i}] 제목: {article.title}\n    링크: {article.link}\n\n"

    # 에이전트 페르소나 지시문 선언
    system_instruction = (
        "당신은 IT 트렌드를 예리하게 분석하는 전문 테크 저널리스트이자 AI 에이전트입니다.\n"
        "제공된 뉴스 목록을 바탕으로 개발자와 IT 직군 종사자들이 읽기 좋은 '오늘의 테크 뉴스레터'를 작성해 주세요.\n"
        "포맷은 반드시 Markdown 형식을 사용하고, 전체적인 요약과 각 뉴스별 흥미로운 관점을 포함해 주세요."
    )
    user_prompt = f"다음은 오늘 수집된 최신 뉴스 목록입니다. 분석 리포트를 작성해 주세요:\n\n{news_context}"

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
            ),
        )
        return response.text

    except Exception as e:
        print(f"Gemini 분석 중 에러 발생: {e}")
        return ""


def send_to_notion(report_content):
    """3단계: 생성된 뉴스레터 마크다운 리포트를 노션 데이터베이스에 적재합니다."""
    if not report_content:
        print("노션으로 전송할 내용이 없습니다.")
        return

    # 환경 변수가 비어있는지 검증
    if not NOTION_TOKEN or not NOTION_DATABASE_ID:
        print("❌ 노션 토큰 또는 데이터베이스 ID가 세팅되지 않았습니다. .