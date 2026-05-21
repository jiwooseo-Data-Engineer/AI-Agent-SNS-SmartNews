# 🤖 Real-Time Tech Trend Analysis & Automated Newsletter Agent (v1.2.0)
> **FastAPI, SQLite 및 APScheduler 기반의 무인 자동화 테크 뉴스레터 파이프라인 시스템**

본 프로젝트는 외부 데이터 소스(RSS)로부터 실시간 기술 트렌드 데이터를 안정적으로 수집(Data Ingestion)하고, 서버 내부의 로컬 가상 RDB(SQLite)를 통해 데이터 멱등성(Idempotency)을 확보하며, 생성형 AI(Gemini Pro)와 백그라운드 스케줄러를 결합해 무인 배치(Batch) 환경에서 뉴스레터를 자동 생성 및 노션 DB로 서빙하는 **생산성 자동화 백엔드 시스템**입니다.

도커(Docker) 기반의 컨테이너라이징을 통해 환경에 구애받지 않는 클라우드 아키텍처 배포 준비를 완료했습니다.

📅 **실시간 적재 대시보드:** 

## 🏗️ 시스템 아키텍처 (Architecture)

[인프라 트리거 및 스케줄러 라인]
⏰ Background Scheduler (APScheduler) ──(1분 주기/매일 정기 배치)──┐
▼
[웹 엔드포인트 라인]                                             [ Core Pipeline ]
👤 Client / Tester ──(HTTP POST)──> [ FastAPI Server ] ──────> 1. Ingestion (urllib3)
2. Deduplication (SQLite)
3. LLM Processing (Gemini)
4. Serving (Notion API)



[Client / UI] ──(HTTP POST 요청)──> [ FastAPI Web Server ] (main.py)
│
┌──────────┴──────────┐
▼                     ▼
[ Ingestion & Filter ]  [ Core AI Agent ]
- urllib3 / feedparser  - Gemini 2.5 Flash
- SQLite RDB (적재/검증) - 프로그래밍 템플릿 가공
│                     │
└──────────┬──────────┘
▼
[ Data Serving Layer ]
- Notion Web API 적재
---
---

## ✨ 핵심 인프라 기능 (Key Features)

* **RESTful API 웹 서버 & Swagger UI:** `FastAPI` 기반 아키텍처 전환 및 자동 명세서 토대 구축.
* **데이터 멱등성(Idempotency) 보장:** `SQLite3` 유니크 키 제약을 활용하여 반복 호출 시 데이터 중복 유입 및 LLM 토큰 비용 낭비를 원천 차단하는 정제 레이어 구현.
* **무인 배치 자동화 시스템:** 백그라운드 스케줄러(`APScheduler`) 탑재로 365일 정해진 타임라인에 휴먼 에러 없이 파이프라인이 자동 구동되는 완전 자동화 달성.
* **Docker 가상화 기술 적용:** 배포 환경 격리를 위한 `Dockerfile` 인프라 코딩을 완료하여 컨테이너 기반 클라우드(AWS, GCP 등) 배포 최적화.

---

## 🛠️ 기술 스택 (Tech Stacks)

* **Backend & Infrastructure:** `FastAPI`, `Uvicorn`, `APScheduler`, `Docker`
* **Language & Database:** Python 3.11+, `SQLite3`
* **Third-Party API & Parsing:** `google-genai`, `feedparser`, `requests`, `python-dotenv`

---

## 🚀 배포 및 시작 가이드 (How to Run with Docker)

### 1. 로컬 환경 변수 구성 (`.env`)
프로젝트 최상위 루트에 `.env` 파일을 생성하고 발급받은 키를 매핑합니다.
```text
GEMINI_API_KEY=your_gemini_api_key
NOTION_TOKEN=your_notion_integration_token
NOTION_DATABASE_ID=your_notion_database_id
```

2. 도커 컨테이너 빌드 및 실행 (Dockerizing)
# 1. 도커 이미지 빌드
docker build -t tech-trend-agent .

# 2. 환경변수 파일을 주입하여 컨테이너 독립 구동 (배포 모드)
docker run -d -p 8000:8000 --env-file .env --name trend-bot tech-trend-agent

## 🚀 시작 가이드 (How to Run)

### 1. 로컬 환경 변수 구성 (`.env`)
프로젝트 최상위 루트에 `.env` 파일을 생성하고 발급받은 키를 매핑합니다.
```text
GEMINI_API_KEY=your_gemini_api_key
NOTION_TOKEN=your_notion_integration_token
NOTION_DATABASE_ID=your_notion_database_id
```
2. 패키지 설치 및 웹 서버 구동

# 가상환경 내부 필수 패키지 설치
pip install fastapi uvicorn google-genai feedparser requests python-dotenv urllib3

# FastAPI 웹 서버 기동
python main.py

3. API 명세서 및 파이프라인 테스트
서버가 켜지면 브라우저를 열고 아래 주소로 접속해 백엔드 인프라를 웹 환경에서 직접 테스트할 수 있습니다.

메인 API 헬스체크: http://127.0.0.1:8000/
인터랙티브 Swagger 대시보드: http://127.0.0.1:8000/docs

**백그라운드 스케줄러(Background Automation) 탑재:** `APScheduler`를 연동하여 가동 시간 분산 및 자동 배치(Batch Job) 인프라 구축. 매일 지정된 시간에 휴먼 에러 없이 무인으로 작동하는 완전 자동화 데이터 파이프라인 달성.