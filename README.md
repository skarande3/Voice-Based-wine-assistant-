# Voice-Based Wine Assistant

Voice-Based Wine Assistant is a single-page web app built for the Onki internship assignment. It lets a user ask questions about a wine dataset by voice or text and receive answers back as:

- on-screen text
- structured wine results
- spoken voice from the frontend

The core requirement for this project was to keep answers grounded in the provided dataset and avoid inventing facts. The app is designed around deterministic dataset retrieval, with an optional OpenAI fallback used only for query interpretation on vague prompts.

## Demo Scope

The app supports questions like:

- `Which are the best-rated wines under $50?`
- `What do you have from Burgundy?`
- `What is the most expensive bottle you have?`
- `Recommend me some red wine in United States under $50 for a gift`
- `What about white wine in United States`

It also handles:

- unsupported queries honestly
- ambiguous queries by asking for clarification
- recommendation-style prompts through transparent heuristics over dataset fields

## Tech Stack

Frontend:

- React
- TypeScript
- Vite
- Tailwind CSS
- Motion
- Web Speech API

Backend:

- Python
- FastAPI
- pandas
- httpx
- rapidfuzz
- optional OpenAI fallback for vague-query parsing

## Architecture

The system has three main stages:

1. Question capture
   - The frontend uses browser speech recognition or typed input.

2. Query interpretation
   - Clear prompts are handled with rule-based parsing.
   - Vague prompts can fall back to OpenAI for structured query extraction only.

3. Grounded retrieval and response generation
   - The backend filters the normalized wine dataset.
   - Final answers are generated only from matching rows in the dataset.

This keeps the app flexible for natural language while still grounded in the spreadsheet.

## Dataset

Primary source of truth:

- Google Sheet CSV export from the provided Onki wine dataset

The backend loads:

- `Name`
- `Producer`
- `Country`
- `Region`
- `Appellation`
- `Retail`
- `Varietal`
- `Vintage`
- `color`
- `ABV`
- `professional_ratings`
- `reference_url`
- `image_url`
- `volume_ml`

It normalizes text fields, converts numeric fields, and derives an average rating from `professional_ratings`.

## Project Structure

```text
Onki/
  backend/
    app/
      routes/
      services/
      utils/
    requirements.txt
  src/
    app/
      components/
      screens/
      utils/
    assets/
    styles/
  package.json
```

## Running the Project

### 1. Start the backend

```bash
cd /Users/shravankarande/Onki/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs on:

- `http://127.0.0.1:8000`

### 2. Start the frontend

```bash
cd /Users/shravankarande/Onki
npm install
VITE_API_BASE_URL=http://127.0.0.1:8000 npm run dev
```

Open the local Vite URL printed in the terminal.

## Optional OpenAI Hybrid Parser

The app works without OpenAI. In that mode, it uses rule-based parsing only.

To enable hybrid parsing for vague prompts, create:

- [`backend/.env`](./backend/.env)

with:

```env
OPENAI_API_KEY=your_openai_api_key_here
ONKI_OPENAI_MODEL=gpt-4.1-mini
```

Important:

- OpenAI is used only to interpret vague prompts into structured fields.
- OpenAI is not used to generate final wine facts.
- Final answers are still generated only from dataset rows.

## API Overview

Main endpoints:

- `GET /health`
- `GET /wines`
- `POST /ask`
- `POST /refresh-data`

Example request:

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"Which are the best-rated wines under $50?"}'
```

## Design Decisions

- Grounded answers first: the answer engine always uses the dataset as the source of truth.
- Deterministic parsing for clear prompts: better latency, lower cost, easier debugging.
- OpenAI only as fallback: improves vague prompt handling without turning the app into a hallucination-prone chatbot.
- Honest unsupported handling: if the dataset cannot support the question, the backend says so.
- Transparent recommendations: prompts like gift suggestions use explicit heuristics over rating and price instead of pretending the spreadsheet contains that label.

## Example Unsupported Behavior

If a user asks:

- `What wine pairs best with sushi?`

the backend will not fabricate a pairing answer, because the dataset does not include food pairing data.

## Submission Notes

This project was built to demonstrate:

- product thinking
- data grounding
- voice UX
- modular backend design
- practical AI integration without overengineering

## Additional Docs

- Backend details: [`backend/README.md`](./backend/README.md)
