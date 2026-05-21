# main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import datetime

# APScheduler에서 백그라운드 구동을 담당하는 모듈을 가져옵니다.
from apscheduler.schedulers.background import BackgroundScheduler

# 기존에 빌드한 모듈 및 DB 함수 가져오기
from fetch_news.fetch_news import get_tech_news, analyze_news_with_gemini, send_to_notion
from database import init_db, save_articles, save_report

app = FastAPI(
    title="Smart Newsletter & SNS Automation API",
    description="스케줄러 기반 실시간 자동화 파이프라인이 탑재된 백엔드 인프라",
    version="1.2.0"
)


# 1. 자동화 파이프라인의 핵심 코어를 별도 함수로 모듈화합니다.
def run_auto_pipeline():
    """정해진 시간마다 자동으로 뉴스 수집 -> DB 필터링 -> AI 분석 -> 적재를 수행하는 코어 배치 잡(Job)"""
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n⏰ [⏰ 자동 스케줄러] {current_time} - 정기 트렌드 분석 파이프라인을 자동으로 시작합니다.")

    try:
        # 1단계: 뉴스 수집
        captured_articles = get_tech_news()
        if not captured_articles:
            print("[⚠️ 자동화 경고] 외부 뉴스 데이터를 가져오지 못했습니다.")
            return

        # 2단계: 로컬 DB 적재 및 중복 검증
        new_saved_count = save_articles(captured_articles)
        print(f"[데이터 적재] 수집된 {len(captured_articles)}개 중 {new_saved_count}개의 새로운 뉴스가 DB에 저장되었습니다.")

        # 3단계: 제미나이 AI 뉴스레터 가공
        report_md = analyze_news_with_gemini(captured_articles)
        if not report_md:
            print("[⚠️ 자동화 경고] Gemini 분석 리포트 생성에 실패했습니다.")
            return

        # 4단계: 생성된 리포트 로컬 DB 저장
        today_str = datetime.date.today().isoformat()
        report_title = f"🤖 오늘의 테크 트렌드 리포트 ({today_str})"
        save_report(report_title, report_md)

        # 5단계: 노션 데이터베이스 최종 서빙
        send_to_notion(report_md)
        print(f"🚀 [성공] {current_time} 자 정기 자동 파이프라인이 안전하게 완료되었습니다.\n")

    except Exception as e:
        print(f"[🚨 자동화 시스템 에러] 배치 작업 중 예외 발생: {e}")


# 2. [Event Listener] 웹 서버가 켜질 때 DB를 초기화하고, 스케줄러를 가동합니다.
@app.on_event("startup")
def startup_event():
    # 데이터베이스 초기화
    init_db()

    # 백그라운드 스케줄러 가동
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")

    # [테스트용] 서버가 켜진 후, '1분마다(interval)' 한 번씩 위 run_auto_pipeline 함수를 자동으로 실행하도록 세팅
    # 💡 실무 배포 시에는 cron 방식으로 변경합니다. 예: trigger="cron", hour=7, minute=0 (매일 아침 7시 정각)
    scheduler.add_job(run_auto_pipeline, trigger="interval", minutes=1, id="trend_sync_job")

    # 스케줄러 켜기
    scheduler.start()
    print("[스케줄러 인프라] 백그라운드 자동화 스케줄러 가동 시작 (1분 주기 봇 활성화).")


@app.get("/")
def read_root():
    return {"message": "AI 뉴스레터 자동화 및 스케줄러 백엔드 서버가 정상 구동 중입니다. 🚀"}


# 기존의 수동 호출용 주소(POST)도 그대로 유지하여 하이브리드로 작동하게 만듭니다.
@app.post("/api/v1/trends/collect")
def collect_and_archive_trends():
    print("\n[API 수동 호출] 실시간 트렌드 파이프라인 가동 요청을 수신했습니다.")
    run_auto_pipeline()
    return JSONResponse(
        status_code=200,
        content={"status": "success", "message": "수동 파이프라인 구동이 완료되었습니다."}
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)