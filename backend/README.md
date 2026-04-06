# Onki Voice Wine Explorer Backend

Production-style FastAPI backend for the Onki internship assignment.

## What It Does

- Loads the wine dataset from the Google Sheet CSV export URL.
- Falls back to the local Excel copy if the remote fetch is unavailable.
- Cleans and normalizes the wine data into a consistent in-memory cache.
- Parses user questions with deterministic, explainable logic.
- Returns grounded JSON responses for the frontend.
- Handles ambiguity and unsupported questions without inventing facts.

## Tech Stack

- Python
- FastAPI
- pandas
- uvicorn
- httpx
- rapidfuzz

## Folder Structure

```text
backend/
  app/
    main.py
    config.py
    models.py
    schemas.py
    routes/
      ask.py
      health.py
      wines.py
    services/
      answer_engine.py
      data_cleaner.py
      dataset_loader.py
      query_parser.py
      recommendation_engine.py
    utils/
      match_utils.py
      text_utils.py
  requirements.txt
  README.md
```

## Run Locally

```bash
cd /Users/shravankarande/Onki/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API will run on `http://127.0.0.1:8000`.

## OpenAI Hybrid Parser

The backend supports a hybrid query parser:

- deterministic rules for common wine questions
- OpenAI fallback for vague or underspecified prompts
- dataset-grounded answer generation remains unchanged

Add your API key in one of these ways:

```bash
export OPENAI_API_KEY="your_api_key_here"
```

or create `backend/.env` with:

```bash
OPENAI_API_KEY=your_api_key_here
ONKI_OPENAI_MODEL=gpt-4.1-mini
```

If no API key is present, the backend falls back to rule-based parsing only.

## Endpoints

### `GET /health`

Returns health and dataset load metadata.

### `GET /wines`

Optional inspection endpoint. Query params:

- `price_min`
- `price_max`
- `region`
- `country`
- `min_rating`
- `limit`

Example:

```bash
curl "http://127.0.0.1:8000/wines?price_max=50&region=Champagne&limit=3"
```

### `POST /ask`

Primary frontend endpoint.

Example:

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"Which are the best-rated wines under $50?"}'
```

### `POST /refresh-data`

Reloads the dataset into memory.

## Design Notes

- Grounding: Every answer comes from filtered rows in the dataset cache.
- Ratings: The backend derives `rating` from the average of `professional_ratings` scores normalized to a 100-point scale.
- Gift recommendations: These are transparent heuristics over rating, price band, and recognizable styles. The response text explicitly says the dataset does not label wines as gifts.
- Unsupported questions: The backend returns an honest explanation instead of trying to infer unsupported facts such as food pairings.

## Frontend Compatibility

The `/ask` response shape is designed for the existing voice frontend:

- `answer_text` for on-screen and spoken response
- `results` for cards or structured rendering
- `meta` for graceful handling of ambiguity and unsupported requests

## Optional Environment Variables

- `ONKI_LOCAL_DATASET_PATH`
- `ONKI_CSV_EXPORT_URL`
- `ONKI_CORS_ORIGINS`
- `OPENAI_API_KEY`
- `ONKI_OPENAI_MODEL`
