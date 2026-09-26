# NexTour: Dynamic Tour Operations Platform

NexTour is an AI-powered personalized tour planning and dynamic tour operations platform. It adapts itineraries to real-world disruptions, optimizes travel experiences, and bridges the gap between travelers and tour operators with an automated cost control tower.

## Product Overview

Anyone can generate an itinerary. NexTour takes the next step: it determines whether that itinerary can actually operate within the traveler's budget and real-world constraints.

By continuously ingesting travel data, detecting changes, measuring financial impact, and finding feasible alternatives, NexTour preserves traveler preferences while protecting operator margins.

## Architecture & Tech Stack

### Frontend
* **Next.js 14** (App Router)
* **React 18**
* **Tailwind CSS** (for styling)
* **Lucide React** (Icons)
* **Radix UI** (Accessible components)

### Backend
* **FastAPI** (Python 3)
* **SQLAlchemy** (SQLite for demo/local storage)
* **Uvicorn** (Development server)
* **Pytest** (Testing framework)

## Key Features

1. **Travel DNA & Personalization**
   * Translates unstructured traveler requests into deep behavioral profiles (Travel DNA).
2. **Cost Optimization Engine**
   * Deterministically matches itinerary items against real-time data ingestion pipelines, providing max-savings or preference-balanced scenarios.
3. **Dynamic Disruption Engine**
   * Detects data staleness, price changes, weather risks, and hotel unavailability, calculating exact cost impacts.
4. **Operator Control Tower**
   * Gives operators a high-level view of "Cost At Risk," active disruptions, and data health, allowing them to instantly approve AI-recommended itinerary fixes.
5. **Real-time Data Ingestion & Health**
   * Pulls data from mock Amadeus and OpenMeteo APIs.
   * Tracks sync idempotency, data freshness, and prevents the optimizer from silently using stale data.
6. **LIVE / TEST / DEMO Modes**
   * The platform operates transparently in three modes to guarantee accurate demo presentations.

## Environment Setup

To run the platform locally, set the following environment variables. Do **not** commit actual keys.

**`.env`** (Backend)
```env
OPENAI_API_KEY=your_openai_api_key_here
```
*(If the OpenAI API key is omitted, the platform degrades gracefully and uses deterministic mock LLM responses).*

## How to Run

### Backend
1. `cd backend`
2. Set up a virtual environment: `python -m venv venv`
3. Activate the environment: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
4. Install dependencies: `pip install -r requirements.txt` (or if not present, `pip install fastapi uvicorn sqlalchemy httpx pytest`)
5. Start the server: `uvicorn app.main:app --reload --port 8000`

### Frontend
1. `cd frontend`
2. Install dependencies: `npm install`
3. Run the development server: `npm run dev`
4. Visit `http://localhost:3000`

### Running Tests
To run the automated test suite for the ingestion and disruption models:
1. `cd backend`
2. `python -m pytest tests/ -v`

## Demo Flow

The application comes with a safe, deterministic demo reset endpoint.

**To reset the demo:**
```bash
curl -X POST http://localhost:8000/api/v1/demo/reset
```

**Recommended Presentation Flow:**
1. Open the landing page (`/`).
2. Navigate to **Discover** -> **Kyoto**.
3. Set a Budget of ₹60,000, with preferences for Culture, Food, and Relaxed travel.
4. Click **Plan Trip** and view the initial itinerary.
5. Review the **"Why this trip?"** cost intelligence explanation.
6. Click **Run Cost Optimization**. Compare the original cost vs. optimized cost and notice the explicit "Data Source" and "Freshness" tags.
7. Trigger a **DEMO SIMULATION** for a disruption.
8. Analyze the disruption impact, view generated alternatives, and compare cost/preference preservation.
9. Approve an alternative to see the new itinerary version.
10. Navigate to **Operator Control Tower** (`/operator`).
11. View "Cost At Risk" and active disruptions.
12. Check **Data Health** to see the Ingestion Activity Timeline and understand the platform's reliability safeguards.

## Known Limitations
* **Currency**: The demo currently uses INR and USD natively without live FX conversions. Values are handled as configured in the fallback scenarios.
* **Database**: Uses SQLite for local hackathon demo purposes. A production deployment should migrate to PostgreSQL.
* **Mock Providers**: The current AMADEUS and OpenMeteo connectors hit public/test endpoints or return deterministic mock data depending on the selected environment (DEMO vs LIVE).
