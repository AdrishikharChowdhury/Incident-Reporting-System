# Incident Reporting API

A small FastAPI service for reporting, retrieving, updating, and deleting civic
incidents (power outages, water leaks, theft, etc.). Data is stored in a local
SQLite database through SQLModel; on first startup the tables are created and
seeded from the mock data in `data.py`. Reported locations are geocoded with
Nominatim.

> **Status:** SQLite-backed. All read and write handlers (list, get-one, create,
> update) now query and mutate the database through SQLModel. The `DELETE`
> handler still operates on the module-level mock stores in `data.py`; migrating
> it is pending.

## Tech stack

- **Python 3.13**
- **FastAPI** (`fastapi[standard]`)
- **Uvicorn** (ASGI server)
- **SQLModel / SQLAlchemy** with **SQLite**
- **geopy / Nominatim** for geocoding
- **uv** for dependency management and packaging

## Project structure

```
incident-api/
├── pyproject.toml            # project metadata + dependencies
├── uv.lock                   # locked dependency versions
├── README.md
└── src/
    └── incident_api/
        ├── __init__.py       # engine, session dependency, table creation, `main()` entrypoint
        ├── main.py           # FastAPI app + routes + lifespan (startup seeding)
        ├── models.py         # SQLModel tables + Category/Tag models + request models + JSON TypeDecorators
        ├── enums.py          # `Status` and `GeocodeStatus` enums
        ├── response_model.py # generic `Response` / `IncidentResponse` response models
        ├── data.py           # in-memory mock stores (seed source) + get/set helpers
        ├── seed.py           # writes the mock data into the database on startup
        └── utils.py          # geocoding + category/tag builders
```

## Getting started

Prerequisites: [uv](https://docs.astral.sh/uv/) installed.

Install dependencies:

```bash
uv sync
```

Run the development server (with auto-reload):

```bash
uv run incident-api
```

Or via FastAPI's dev runner:

```bash
uv run fastapi dev src/incident_api/main.py
```

The app serves at `http://127.0.0.1:8000` with interactive docs at
`http://127.0.0.1:8000/docs`.

On startup the app creates the SQLite tables (`incident_report.db`) and, if the
`incident` table is empty, seeds it from the mock data in `data.py`.

## Data models

Defined in `models.py` as SQLModel `table=True` classes. Primary keys are UUIDs,
and every related row carries an `incident_id` foreign key back to
`incident.id`.

| Table | Key fields |
| --- | --- |
| `incident` | `id` (UUID), `title`, `sanitized_text`, `categories_id` (FK), `location_id` (FK), `occurred_at`, `created_at`, `status`, `duplicate_of_id` (self-FK, nullable) |
| `location` | `id` (UUID), `incident_id` (FK), `display_name`, `normalized_name`, `latitude`, `longitude`, `geocode_status` |
| `categories` | `id` (UUID), `incident_id` (FK), `categories` — JSON list of `{name, slug}` |
| `tags` | `id` (UUID), `incident_id` (FK), `tags` — JSON list of `{name, tag}` |
| `metadata` | `id` (UUID), `incident_id` (FK), `source`, `received_at`, `request_id` |

The `Category` and `Tag` value models are stored in JSON columns through the
`CategoryList` / `TagList` `TypeDecorator`s.

Request models (Pydantic, not tables):

- `IncidentCreate` — `title`, `text`, `location` (required); `categories`,
  `tags`, `occurred_at` (optional).
- `IncidentUpdate` — `title`, `text` (both required).

Enums (`enums.py`):

- `Status`: `pending`, `in progress`, `resolved`, `duplicate`, `closed`, `rejected`
- `GeocodeStatus`: `success`, `failed`

## API endpoints

Routes are served at the application root (no path prefix is currently applied —
see the note below).

| Method | Path | Description |
| --- | --- | --- |
| GET | `/` | Health/welcome message |
| GET | `/incidents` | List all incidents |
| GET | `/incidents/{incident_id}` | Get one incident with its related records (returns `404` if not found) |
| GET | `/categories` | List categories |
| GET | `/locations` | List locations |
| GET | `/incident-tags` | List incident tags |
| GET | `/submission-data` | List submission metadata |
| POST | `/incidents/create` | Create an incident (plus its location, categories, tags, and submission metadata) |
| PUT | `/incidents/update/{incident_id}` | Update an incident's `title` and `text` |
| DELETE | `/incidents/{incident_id}` | Delete an incident and its related records (still in-memory) |

The collection endpoints (`/incidents`, `/categories`, `/locations`,
`/incident-tags`, `/submission-data`) wrap their results in a `data` key:

```json
{ "data": [ { "...": "..." } ] }
```

### `GET /incidents/{incident_id}`

Returns the incident together with the related records joined on `incident_id`:

```json
{
  "incident": { "id": "362983e5-36c4-5e04-a543-9620d490b651", "title": "Power Outage in Sector V", "...": "..." },
  "category": { "id": "77e216c2-...", "incident_id": "362983e5-...", "categories": [{ "name": "Utility / Infrastructure", "slug": "utility-infrastructure" }] },
  "location": { "id": "c2ff83c9-...", "incident_id": "362983e5-...", "display_name": "Sector V, Salt Lake, Kolkata", "...": "..." },
  "tags": { "id": "33e36f89-...", "incident_id": "362983e5-...", "tags": [{ "name": "Power Outage", "tag": "power-outage" }] },
  "metadata": { "id": "314f5370-...", "incident_id": "362983e5-...", "source": "mobile_app", "...": "..." }
}
```

Returns `404 Not Found` if no incident matches `incident_id`.

### `POST /incidents/create`

Request body (`IncidentCreate`). `title`, `text`, and `location` are required;
`tags` and `categories` are comma-separated strings; `occurred_at` is an
ISO&nbsp;8601 datetime.

```json
{
  "title": "Theft in Broad Daylight",
  "text": "A bold daytime robbery occurred near the market.",
  "location": "Park Street, Kolkata",
  "categories": "Crime, Robbery",
  "tags": "Theft, Fraud, Assault",
  "occurred_at": "2026-10-11T14:30:00Z"
}
```

Behavior:

- A UUID (`uuid4`) is generated for the incident and each related record.
- `location` is geocoded via Nominatim; `latitude`/`longitude` are set from the
  result and `geocode_status` is `"success"` or `"failed"` (a failed or empty
  lookup leaves the coordinates `null`).
- `categories` and `tags` are split on `,`, trimmed, and expanded into
  `{name, slug}` / `{name, tag}` rows.
- `status` defaults to `"pending"` and `duplicate_of_id` to `null`.
- `metadata.source` is taken from the request `User-Agent` header and
  `metadata.request_id` is a fresh UUID.
- The record is committed to the database before the response is returned.

Response:

```json
{
  "incident": { "...": "..." },
  "category": { "...": "..." },
  "location": { "...": "..." },
  "tags": { "...": "..." },
  "metadata": { "...": "..." }
}
```

### `PUT /incidents/update/{incident_id}`

Updates an incident's `title` and `sanitized_text`, keyed by `incident_id`.
Both fields are required (`IncidentUpdate`).

Status codes:

| Code | When |
| --- | --- |
| `200 OK` | The incident was updated |
| `404 Not Found` | No incident with that `incident_id` |

Request body:

```json
{
  "title": "Theft in Broad Daylight (updated)",
  "text": "Updated description of the incident."
}
```

Response:

```json
{
  "incident": { "...": "..." },
  "category": { "...": "..." },
  "location": { "...": "..." },
  "tags": { "...": "..." },
  "metadata": { "...": "..." }
}
```

### `DELETE /incidents/{incident_id}`

Removes the incident together with its related location, categories, tags, and
submission metadata.

- `204 No Content` — the incident was deleted.
- `404 Not Found` — no incident with that `incident_id`.

> Not yet migrated: this handler still reads/writes the in-memory mock stores in
> `data.py`.

## Notes & limitations

- **Database-backed handlers.** The list, get-one, create, and update handlers
  all use the SQLite database through the `SessionDep` dependency; data persists
  across restarts.
- **Seeding.** `seed.py` runs on startup and inserts the mock data from `data.py`
  only when the `incident` table is empty.
- **`DELETE` still in-memory.** The delete handler operates on the module-level
  lists in `data.py`, so it does not affect the persisted rows — migration is
  pending.
- **No path prefix.** `main.py` constructs `FastAPI(root="/api/v1")`, but FastAPI
  has no `root` parameter (`root_path` exists but does not prefix routes), so it
  is ignored and routes are served from `/`. A versioned prefix (e.g. `/api/v1`,
  `/api/v2`) is not yet wired up.
- `created_at` / `received_at` use UTC-aware `datetime.now(timezone.utc)`.
- Geocoding makes a live network call to Nominatim per create request; failures
  are swallowed and recorded as `geocode_status: "failed"`.
