# Spike AI Backend - Architecture Diagrams

## 1. System Flow

This diagram shows the high-level system architecture and how requests flow through the system from API entry to response.

```mermaid
flowchart TB
    subgraph "Client Layer"
        C[HTTP Client]
    end

    subgraph "API Layer"
        direction LR
        E1[POST /query]
        E2[GET /health]
    end

    subgraph "FastAPI Application"
        F[main.py<br/>FastAPI Server]
        M[QueryRequest Model]
    end

    subgraph "Orchestration Layer"
        O[Orchestrator]
        ID{Intent<br/>Detection}
        QD[Query<br/>Decomposition]
    end

    subgraph "Agent Layer"
        AA[Analytics Agent<br/>Tier 1]
        SA[SEO Agent<br/>Tier 2]
        MF[Multi-Agent Fusion<br/>Tier 3]
    end

    subgraph "LLM Layer"
        LC[LiteLLM Client]
        PS[Pydantic Schemas]
    end

    subgraph "External Services"
        GA[(Google Analytics<br/>Data API)]
        GS[(Google Sheets<br/>API)]
        LLM[LiteLLM Proxy<br/>Gemini 2.5 Flash]
    end

    C -->|HTTP Request| E1 & E2
    E1 --> F
    E2 --> F
    F --> M --> O
    O --> ID
    ID -->|ANALYTICS| AA
    ID -->|SEO| SA
    ID -->|BOTH| QD --> MF
    MF --> AA & SA
    AA --> LC
    SA --> LC
    MF --> LC
    LC --> PS
    AA <-->|GA4 Data API| GA
    SA <-->|gspread| GS
    LC <-->|OpenAI Compatible| LLM
    AA & SA & MF -->|QueryResponse| F --> C
```

---

## 2. Agent Interactions

This diagram details how the three agent tiers interact with each other and their respective data sources.

```mermaid
flowchart LR
    subgraph "Input"
        Q[User Query]
        PID[Property ID<br/>Optional]
    end

    subgraph "Tier 1: Analytics Agent"
        direction TB
        A1[Infer GA4 Plan<br/>via LLM]
        A2[Validate Allowlist<br/>Metrics & Dimensions]
        A3[Build RunReportRequest]
        A4[Execute GA4 API Call]
        A5[Summarize Results<br/>via LLM]
        A1 --> A2 --> A3 --> A4 --> A5
    end

    subgraph "Tier 2: SEO Agent"
        direction TB
        S1[Load Spreadsheet<br/>Configs]
        S2[Generate Pandas Code<br/>via LLM]
        S3["Execute Code Sandbox<br/>(exec)"]
        S4[Return Result]
        S1 --> S2 --> S3 --> S4
    end

    subgraph "Tier 3: Multi-Agent Fusion"
        direction TB
        M1[Decompose Query<br/>via LLM]
        M2[Execute Analytics<br/>Sub-Query]
        M3[Execute SEO<br/>Sub-Query]
        M4[Fuse Results<br/>via LLM]
        M1 --> M2 & M3
        M2 & M3 --> M4
    end

    subgraph "Data Sources"
        GA[(GA4 Property)]
        GS[(Google Sheets)]
    end

    Q --> A1 & S1 & M1
    PID --> A3
    A4 <--> GA
    S1 <--> GS
    M2 --> A1
    M3 --> S1
```

### Agent Responsibilities

| Agent | Tier | Data Source | Key Capabilities |
|-------|------|-------------|------------------|
| **Analytics Agent** | 1 | Google Analytics 4 API | - LLM-based query planning<br/>- Metric/Dimension allowlist validation<br/>- Live GA4 data retrieval<br/>- LLM result summarization |
| **SEO Agent** | 2 | Google Sheets (Screaming Frog data) | - Multi-spreadsheet support<br/>- LLM-generated Pandas code<br/>- Sandboxed code execution<br/>- Schema auto-detection |
| **Multi-Agent Fusion** | 3 | Both GA4 + Sheets | - Dynamic query decomposition<br/>- URL path normalization<br/>- Cross-source data matching<br/>- JSON/natural language output |

---

## 3. Orchestrator Routing

This diagram shows the decision-making flow within the orchestrator for routing requests to the appropriate agent(s).

```mermaid
flowchart TD
    START([Incoming Request]) --> PARSE[Parse QueryRequest]
    PARSE --> INTENT{LLM Intent<br/>Classification}
    
    INTENT -->|"IntentClassification.intent"| EVAL{Evaluate<br/>Intent}
    
    EVAL -->|"ANALYTICS"| CHECK_PID{Property ID<br/>Provided?}
    CHECK_PID -->|Yes| ANALYTICS[Route to<br/>Analytics Agent]
    CHECK_PID -->|No| FALLBACK_SEO[Fallback to<br/>SEO Agent]
    
    EVAL -->|"SEO"| SEO[Route to<br/>SEO Agent]
    
    EVAL -->|"BOTH"| DECOMPOSE[Decompose Query<br/>via LLM]
    DECOMPOSE --> PARALLEL[Execute Both<br/>Agents in Parallel]
    
    subgraph "Multi-Agent Flow"
        PARALLEL --> AA_EXEC[Analytics Agent<br/>Sub-Query]
        PARALLEL --> SA_EXEC[SEO Agent<br/>Sub-Query]
        AA_EXEC & SA_EXEC --> FUSE[LLM Fusion<br/>of Results]
    end
    
    EVAL -->|"UNKNOWN"| FALLBACK{Property ID<br/>Provided?}
    FALLBACK -->|Yes| ANALYTICS
    FALLBACK -->|No| SEO
    
    ANALYTICS --> RESPONSE([JSON Response])
    FALLBACK_SEO --> RESPONSE
    SEO --> RESPONSE
    FUSE --> RESPONSE

    style START fill:#e1f5fe
    style RESPONSE fill:#c8e6c9
    style INTENT fill:#fff9c4
    style DECOMPOSE fill:#fff9c4
    style FUSE fill:#fff9c4
```

### Routing Decision Matrix

| Detected Intent | Property ID | Action |
|-----------------|-------------|--------|
| `ANALYTICS` | ✅ Provided | Route to Analytics Agent |
| `ANALYTICS` | ❌ Missing | Fallback to SEO Agent |
| `SEO` | Any | Route to SEO Agent |
| `BOTH` | ✅ Provided | Execute both agents + LLM fusion |
| `BOTH` | ❌ Missing | Execute SEO only (Analytics errors gracefully) |
| `UNKNOWN` | ✅ Provided | Fallback to Analytics Agent |
| `UNKNOWN` | ❌ Missing | Fallback to SEO Agent |

### Structured LLM Schemas Used

```mermaid
classDiagram
    class IntentClassification {
        +intent: ANALYTICS | SEO | BOTH
    }
    
    class DecomposedQuery {
        +analytics_query: str
        +seo_query: str
        +output_format: json | natural_language
        +limit: int = 10
    }
    
    class GA4QueryPlan {
        +metrics: List~str~
        +dimensions: List~str~
        +date_ranges: List~DateRange~
        +order_by: Optional~List~OrderByField~~
    }
    
    class SEOCodeResponse {
        +code: str
    }
    
    IntentClassification <-- Orchestrator : uses
    DecomposedQuery <-- Orchestrator : uses
    GA4QueryPlan <-- AnalyticsAgent : uses
    SEOCodeResponse <-- SEOAgent : uses
```

---

## 4. Complete Request Lifecycle

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant FastAPI as FastAPI Server
    participant Orch as Orchestrator
    participant LLM as LiteLLM Client
    participant AA as Analytics Agent
    participant SA as SEO Agent
    participant GA4 as Google Analytics
    participant GS as Google Sheets

    Client->>FastAPI: POST /query {query, propertyId?}
    FastAPI->>Orch: route_request(QueryRequest)
    
    rect rgb(255, 249, 196)
        Note over Orch,LLM: Intent Detection
        Orch->>LLM: chat_structured(IntentClassification)
        LLM-->>Orch: {intent: "BOTH"}
    end
    
    rect rgb(255, 249, 196)
        Note over Orch,LLM: Query Decomposition
        Orch->>LLM: chat_structured(DecomposedQuery)
        LLM-->>Orch: {analytics_query, seo_query, ...}
    end
    
    par Analytics Flow
        Orch->>AA: process_query(analytics_query, propertyId)
        AA->>LLM: chat_structured(GA4QueryPlan)
        LLM-->>AA: {metrics, dimensions, date_ranges}
        AA->>AA: Validate against allowlist
        AA->>GA4: RunReportRequest
        GA4-->>AA: Report data
        AA->>LLM: Summarize results
        LLM-->>AA: Summary text
        AA-->>Orch: analytics_result
    and SEO Flow
        Orch->>SA: process_query(seo_query)
        SA->>LLM: chat_structured(SEOCodeResponse)
        LLM-->>SA: {code: "pandas code..."}
        SA->>SA: exec(code) in sandbox
        SA-->>Orch: seo_result
    end
    
    rect rgb(200, 230, 201)
        Note over Orch,LLM: Result Fusion
        Orch->>LLM: chat(fusion_prompt)
        LLM-->>Orch: Fused answer
    end
    
    Orch-->>FastAPI: answer string
    FastAPI-->>Client: {answer: "..."}
```

---

## Key Architecture Highlights

| Component | Technology | Purpose |
|-----------|------------|---------|
| **API Framework** | FastAPI | Async HTTP server with Pydantic validation |
| **LLM Integration** | LiteLLM + OpenAI SDK | Unified interface for Gemini 2.5 Flash |
| **Structured Outputs** | Pydantic + JSON Schema | Type-safe, validated LLM responses |
| **Analytics API** | google-analytics-data | GA4 Data API v1beta client |
| **Sheets API** | gspread + oauth2client | Google Sheets access via service account |
| **Data Processing** | Pandas | DataFrame manipulation for SEO analysis |
