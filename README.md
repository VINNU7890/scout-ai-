<div align="center">

# 🦅 ScoutAI
### Autonomous AI Competitor & Market Intelligence Agent
**Self-directed multi-agent market research pipeline with cyclic verification, dual-source vector RAG, and zero hallucinations.**

[![Live Demo](https://img.shields.io/badge/Live_Demo-scoutai--agent.embarko.app-6366F1?style=for-the-badge&logo=fastapi&logoColor=white)](https://scoutai-agent.embarko.app)
[![Docker Hub](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Cyclic_Agent-FF6F00?style=for-the-badge&logo=diagram-project&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

<p align="center">
  <a href="#-live-demo">Live Demo</a> •
  <a href="#-key-capabilities">Key Capabilities</a> •
  <a href="#-system-architecture">Architecture</a> •
  <a href="#-quickstart">Quickstart</a> •
  <a href="#-anti-hallucination-engine">Anti-Hallucination</a> •
  <a href="#-api-reference">API Reference</a> •
  <a href="#-deployment">Deployment</a>
</p>

</div>

---

## 🌐 Live Demo

Experience ScoutAI live on the cloud:

👉 **[https://scoutai-agent.embarko.app](https://scoutai-agent.embarko.app)**

*Try pre-loaded scenarios such as `BitDelta India vs CoinDCX, CoinSwitch, ZebPay & Mudrex` or test your own competitive queries with live SSE streaming!*

---

## 🌟 Key Capabilities

- **Cyclic LangGraph Orchestration**: 6-node state graph (`planner` &rarr; `[web_researcher || doc_researcher]` &rarr; `analyst` &rarr; `writer` &rarr; `verifier` &rarr; `writer` | `END`).
- **Grounded LLM-as-Judge Verifier**: Cross-checks generated factual claims against retrieved verbatim evidence quotes (&le;25 words). Unsupported claims trigger an automated feedback loop back to the writer node.
- **Strict "Not Found" Policy**: Never extrapolates or fabricates metrics. If a data point is unconfirmed by sources, the agent explicitly marks it as `"Not found"`.
- **Dual Retrieval Engine**:
  - **Live Web Research**: DuckDuckGo search (`ddgs`) with zero API key required, or optional Tavily API integration.
  - **Document Vector RAG**: Upload internal pitch decks, battlecards, and reports (PDF, DOCX, TXT, MD) embedded into a persistent **ChromaDB** vector store.
- **Interactive Full-Stack SPA**:
  - **Interactive Citation Popovers**: Hover over `[1]`, `[2]` chips to view the source title, domain, and verbatim quote.
  - **Cross-Entity Comparison Matrix**: Sticky-header grid with click-to-inspect evidence modals.
  - **Radar & Bar Scorecards**: Recharts radar charts visualizing aspect scores across entities.
  - **Grounded Q&A Chat (`/api/runs/{id}/ask`)**: Ask follow-up questions answered strictly using the run's findings.
- **Multi-Format Executive Exports**: One-click download as **Markdown**, styled **PDF** (via ReportLab), or Microsoft **DOCX** (via python-docx).
- **Zero-Dependency Demo Mode**: Set `DEMO_MODE=true` to replay a complete recorded scenario with zero API keys needed.
- **Single Deployable Container**: Multi-stage Dockerfile packages the React SPA directly into FastAPI for instant hosting on Render, Railway, Embarko, or AWS/GCP.

---

## 🏗 System Architecture

```mermaid
flowchart TD
    User([User Query + Uploaded Documents]) --> FastAPIServer[FastAPI Application Server]
    FastAPIServer --> Orchestrator[Research Service Coordinator]

    subgraph LangGraph Multi-Node Pipeline
        Orchestrator --> Planner[1. Planner Node<br/>Extract 6 Entities & 8 Comparison Aspects]
        
        Planner -->|Generate Web Queries| WebNode[2. Web Researcher Node<br/>DuckDuckGo / Tavily + trafilatura<br/>SSRF Protected & Cached]
        Planner -->|Vector Similarity Query| DocNode[3. Document Researcher Node<br/>ChromaDB Vector Store<br/>PDF, DOCX, TXT, MD Chunks]

        WebNode --> FindingsCatalog[(Evidence Catalog: Bounded &le;25 Word Quotes)]
        DocNode --> FindingsCatalog

        FindingsCatalog --> AnalystNode[4. Analyst Node<br/>SWOT, Aspect Scoring 1-5, Matrices]
        AnalystNode --> WriterNode[5. Writer Node<br/>Draft Executive Brief & Inline [N] Citations]

        WriterNode --> VerifierNode[6. Verifier Node<br/>LLM-as-Judge Grounding Check]

        VerifierNode -->|Unsupported Claims Detected & Cycles < 2| FeedbackLoop[Verification Rewrite Loop]
        FeedbackLoop --> WriterNode
        VerifierNode -->|Verification Passed or Max Cycles Reached| FinalArtifacts([Verified Final Report])
    end

    FinalArtifacts --> SSEStream[Live Server-Sent Events SSE]
    FinalArtifacts --> SQLiteDB[(Persistent SQLite Database)]
    FinalArtifacts --> ExportEngine[Export Service: MD / PDF / DOCX]
    FinalArtifacts --> RAGAskChat[Grounded Follow-up Q&A API]
```

### Node Specifications

| Node | Name | Primary Task | Output Artifact |
|---|---|---|---|
| **1** | `planner` | Deconstructs user query into entities (max 6), aspects (max 8), and targeted search questions. | `ResearchPlan` |
| **2** | `web_researcher` | Executes parallel search queries with SSRF validation, fetches page text, and extracts verbatim quotes (&le;25 words). | `List[Finding]` (web) |
| **3** | `doc_researcher` | Queries ChromaDB embeddings for chunks related to target entities and aspects. | `List[Finding]` (doc) |
| **4** | `analyst` | Aggregates findings into structured comparison matrices, SWOT analysis, and 1-5 aspect scores with rationales. | `CompetitorProfile[]` |
| **5** | `writer` | Drafts executive summary (&le;150w), 5 key takeaways, competitor profiles, and GTM recommendations with `[N]` citations. | `Report` |
| **6** | `verifier` | Evaluates claims against source evidence quotes. If severity is `"unsupported"`, rejects and routes back to `writer`. | `VerificationResult` |

---

## 🛡 Anti-Hallucination Engine

ScoutAI is engineered specifically to prevent the common hallucination issues of generative AI:

```
[Retrieved Source HTML]
         │
         ▼ (trafilatura clean text extraction)
[Verbatim Evidence Snippet] ───► Maximum 25 words directly from source
         │
         ▼ (Deterministic Citation Index)
[Inline Citation Token [3]] ───► Tied to Source URL & Timestamp
         │
         ▼ (LLM-as-Judge Cross-Examination)
[Verifier Judgment] ─────────► "Passed" or "Unsupported"
```

1. **Evidence-First Extraction**:
   Neither raw unparsed HTML nor loose LLM summaries are passed to the writer. Every fact is stored as an atomic `Finding`:
   - Specific factual claim.
   - **Verbatim evidence quote (&le; 25 words)** directly clipped from source text.
   - Source URL or document filename + page number.
2. **Deterministic Citation Catalog**:
   Citations are sequentially indexed `[1], [2], ...` and mapped strictly to sources backing confirmed findings.
3. **LLM-as-Judge Verifier Loop**:
   The `verifier` node reviews the drafted report alongside all extracted findings. If an assertion is judged unsupported by the verbatim quote, the verifier appends actionable feedback and LangGraph re-routes execution back to the `writer` node.
4. **Mandatory "Not Found" Directive**:
   System prompts enforce an explicit refusal policy:
   > *"If an aspect or data point for a competitor is not explicitly confirmed by retrieved sources, write 'Not found'. Never infer, extrapolate, or invent metrics."*

---

## 🚀 Quickstart

### Option 1: Run Locally (Fastest)

#### Prerequisites
- Python 3.11 or 3.12
- Node.js 18+ (for frontend)

#### Step 1: Clone Repository
```bash
git clone https://github.com/your-username/scoutai.git
cd scoutai
```

#### Step 2: Backend Setup
```bash
# Create and activate Python virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

# Install backend package
pip install -e ./backend
```

#### Step 3: Frontend Build
```bash
cd frontend
npm install
npm run build
cd ..
```

#### Step 4: Configure Environment & Run
Copy the example environment configuration:
```bash
cp .env.example .env
```
Edit `.env` and add your Google Gemini API key:
```env
GEMINI_API_KEY=AIzaSy...
DEMO_MODE=false
```

Start the application:
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser!

> 💡 **Tip:** Leave `DEMO_MODE=true` in `.env` to test the full interface with a recorded BitDelta run with zero API keys required.

---

### Option 2: Docker / Docker Compose

Build and start the self-contained container in a single command:

```bash
docker-compose up --build
```
Open **[http://localhost:8000](http://localhost:8000)**.

To run with your own Gemini API key via Docker CLI:
```bash
docker build -t scoutai:latest .
docker run -p 8000:8000 \
  -e GEMINI_API_KEY="your-gemini-key" \
  -e DEMO_MODE="false" \
  scoutai:latest
```

---

## 🔑 Google Gemini Free Tier Optimization

ScoutAI is designed to run completely inside the free tier of **Google Gemini 2.5 Flash** ($0.00 cost):

| Resource Limit | Gemini 2.5 Flash Free Quota | ScoutAI Guardrails & Optimizations |
|---|---|---|
| **Requests / Min (RPM)** | 15 RPM | Built-in sliding-window rate-limiter + global concurrency semaphore |
| **Tokens / Min (TPM)** | 1,000,000 TPM | Web pages truncated to 15,000 chars, structured Pydantic outputs |
| **Requests / Day (RPD)** | 1,500 RPD | 24-hour persistent SQLite caching for search queries and web fetches |
| **Credit Card** | Not required | Free forever via [Google AI Studio](https://aistudio.google.com/) |

### Getting a Free Key:
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Click **Get API key** &rarr; **Create API key**.
3. Paste the key into `GEMINI_API_KEY` in `.env`.

---

## 📊 Comparison & Scorecard Views

````carousel
```
┌────────────────────────────────────────────────────────────────────────┐
│                        SCOUTAI COMPARISON MATRIX                       │
├────────────────────┬───────────────────────┬───────────────────────────┤
│ Aspect             │ BitDelta              │ CoinDCX                   │
├────────────────────┼───────────────────────┼───────────────────────────┤
│ FIU-IND Compliance │ Registered [1]        │ Registered (ISO 27001)[2] │
│ Maker/Taker Fees   │ 0.1% maker / 0.1% [3] │ 0.2% standard spot [4]    │
│ Proof of Reserves  │ Monthly audits [5]    │ Public Merkle-tree [6]    │
│ INR Payment Rails  │ IMPS / NEFT / UPI [7] │ Bank Transfer / UPI [8]   │
└────────────────────┴───────────────────────┴───────────────────────────┘
```
<!-- slide -->
```
┌────────────────────────────────────────────────────────────────────────┐
│                    MULTI-ENTITY RADAR SCORECARD (1-5)                  │
├────────────────────────────────────────────────────────────────────────┤
│                     [Compliance & Trust]                               │
│                             5.0                                        │
│                            /   \                                       │
│          [GTM Strategy]   /     \   [Product Features]                 │
│                 4.0 ─────●       ●───── 4.5                            │
│                  \              /                                      │
│                   \            /                                       │
│                    ●──────────●                                        │
│              [Pricing/Fees]  [Security]                                │
│                   4.2           4.8                                    │
│                                                                        │
│    Legend: ─── BitDelta    ┄┄┄ CoinDCX    ┈┈┈ CoinSwitch               │
└────────────────────────────────────────────────────────────────────────┘
```
````

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/runs` | Initiate a new autonomous research run (`query`, `options`, `document_ids`). |
| `GET` | `/api/runs` | List all historical research runs with status and timestamps. |
| `GET` | `/api/runs/{id}` | Retrieve run status, plan, report, findings, and verification results. |
| `GET` | `/api/runs/{id}/stream` | Subscribe to live Server-Sent Events (SSE) progress stream. |
| `POST` | `/api/runs/{id}/ask` | Interactive grounded Q&A answering follow-up questions from findings. |
| `GET` | `/api/runs/{id}/export?format={md\|pdf\|docx}` | Export report as Markdown, ReportLab PDF, or Word DOCX. |
| `POST` | `/api/documents` | Upload internal knowledge document (PDF, DOCX, TXT, MD) to ChromaDB. |
| `DELETE` | `/api/runs/{id}` | Delete research run and purge associated ChromaDB vector collections. |
| `GET` | `/api/health` | System health check (Gemini config, search provider, demo mode). |

---

## ⚙️ Configuration Reference

| Environment Variable | Default | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | `""` | Google Gemini API key from Google AI Studio |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model variant (`gemini-2.5-flash` or `gemini-1.5-pro`) |
| `DEMO_MODE` | `true` | Offline demo mode replaying recorded BitDelta scenario |
| `SEARCH_PROVIDER` | `ddg` | Web search provider (`ddg` = DuckDuckGo, `tavily` = Tavily) |
| `TAVILY_API_KEY` | `""` | Optional Tavily API key |
| `LANGSMITH_API_KEY` | `""` | Optional LangSmith key for tracing agent transitions |
| `PORT` | `8000` | Port for FastAPI server |
| `DATABASE_URL` | `sqlite:///./scoutai.db` | SQLAlchemy SQLite database URL |
| `CHROMA_DIR` | `./data/chroma` | Directory for persistent ChromaDB embeddings |
| `UPLOAD_DIR` | `./data/uploads` | Directory for temporary uploaded files |
| `CORS_ORIGINS` | `*` | Allowed CORS origins (comma-separated or `*`) |
| `RATE_LIMIT_PER_MINUTE`| `60` | Per-IP sliding-window rate limit |
| `MAX_AGENT_CYCLES` | `2` | Maximum retry cycles between verifier and writer |

---

## 🧪 Testing & Code Quality

ScoutAI includes automated unit, integration, and linting suites:

```bash
# Run backend pytest suite (21 tests)
pytest -v backend/tests

# Run ruff linter & formatting check
ruff check backend
ruff format --check backend

# Run frontend Vitest suite (7 component tests)
cd frontend
npx vitest run

# Run production Vite build
npm run build
```

**Test Coverage Summary:**
- `test_agent.py`: LangGraph multi-node graph execution with simulated LLM & verifier cycle.
- `test_api.py`: FastAPI endpoints, health check, run lifecycle, and export generation.
- `test_url_safety.py`: SSRF security, private IP range rejection, and scheme validation.
- `test_citations.py`: Citation indexing, source mapping, and catalog creation.
- `Timeline.test.tsx`, `CitationHover.test.tsx`, `ComparisonTable.test.tsx`: React UI component tests.

---

## 🚢 Cloud Deployment

### 1. Deploy to Embarko
```bash
# Package deployable bundle (no Dockerfile)
tar -czf scoutai_deploy.tar.gz \
  --exclude=node_modules --exclude=.git --exclude='.env*' \
  --exclude=venv --exclude=.venv --exclude=__pycache__ --exclude='*.db' .

# Deploy anonymously
curl -sS -X POST 'https://ship.embarko.ai/apps' \
  -H 'X-App-Name: scoutai-agent' \
  -H 'X-Agent-Name: antigravity' \
  -F 'source=@scoutai_deploy.tar.gz'
```

### 2. Deploy to Render (One-Click Blueprint)
Push this repository to GitHub and connect via [Render Blueprints](https://render.com/):
- Render automatically uses the included [`render.yaml`](./render.yaml).
- Builds the multi-stage Dockerfile and deploys on a free web service.

### 3. Deploy to Railway
- Select **Deploy from GitHub repo**.
- Railway automatically detects [`Dockerfile`](./Dockerfile) and provisions the service.

---

## 💼 Resume & Interview Talking Points

### Resume Bullets
- **Architected an autonomous multi-agent competitor research system** using **LangGraph**, **FastAPI**, and **React 18**, synthesizing 10-page market intelligence reports with zero hallucinations.
- **Implemented a cyclic LLM-as-judge verification pipeline** that cross-checks factual assertions against verbatim source quotes (&le;25 words), rejecting unsupported claims through an automated feedback loop.
- **Engineered a dual-retrieval engine** fusing live DuckDuckGo web scraping (SSRF-protected, robots.txt compliant) with persistent **ChromaDB vector RAG** for customer internal battlecards.
- **Developed a production full-stack SPA** featuring real-time Server-Sent Events (SSE) streaming, Recharts multi-entity radar charts, sticky comparison matrices, and multi-format exports (Markdown, ReportLab PDF, and DOCX).

### Architectural Highlights for Interviews
- **SSRF Defense**: `url_safety.py` resolves domain DNS records prior to connection, strictly preventing attacks on private subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`, `169.254.169.254`).
- **SQLite Concurrency with NullPool**: Handled async SSE streaming alongside SQLite by configuring SQLAlchemy's `poolclass=NullPool`, eliminating Windows file-lock race conditions.
- **Deterministic RAG Grounding**: Chose to extract discrete `Finding` objects with bounded 25-word evidence snippets rather than passing raw multi-megabyte HTML dumps into downstream LLM prompts.

---

## 📄 License

Distributed under the MIT License. See [LICENSE](file:///c:/Users/Lenovo/Desktop/research%20agents/LICENSE) for more details.
