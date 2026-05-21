# main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import datetime

# 우리가 만든 모듈들을 가져옵니다.
from fetch_news.fetch_news import get_tech_news, analyze_news_with_gemini, send_to_notion
from database import init_db, save_articles, save_report  # ⭐ DB 모듈 추가!

app = FastAPI(
    title="Smart Newsletter & SNS Automation API",
    description="로컬 가상 DB 아카이빙 기능이 탑재된 AI 에이전트 백엔드 시스템",
    version="1.1.0"
)


# [Event Listener] 서버가 구동될 때 데이터베이스 테이블을 자동으로 만듭니다.
@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/")
def read_root():
    return {"message": "AI 뉴스레터 자동화 백엔드 서버가 정상 구동 중입니다. 🚀"}


@app.post("/api/v1/trends/collect")
def collect_and_archive_trends():
    print("\n[API 호출] 실시간 트렌드 파이프라인 가동 요청을 수신했습니다.")

    try:
        # 1단계: 데이터 인제스션 (뉴스 수집)
        captured_articles = get_tech_news()
        if not captured_articles:
            raise HTTPException(status_code=500, detail="외부 RSS 피드 데이터 수집 실패")

        # 2단계: 로컬 DB 적재 및 중복 필터링 (Data Engineering)
        # 만약 5개 뉴스 중 기존에 수집했던 뉴스가 있다면 DB가 알아서 걸러줍니다.
        new_saved_count = save_articles(captured_articles)
        print(f"[데이터 적재] 수집된 {len(captured_articles)}개의 뉴스 중 {new_saved_count}개의 신규 뉴스가 DB에 보관되었습니다.")

        # 3단계: 제미나이 AI 트렌드 리포트 가공
        report_md = analyze_news_with_gemini(captured_articles)
        if not report_md:
            raise HTTPException(status_code=500, detail="Gemini 분석 실패")

        # 4단계: 생성된 리포트를 로컬 DB 히스토리 테이블에 적재
        today_str = datetime.date.today().isoformat()
        report_title = f"🤖 오늘의 테크 트렌드 리포트 ({today_str})"
        save_report(report_title, report_md)

        # 5단계: 노션 데이터베이스 최종 서빙 (토큰이 없으면 콘솔 경고만 뜨고 프로세스는 안전하게 통과됩니다)
        send_to_notion(report_md)

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "로컬 DB 적재 및 AI 분석 파이프라인이 성공적으로 완료되었습니다. (노션 적재는 토큰 세팅 후 정상 반영됩니다)",
                "database_stats": {
                    "total_fetched": len(captured_articles),
                    "new_inserted_into_db": new_saved_count
                }
            }
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"[서버 내부 에러] {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)