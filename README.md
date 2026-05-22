# 🤖 Real-Time Tech Trend Analysis & Automated Newsletter Agent
> **FastAPI, SQLite 및 APScheduler 기반의 무인 자동화 테크 뉴스레터 파이프라인 시스템**

본 프로젝트는 외부 데이터 소스(RSS)로부터 실시간 기술 트렌드 데이터를 안정적으로 수집(Data Ingestion)하고, 서버 내부의 로컬 가상 관계형 데이터베이스(SQLite RDB)를 통해 데이터 멱등성(Idempotency)을 확보하며, 생성형 AI(Gemini Pro)와 백그라운드 스케줄러를 결합해 무인 배치(Batch) 환경에서 뉴스레터를 자동 생성 및 노션 데이터베이스로 자동 서빙하는 **안정적인 엔드투엔드(End-to-End) 데이터 파이프라인 백엔드 시스템**입니다.

기존의 단순 수동 실행 스크립트 형태에서 **RESTful API 웹 서버 및 백그라운드 워커 아키텍처**로 완전히 진화시켜 인프라 확장성을 확보했으며, 도커(Docker) 기반의 컨테이너라이징을 통해 클라우드 배포 최적화를 달성했습니다.

📅 **실시간 적재 대시보드:** [👉 본인의 노션 데이터베이스 공유 링크를 여기에 넣어주세요]

---

## 🏗️ 시스템 아키텍처 & 데이터 흐름 (Architecture & Data Flow)

본 시스템은 데이터 수집(Ingestion), 자체 DB 검증(Storage), AI 분석/가공(Processing), 외부 서비스 제공(Serving) 레이어가 철저히 분리된 디커플링(Decoupled) 구조를 지향합니다.

[인프라 트리거 및 스케줄러 라인]
⏰ Background Scheduler (APScheduler) ──(1분 주기/매일 정기 배치)──┐
▼
[웹 엔드포인트 라인]                                             [ Core Pipeline ]
👤 Client / Tester ──(HTTP POST)──> [ FastAPI Server ] ──────> 1. Ingestion (urllib3)
2. Deduplication (SQLite)
3. LLM Processing (Gemini)
4. Serving (Notion API)

### 🔄 Detailed Data Pipeline Flow
1. **Data Ingestion**: `urllib3` 및 `feedparser`를 활용하여 외부 기술 RSS 피드에서 실시간 뉴스 메타데이터 수집. (HTTP 마스킹 헤더 주입으로 보안 장벽 해제)
2. **Data Deduplication**: 데이터 유입 시 `SQLite3`의 `UNIQUE` 제약 조건을 통해 기존에 적재된 기사인지 검증 후, 신규 로우(Row)만 가상 DB에 보관 (**데이터 멱등성 보증**).
3. **AI Processing**: 정제된 뉴스 컨텍스트를 기반으로 `Gemini 2.5 Flash` 모델에 전문 테크 저널리스트 페르소나와 마크다운 구조화 프롬프트를 주입하여 리포트 생성.
4. **Data Serving**: 생성된 롱폼 마크다운 본문을 노션 블록 API 스키마 양식에 맞게 JSON 페이로드로 가공 후, `Notion Web API` 엔드포인트로 전송하여 최종 대시보드 적재.

---

## ✨ 핵심 인프라 기능 (Key Features)

* **RESTful API 웹 서버 전환:** `FastAPI`와 비동기 ASGI 서버 `Uvicorn`을 도입하여 수동 스크립트를 표준 API 엔드포인트(`POST /api/v1/trends/collect`) 구조로 서빙화.
* **로컬 가상 RDB 구축 & 데이터 멱등성(Idempotency) 확보:** `SQLite3`를 연동하여 수집된 뉴스 메타데이터와 AI 분석 리포트 원문을 서버 내부에 구조화된 스키마로 상시 보관. 뉴스 고유 링크(`Link`)를 `UNIQUE` 키로 설정하고 `INSERT OR IGNORE` 쿼리를 적용하여 동일 데이터의 반복 적재를 원천 필터링 (LLM API 토큰 비용 낭비 방지).
* **무인 배치 자동화 시스템:** 백그라운드 스케줄러(`APScheduler`) 탑재로 365일 정해진 타임라인에 휴먼 에러 없이 파이프라인이 자동 구동되는 완전 자동화 달성.
* **Docker 가상화 기술 적용:** 배포 환경 격리를 위한 `Dockerfile` 및 `.dockerignore` 인프라 코딩을 완료하여 컨테이너 기반 클라우드(AWS, GCP 등) 배포 최적화.
* **대화형 API 명세서(Swagger UI) 제공:** 웹 서버 가동과 동시에 자동으로 빌드되는 인터랙티브 명세서(`/docs`)를 통해 엔드포인트를 실시간으로 테스트 및 모니터링 가능.

---

## 🛠️ 기술 스택 (Tech Stacks)

* **Backend & Infrastructure:** `FastAPI`, `Uvicorn`, `APScheduler`, `Docker`
* **Language & Database:** Python 3.11+, `SQLite3` (Embedded RDB)
* **Third-Party API & Parsing:** `google-genai`, `feedparser`, `requests`, `python-dotenv`, `urllib3`

---

## 🔥 기술적 도전 및 트러블슈팅 (Technical Challenges & Troubleshooting)

### 1. 외부 서버의 봇 차단(403 Forbidden) 및 SSL 인증서 에러 해결
* **문제 상황:** `requests`를 이용해 외부 RSS를 수집할 때 로컬 환경의 SSL 인증서 미검증 이슈와 외부 서버의 크롤링 봇 차단 정책으로 인해 `403 Forbidden` 에러 발생.
* **해결 방법:** `urllib3.disable_warnings()`로 경고를 제어하고 `verify=False` 옵션으로 SSL 장벽을 우회하는 한편, 진짜 윈도우 크롬 브라우저 요청인 것처럼 가공된 `User-Agent` 및 `Accept` HTTP 마스킹 헤더를 주입해 수집 파이프라인의 안정성 확보.

### 2. 가상 데이터베이스 연동을 통한 데이터 중복 적재 제어 (Data Deduplication)
* **문제 상황:** 동일한 주기나 스케줄러에 의해 API가 다회 호출될 경우, 이미 노션 및 로컬에 존재하는 뉴스가 중복 수집되어 대시보드가 오염되고 LLM API 토큰 비용이 낭비되는 비효율 발견.
* **해결 방법:** 내장 관계형 데이터베이스인 SQLite를 연동하여 `articles` 테이블을 설계하고, 원본 기사 링크에 `UNIQUE` 제약을 부여. 데이터 인서트 시 `INSERT OR IGNORE` 구문을 사용하여 네트워크 통신단이 아닌 데이터베이스 레이어에서 중복 로우(Row)를 완벽하게 걸러내도록 설계 (2회 이상 반복 요청 시 신규 적재 개수 `0`건 로그 반환 보증).

### 3. 멀티 아키텍처 환경을 위한 동적 경로(Dynamic Path Tracking) 추적
* **문제 상황:** 프로젝트의 디렉터리 구조상 실행 스크립트가 하위 폴더에 위치함에 따라, 최상위 루트에 배치된 환경 변수 파일(`.env`)이나 로컬 데이터베이스 파일(`tech_trends.db`)의 경로를 파이썬 시스템이 인식하지 못해 키 누락 및 가짜 DB 분산 적재 문제 우려.
* **해결 방법:** `pathlib.Path(__file__).resolve()` 오브젝트를 활용해 메인 서버 파일의 위치를 기준으로 프로젝트 전체 경로를 동적으로 연동(`BASE_DIR`)함으로써, 어떤 환경이나 폴더 내에서 프로세스가 구동되어도 한 곳의 고정된 DB 및 설정 파일과 싱크되도록 정합성 유지.

### 4. 노션 API의 단일 텍스트 블록 글자 수 제한(2000자) 대응
* **문제 상황:** 제미나이 에이전트가 생성한 롱폼(Long-form) 뉴스레터 본문이 노션 API의 단일 텍스트 블록 제한(2000자)을 초과하여 전송 시 400 에러 발생 위험 인지.
* **해결 방법:** 데이터의 유실을 막고 안정적인 서빙을 위해 슬라이싱(`report_content[:2000]`) 레이어를 추가하여 예외 처리 메커니즘 구축. (향후 2000자 단위 문자열 청킹 및 멀티 블록 적재 로직으로 고도화 예정)

---

## 🚀 배포 및 시작 가이드 (How to Run with Docker)

### 1. 로컬 환경 변수 구성 (`.env`)
프로젝트 최상위 루트에 `.env` 파일을 생성하고 발급받은 키를 매핑합니다.
```text
GEMINI_API_KEY=your_gemini_api_key
NOTION_TOKEN=your_notion_integration_token
NOTION_DATABASE_ID=your_notion_database_id
<<<<<<< HEAD

2. 패키지 설치 및 웹 서버 구동
=======
```
2. 도커 컨테이너 빌드 및 실행 (Dockerizing)
# 1. 도커 이미지 빌드
docker build -t tech-trend-agent .

# 2. 환경변수 파일을 주입하여 컨테이너 독립 구동 (배포 모드)
docker run -d -p 8000:8000 --env-file .env --name trend-bot tech-trend-agent

# 3. API 명세서 및 파이프라인 테스트
메인 API 헬스체크: http://127.0.0.1:8000/
<<<<<<< HEAD
인터랙티브 Swagger 대시보드: http://127.0.0.1:8000/docs
=======
