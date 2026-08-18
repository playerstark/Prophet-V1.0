# Prophet V1.0 — Eddie Intraday (Fixed) — Setup Notes

Same ports as before: **backend on 8001, frontend dev server on 8002**
(frontend proxies `/api` → `http://localhost:8001`).

`venv/`, `frontend/node_modules/`, `.git/`, and cache/db files were stripped
out of this zip to keep it small — reinstall them locally with the steps
below.

## What changed (bug fixes only — no ports, no APIs renamed)

**Backend**
- `backend/tests/conftest.py` (new): ensures DB tables exist before tests run.
  Without it, tests that hit the `catalysts` table failed with
  "no such table: catalysts" because FastAPI's startup event (which creates
  tables) never fired under `TestClient(app)` used without a `with` block.
- `backend/requirements.txt`: added `aiohttp`, which the catalyst code
  imports but which was missing from the dependency list.
- Two test files updated for pandas 2.x compatibility (deprecated `'H'`
  frequency alias, and a chained-assignment bug that silently no-op'd).
- **Test suite: 168/180 → 180/180 passing.**

**Frontend**
- Deleted 26 stray compiled `.js` files that were sitting directly next to
  their `.tsx`/`.ts` source files in `src/` (e.g. `Home.js` next to
  `Home.tsx`). These broke Vite's production build entirely — `npm run
  build` could not have succeeded before this fix. Added a `.gitignore`
  rule to stop it recurring.
- `tsconfig.json`: was missing `"jsx": "react-jsx"` entirely and had an
  invalid `allowImportingTsExtensions` config — meaning the `tsc` type-check
  step (which runs before every `npm run build`) has likely never passed.
  Fixed.
- Fixed ~15 real TypeScript errors this surfaced, including:
  - A bug in `NewsTabsDashboard.tsx` where `setError()` was called with a
    stray second argument left over from a copy-pasted `axios.get` call.
  - A bug in `Home.tsx` where `CustomWatchlistCard` needed an `onAddTicker`
    callback that was never passed in — adding/removing a custom watchlist
    ticker would throw and show a false "failed" error even though the API
    call had actually succeeded. Now wired to refresh the dashboard.
  - **Eddie's NEW / ACTIVE / WEAKENING status tracking** (per the guide,
    section 6 & 10) was being computed on every 30-minute refresh but then
    discarded before rendering. Fixed so it flows through to the UI, and
    added the `StatusBadge` to all three market-cap card sections.
  - A UX gap where clicking a stock card showed nothing while its 6-filter
    analysis was loading — added a loading state.
- **Production build now completes cleanly** (`tsc && vite build`).

## Running it locally

### Backend (port 8001)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # fill in DEEPSEEK_API_KEY / FINNHUB_API_KEY
# For quick local testing without Postgres, you can use SQLite instead:
#   DATABASE_URL=sqlite:///./prophet.db
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```
Health check: http://localhost:8001/health
Interactive API docs: http://localhost:8001/docs

### Frontend (port 8002)
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:8002 — Eddie Intraday is under the "Eddie Intraday"
nav item, calling through to `/api/eddie/*` on the backend.

### Run the test suite
```bash
cd backend
DATABASE_URL="sqlite:///./test.db" pytest -q
```
Expect `180 passed`.

## One thing to know

`backend/.env` currently has `FINNHUB_API_KEY=` **empty**. Filter 2
(Catalysts & Industry Events) depends on Finnhub for real news — without a
key it'll run but won't have live catalyst data. Get a free key at
https://finnhub.io and drop it into `.env`.

`DEEPSEEK_API_KEY` is present in the uploaded `.env` — the AI-enhanced
catalyst analysis piece (also part of Filter 2) should work as-is.
