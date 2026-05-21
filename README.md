# 🤖 Real-Time Tech Trend Analysis & Automated Newsletter Agent
> **실시간 IT 뉴스 트렌드 수집 및 Gemini 에이전트 기반 노션 자동 아카이빙 파이프라인**

본 프로젝트는 외부 데이터 소스(RSS)로부터 실시간 기술 트렌드 데이터를 안정적으로 수집(Data Engineering)하고, 생성형 AI(Gemini Pro)를 활용해 전문적인 테크 뉴스레터 콘텐츠로 가공한 뒤, B2B 업무 생산성 도구(Notion Database)로 자동 서빙(Backend)하는 **End-to-End 데이터 파이프라인 시스템**입니다.

현재 백엔드 및 데이터 엔지니어링의 핵심 MVP 레이어가 구현되어 있으며, 향후 인프라 확장(FastAPI, Docker, Apache Airflow)을 염두에 둔 아키텍처로 설계되었습니다.

📅 **실시간 적재 대시보드:** [👉 본인의 노션 데이터베이스 공유 링크를 여기에 넣어주세요]

---

## 🏗️ 시스템 아키텍처 (Architecture)

프로젝트는 데이터 수집, AI 분석/가공, 최종 서빙의 3단계 디커플링(Decoupled) 구조로 동작합니다.

[1단계: Data Ingestion]      [2단계: AI Agentic Workflow]    [3단계: Data Serving]
한겨레 Science RSS         Google Gemini 2.5 Flash          Notion Web API
(urllib3/feedparser)   ->  (Prompt Engineering/JSON)  ->  (Requests/Data Schema)
│                             │                              │
브라우저 가면 변장                테크 저널리스트 페르소나          API 규격 매핑 및
& SSL 인증서 우회                 및 마크다운 리포트 생성           2000자 청크 제한 대응

---

## ✨ 핵심 기능 (Key Features)

* **안정적인 데이터 인제스션(Ingestion):** 외부 RSS 피드의 보안 장벽(SSL 인증서) 및 봇 차단 정책(403 Forbidden)을 우회하는 견고한 크롤링 파이프라인 구축
* **Agentic 콘텐츠 생성:** 단순 요약을 넘어 현업 키워드(Green IT, AI4S, 디지털 트윈 등)를 도출하고 백엔드/DE 시각의 인사이트를 녹여내는 프롬프트 엔지니어링 적용
* **구조화된 데이터 아카이빙:** 제미나이의 출력 데이터를 노션 API 스키마(`properties`, `children` 블록)에 맞게 정제하여 데이터베이스 레코드로 자동 적재

---

## 🛠️ 기술 스택 (Tech Stacks)

* **Language:** Python 3.11+
* **Libraries:** `google-genai`, `feedparser`, `requests`, `python-dotenv`, `urllib3`
* **Target Platform:** Notion Web API, Google AI Studio (Gemini)

---

## 🔥 기술적 도전 및 트러블슈팅 (Technical Challenges & Troubleshooting)

### 1. 외부 서버의 봇 차단(403 Forbidden) 및 SSL 인증서 에러 해결
* **문제 상황:** `requests`와 `urllib`을 이용해 외부 RSS를 수집할 때, 로컬 환경의 SSL 인증서 미검증 이슈와 외부 서버의 크롤링 봇 차단 정책으로 인해 `400 Bad Request` 및 `403 Forbidden` 에러 발생.
* **해결 방법:** * `urllib3.disable_warnings()`를 통해 인스큐어 요청 경고를 제어하고 `verify=False` 옵션으로 SSL 장벽 우회.
  * 서버가 실제 브라우저의 요청으로 인식하도록 `User-Agent`, `Accept-Language`를 포함한 가짜 HTTP 헤더(Masking Header)를 주입하여 파이프라인의 안정성 확보.

### 2. .env 환경 변수 경로 인식 문제 해결 (Path Dynamic Tracking)
* **문제 상황:** 프로젝트의 디렉터리 구조상 실행 스크립트가 하위 폴더(`fetch_news/`)에 위치함에 따라, 최상위 루트에 있는 `.env` 보안 키 파일을 `load_dotenv()`가 인식하지 못해 API Key 누락 에러 발생.
* **해결 방법:** `pathlib.Path(__file__).resolve()`를 활용해 현재 스크립트의 절대 경로를 동적으로 추적한 뒤, 부모 폴더의 `.env` 경로를 명시적으로 지정(`dotenv_path = BASE_DIR / '.env'`)하여 실행 위치에 구애받지 않는 안전한 환경 변수 로드 로직 구현.

### 3. 노션 API의 단일 텍스트 블록 글자 수 제한(2000자) 대응
* **문제 상황:** 제미나이 에이전트가 생성한 롱폼(Long-form) 뉴스레터 본문이 노션 API의 단일 텍스트 블록 제한(2000자)을 초과하여 전송 시 400 에러 발생 위험 인지.
* **해결 방법:** 데이터의 유실을 막고 안정적인 서빙을 위해 슬라이싱(`report_content[:2000]`) 레이어를 추가하여 예외 처리 메커니즘 구축. (향후 2000자 단위 문자열 청킹 및 멀티 블록 적재 로직으로 고도화 예정)

---

## 🚀 시작 가이드 (How to Run)

### 1. 환경 변수 세팅 (`.env`)
프로젝트 최상위 루트에 `.env` 파일을 생성하고 아래 키를 입력합니다.
```text
GEMINI_API_KEY=your_gemini_api_key
NOTION_TOKEN=your_notion_integration_token
NOTION_DATABASE_ID=your_notion_database_id

2. 패키지 설치 및 실행

pip install google-genai feedparser requests python-dotenv urllib3
python ./fetch_news/fetch_news.py