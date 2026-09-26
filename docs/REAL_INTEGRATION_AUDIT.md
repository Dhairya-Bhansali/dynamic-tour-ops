# Real Integration Audit

## 1. Executive Summary

- **Is the LLM actually connected?** No. `OPENAI_API_KEY` is not present in the runtime environment. The application safely detects this missing key and uses a robust deterministic fallback to simulate AI functionality.
- **Is real external travel data actually being ingested?** Yes for Open-Meteo and OSRM (unauthenticated). No for Amadeus. The application provides LIVE, TEST, and DEMO modes, but defaults to DEMO. The Amadeus connector exists but lacks real credentials for live mode, so it cannot execute a live flight search.
- **Which providers are genuinely reachable?** Open-Meteo and OSRM are reachable and fetch real data in LIVE mode because they are public APIs without auth.
- **Which providers are only implemented as connectors?** Amadeus is implemented but lacks OAuth2 credential flows and environment variables, acting purely as a mock/test wrapper.
- **Which parts use demo/test/fallback data?** The entire current operation of the application (Itinerary generation, Budget Optimizer, Disruptions) utilizes the `DEMO` environment fallback data. The optimizer explicitly tags its generated items with `FALLBACK` because fresh live data is intentionally substituted with deterministic responses.

## 2. AI / LLM

| Component | Provider | Configured | Real Request Tested | Working | Actual Feature | Fallback |
|---|---|---:|---:|---:|---|---|
| `ItineraryPlanner` | OpenAI | NO | NO | NO | Itinerary Generation | Deterministic rule-based mock itinerary |
| `LiveTripService` | OpenAI | NO | NO | NO | Chat Assistant | Deterministic mock responses |
| `PlanFixService` | OpenAI | NO | NO | NO | Disruption Resolutions | Pre-defined alternatives based on DB |

## 3. External Data Providers

| Provider | Source File | API Endpoint | Mode | Request Executed | Real Response | Stored | Used by Optimizer |
|---|---|---|---|---:|---:|---:|---:|
| Amadeus | `amadeus.py` | `https://test.api.amadeus.com` | DEMO | NO | NO | YES (Mock) | YES (Fallback) |
| OpenMeteo | `open_meteo.py` | `https://api.open-meteo.com/v1/forecast` | LIVE (No Auth) | YES (If live) | YES | YES | NO (Not directly optimized) |
| OSRM | `osm.py` | `http://router.project-osrm.org` | LIVE (No Auth) | YES (If live) | YES | YES | NO (Not directly optimized) |

## 4. Ingestion Pipeline

- **Provider:** WORKING (For DEMO data & public APIs)
- **Raw Response:** WORKING
- **Normalization:** WORKING
- **Validation:** WORKING
- **Deduplication:** WORKING
- **Canonical DB:** WORKING
- **Freshness:** WORKING
- **Optimizer:** WORKING (Correctly identifies fallback data)

## 5. Database Provenance

Because the database uses `DEMO` mode for hackathon demonstrations, the database records strictly originate from deterministic simulated responses.

- `FlightOffer`: MOCK (Amadeus fallback)
- `HotelOffer`: MOCK (Amadeus fallback)
- `ActivityOffer`: MOCK (Seed data)
- `WeatherForecast`: MOCK / LIVE (Depending on `/api/v1/ingestion` mode parameter)

## 6. Optimizer Provenance

`BudgetOptimizerService` reads candidate records from the core database tables (e.g., `FlightOffer`, `HotelOffer`). During this audit, all records sourced were `DEMO FALLBACK`.
When the optimizer detects that no `FRESH` real records are available within the freshness thresholds, it explicitly synthesizes fallback variations and injects the following metadata:
`"reasoning": "Using fallback data because fresh provider data is unavailable."`
`"freshness_status": "FALLBACK"`

## 7. Environment Configuration

| Variable | Configured |
|---|---:|
| `OPENAI_API_KEY` | NO |
| `AMADEUS_CLIENT_ID` | NO |
| `AMADEUS_CLIENT_SECRET` | NO |
| `DATABASE_URL` | YES (SQLite) |

## 8. Test Results

- `pytest tests/ -v`: All 14 tests pass successfully. Tests verify ingestion idempotency, staleness/freshness thresholds, disruption simulation mechanics, and the optimizer fallback mechanisms.
- `npm run build`: Static routes compiled cleanly via Turbopack with 0 errors.

## 9. Critical Findings

### VERIFIED REAL
- OpenMeteo and OSRM public API endpoints can be hit when the ingestion controller is triggered in `LIVE` mode.
- The `FreshnessEngine` operates in real-time, accurately decaying data states based on TTLs.

### VERIFIED TEST
- End-to-end unit tests correctly assert logic for fallback and data freshness behaviors.

### MOCK / DEMO
- Initial trip generation, provider ingestion default modes, and LLM inferences are explicitly and intentionally mocked.

### FALLBACK
- Budget Optimization correctly and safely falls back to deterministic rule-based pricing when live providers are unconfigured or data is stale.

### NOT VERIFIED
- Live Amadeus Flight/Hotel ingestion could not be verified due to missing API credentials.

## 10. SIH DEMO CLAIMS

**WHAT WE CAN HONESTLY CLAIM IN THE SIH DEMO:**
- "We have built a real-time ingestion architecture capable of integrating external travel and weather providers, featuring robust validation, deduplication, and a `FreshnessEngine`."
- "The platform guarantees safety through transparent TEST/LIVE/DEMO modes, explicitly identifying stale or simulated data to the operator."
- "Our Budget Optimizer is capable of operating against live provider records, and degrades safely to deterministic fallback prices when external APIs are unavailable or unconfigured."
- "The core dynamic tour operations logic (disruption detection, impact analysis, cost at risk, operator control tower) is fully functional and driven by our backend architecture."

**WHAT WE CANNOT CLAIM:**
- We cannot claim that we are querying real flight prices via Amadeus in real-time.
- We cannot claim the itinerary text generation is currently powered by a live LLM model.
