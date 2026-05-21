# 🤖 Real-Time Tech Trend Analysis & Automated Newsletter Agent (v1.1.0)
> **FastAPI 웹 서버 및 SQLite 가상 DB 기반의 실시간 기술 트렌드 수집 및 AI 에이전트 자동화 시스템**

본 프로젝트는 외부 데이터 소스(RSS)로부터 실시간 기술 트렌드 데이터를 안정적으로 수집(Data Ingestion)하고, 서버 내부의 로컬 가상 관계형 데이터베이스(SQLite RDB)에 이력을 관리하며 중복 데이터를 원천 차단(Idempotency)한 뒤, 생성형 AI(Gemini Pro)를 활용해 가공한 테크 뉴스레터를 노션 데이터베이스로 자동 서빙하는 **안정적인 엔드투엔드(End-to-End) 데이터 파이프라인 백엔드 시스템**입니다.

기존의 단순 수동 실행 스크립트 형태에서 **RESTful API 웹 서버 아키텍처**로 완전히 진화시켜 인프라 확장성을 확보했습니다.

📅 **실시간 적재 대시보드:** [👉 본인의 노션 데이터베이스 공유 링크를 여기에 넣어주세요]

---

## 🏗️ 시스템 아키텍처 (Architecture)

본 시스템은 데이터 수집, 가상 DB 적재, AI 분석, 외부 서빙 레이어가 철저히 분리된 비동기 호환 아키텍처를 지향합니다.

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

## ✨ 핵심 고도화 기능 (Key Features)

* **RESTful API 웹 서버 전환:** `FastAPI`와 비동기 ASGI 서버 `Uvicorn`을 도입하여 수동 스크립트를 표준 API 엔드포인트(`POST /api/v1/trends/collect`) 구조로 서빙화.
* **로컬 가상 RDB 구축 & 데이터 멱등성(Idempotency) 확보:** `SQLite3`를 연동하여 수집된 뉴스 메타데이터와 AI 분석 리포트 원문을 서버 내부에 구조화된 스키마로 상시 보관. 뉴스 고유 링크(`Link`)를 `UNIQUE` 제약 조건으로 설정하고 `INSERT OR IGNORE` 쿼리를 적용하여 동일 데이터의 반복 적재를 원천 필터링하는 데이터 엔지니어링 파이프라인 구축.
* **대화형 API 명세서(Swagger UI) 제공:** 웹 서버 가동과 동시에 자동으로 빌드되는 인터랙티브 명세서(`/docs`)를 통해 엔드포인트를 실시간으로 테스트 및 모니터링 가능.

---

## 🛠️ 기술 스택 (Tech Stacks)

* **Framework & Web:** `FastAPI`, `Uvicorn`, `Requests`, `Urllib3`
* **Language:** Python 3.11+
* **Database:** `SQLite3` (Embedded RDB)
* **AI & Parsing:** `google-genai`, `feedparser`, `python-dotenv`

---

## 🔥 기술적 도전 및 트러블슈팅 (Technical Challenges & Troubleshooting)

### 1. 외부 서버의 봇 차단(403 Forbidden) 및 SSL 인증서 에러 해결
* **문제 상황:** `requests`를 이용해 외부 RSS를 수집할 때 로컬 환경의 SSL 인증서 검증 이슈와 외부 서버의 크롤링 봇 차단 정책으로 인해 `403 Forbidden` 에러 발생.
* **해결 방법:** `urllib3.disable_warnings()`로 경고를 제어하고 `verify=False` 옵션으로 SSL 장벽을 우회하는 한편, 진짜 브라우저 요청인 것처럼 가공된 `User-Agent` HTTP 마스킹 헤더를 주입해 수집 파이프라인의 안정성 확보.

### 2. 가상 데이터베이스 연동을 통한 데이터 중복 적재 제어 (Data Deduplication)
* **문제 상황:** 동일한 주기나 스케줄러에 의해 API가 다회 호출될 경우, 이미 노션 및 로컬에 존재하는 뉴스가 중복 수집되어 대시보드가 오염되고 LLM API 토큰 비용이 낭비되는 비효율 발견.
* **해결 방법:** 내장 관계형 데이터베이스인 SQLite를 연동하여 `articles` 테이블을 설계하고, 원본 기사 링크에 `UNIQUE` 제약을 부여. 데이터 인서트 시 `INSERT OR IGNORE` 구문을 사용하여 네트워크 통신단이 아닌 데이터베이스 레이어에서 중복 로우(Row)를 완벽하게 걸러내도록 설계 (2회 이상 반복 요청 시 신규 적재 개수 `0`건 로그 반환 보증).

### 3. 멀티 아키텍처 환경을 위한 동적 경로(Dynamic Path Tracking) 추적
* **문제 상황:** 스크립트 실행 위치에 따라 최상위 루트에 배치된 환경 변수 파일(`.env`)이나 로컬 데이터베이스 파일(`tech_trends.db`)의 경로를 파이썬 시스템이 인식하지 못해 키 누락 및 가짜 DB 분산 적재 문제 우려.
* **해결 방법:** `pathlib.Path(__file__).resolve()` 오브젝트를 활용해 메인 서버 파일의 위치를 기준으로 프로젝트 전체 경로를 동적으로 연동(`BASE_DIR`)함으로써, 어떤 환경이나 폴더 내에서 프로세스가 구동되어도 한 곳의 고정된 DB 및 설정 파일과 싱크되도록 정합성 유지.

---

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
