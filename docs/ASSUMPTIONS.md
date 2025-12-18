# Assumptions & Open Questions

This document outlines the assumptions made during implementation and open questions that may require clarification for production deployment.

---

## Table of Contents

1. [Core Assumptions](#core-assumptions)
2. [Technical Design Decisions](#technical-design-decisions)
3. [Known Limitations](#known-limitations)
4. [Open Questions](#open-questions)
5. [Edge Cases & Error Handling](#edge-cases--error-handling)

---

## Core Assumptions

### Authentication & Credentials

| Assumption | Rationale | Impact if False |
|------------|-----------|-----------------|
| **Single `credentials.json`** serves both GA4 and Google Sheets APIs | The hackathon requires evaluator-replaceable credentials; a single file simplifies this requirement | Would need separate credential loading logic |
| **Service Account has necessary permissions** for both GA4 Data API and Sheets API | Follows Google Cloud IAM best practices; sheet is shared with service account email | API calls will fail with 403 errors |
| **`credentials.json` is at project root** as specified by hackathon requirements | Matches evaluation criteria for easy replacement | Application won't start |

### LiteLLM Proxy

| Assumption | Rationale | Impact if False |
|------------|-----------|-----------------|
| **LiteLLM proxy at `http://3.110.18.218`** is accessible | Hackathon-provided endpoint | LLM calls fail; system returns errors for all queries |
| **`gemini-2.5-flash` model** is available and sufficient | Listed as available model in hackathon docs | Would need model fallback logic |
| **$100 budget** is adequate for evaluation | Per hackathon allocation | Rate limits / budget exhaustion possible |

### Data Sources

| Assumption | Rationale | Impact if False |
|------------|-----------|-----------------|
| **Google Sheets contain Screaming Frog exports** with standard column structures | Hackathon provides standardized SEO data | LLM may generate incorrect Pandas code |
| **GA4 properties may have sparse/empty data** | Hackathon explicitly states low-traffic is acceptable | System handles gracefully with explanatory messages |
| **Spreadsheet IDs are valid** and sheets are shared with service account | Required for gspread access | SEO Agent initialization fails |

---

## Technical Design Decisions

### 1. Intent Classification via LLM

**Decision**: Use LLM-based intent detection with structured outputs (`IntentClassification` schema) instead of keyword matching.

**Rationale**:
- More robust against varied natural language phrasing
- Scales better to additional agents in the future
- Structured outputs via Pydantic ensure type-safe, predictable routing

**Trade-off**: Adds latency and LLM cost for every request, even simple ones.

---

### 2. Dynamic Code Generation for SEO Analysis

**Decision**: SEO Agent uses LLM to generate Python/Pandas code at runtime, executed via `exec()`.

**Rationale**:
- Flexible handling of any Screaming Frog schema variations
- Avoids hardcoding column names that may change
- Supports complex, arbitrary queries without pre-defined query patterns

**Trade-off**: 
- Security risk from code execution (mitigated by sandboxed `local_vars`)
- Execution failures possible if LLM generates faulty code

**Mitigations Applied**:
```python
local_vars = {"dfs": self.dfs, "pd": pd}  # Limited scope
exec(code, {}, local_vars)  # Empty globals
```

---

### 3. GA4 Metric/Dimension Allowlist Validation

**Decision**: Validate LLM-inferred metrics and dimensions against hardcoded allowlists before API calls.

**Rationale**:
- Prevents invalid GA4 API calls that would fail
- Reduces cost by avoiding retries on bad requests
- Ensures only safe, known fields are queried

**Trade-off**: New GA4 fields require code updates to allowlist.

---

### 4. Multi-Spreadsheet Support via JSON Configuration

**Decision**: Use `spreadsheets.json` to configure multiple SEO data sources instead of a single environment variable.

**Rationale**:
- Extensible to multiple data sources
- Supports both spreadsheet IDs and full URLs
- Easy for evaluators to add/modify sources

**Configuration Format**:
```json
{
  "spreadsheets": [
    {"name": "internal_audit", "source": "SPREADSHEET_ID_OR_URL", "description": "Optional"}
  ]
}
```

---

### 5. URL Normalization for Cross-Agent Matching (Tier 3)

**Decision**: Normalize URLs by extracting paths, lowercasing, and removing trailing slashes.

**Rationale**:
- GA4 returns `pagePath` (e.g., `/pricing`)
- SEO data contains full URLs (e.g., `https://example.com/pricing/`)
- Normalization enables matching between sources

**Trade-off**: May fail for complex URL structures (query params, fragments).

---

## Known Limitations

| Limitation | Description | Mitigation |
|------------|-------------|------------|
| **No persistent cache** | SEO data loaded at startup only | Call `seo_agent.refresh_data()` or restart server |
| **Rate limits** | LiteLLM/Gemini may return 429 errors | Exponential backoff retry (max 5 retries, 1s → 16s delays) |
| **No authentication on API** | `/query` endpoint is unauthenticated | Add auth middleware for production |
| **`exec()` security** | Arbitrary code execution for SEO | Sandboxed with limited vars |
| **Single-threaded data load** | SEO data loaded serially from sheets | Acceptable for hackathon scale |
| **No request timeout** | Long LLM calls may hang | Client-side timeouts recommended |

---

## Open Questions

### For Hackathon Evaluation

> [!IMPORTANT]
> These questions relate directly to hackathon evaluation criteria and may impact scoring.

1. **Property ID Replacement**
   - *Question*: Will evaluators provide a property ID with actual traffic, or should the system gracefully handle empty GA4 responses?
   - *Current Behavior*: System returns explanatory message for empty data.

2. **GA4 Quota Limits**
   - *Question*: What is the expected request volume during evaluation? Should responses be cached?
   - *Current Behavior*: No caching; each request hits the GA4 API directly.

3. **Spreadsheet Schema Variations**
   - *Question*: Will the evaluator spreadsheet use identical columns to the provided sample, or should we handle schema variations?
   - *Current Behavior*: LLM generates code based on actual column names at runtime.

4. **Response Time Expectations**
   - *Question*: Is there a maximum acceptable response time? Current p99 is ~5-10s for complex queries.
   - *Current Behavior*: No timeout; depends on LLM and API latencies.

---

### Technical Clarifications Needed

5. **Date Range Handling**
   - *Question*: How should relative dates (e.g., "last 14 days") be interpreted across timezones?
   - *Current Behavior*: LLM interprets relative dates; GA4 uses account timezone.

6. **GA4 Dimension Limits**
   - *Question*: GA4 API limits dimensions per request (typically 9). Should we handle dimension batching?
   - *Current Behavior*: Simple single-request model; may fail for many-dimension queries.

7. **Multi-Agent Fusion Confidence**
   - *Question*: When URL normalization fails to match between GA4 and SEO, should we return partial results or error?
   - *Current Behavior*: Returns partial results with explanation from LLM.

---

## Edge Cases & Error Handling

### Handled Edge Cases

| Scenario | Handling |
|----------|----------|
| Missing `propertyId` for analytics query | Falls back to SEO agent |
| Empty GA4 response | Returns explanatory message from LLM |
| Invalid spreadsheet ID | Logs error, skips that spreadsheet, continues with others |
| LLM rate limit (429) | Exponential backoff retry up to 5 times |
| Malformed LLM response | Pydantic validation fails; returns error message |
| SEO code execution error | Catches exception; returns error string |

### Unhandled / Risky Edge Cases

| Scenario | Risk | Suggested Improvement |
|----------|------|----------------------|
| LLM generates infinite loop in SEO code | Server hangs | Add execution timeout |
| Very large spreadsheets (>100k rows) | Memory exhaustion | Add row limit or pagination |
| GA4 API quota exceeded | All analytics queries fail | Add quota monitoring |
| Concurrent requests overload LLM | High latency / failures | Add request queuing |
| `credentials.json` format invalid | Startup crash | Add validation with friendly error |

---

## Summary

This implementation prioritizes:

1. **Hackathon Compliance**: Follows all specified requirements (single endpoint, port 8080, credentials at root, deploy.sh)
2. **Extensibility**: Multi-agent architecture supports adding new agents
3. **Robustness**: Structured LLM outputs, allowlist validation, graceful error handling
4. **Simplicity**: Production-ready without over-engineering

For production deployment beyond the hackathon, the [Known Limitations](#known-limitations) and [Open Questions](#open-questions) should be addressed.
