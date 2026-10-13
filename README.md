# Incident Reporting API

A small FastAPI service for reporting, retrieving, updating, and deleting civic
incidents (power outages, water leaks, theft, etc.). Data is served from
in-memory mock stores, while the same mock data is persisted to a local SQLite
database through SQLModel. Reported locations are geocoded with Nominatim.

> **Status:** in-memory serving with a SQLModel/SQLite layer. The schema lives in
> `models.py` and the mock data is written to `incident_report.db` on startup via
> `seed.py`; request handling still reads and writes the module-level stores in
> `data.py`.

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
        ├── models.py         # SQLModel tables + Category/Tag models + JSON TypeDecorators
        ├── enums.py          # `Status` and `GeocodeStatus` enums
        ├── data.py           # in-memory mock stores + get/set helpers
        ├── seed.py           # writes the mock data into the database on startup
        └── utils.py          # geocoding + category/tag helpers
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

The app serves under the root path **`/api/v1`** at `http://127.0.0.1:8000`.
Interactive docs: `http://127.0.0.1:8000/api/v1/docs`.

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

Enums (`enums.py`):

- `Status`: `pending`, `in progress`, `resolved`, `duplicate`, `closed`, `rejected`
- `GeocodeStatus`: `success`, `failed`

## API endpoints

Base path: `/api/v1`

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
| PUT | `/incidents/update/{incident_id}` | Partially update an incident's mutable fields |
| DELETE | `/incidents/{incident_id}` | Delete an incident and its related records |

### `GET /incidents/{incident_id}`

Returns the incident together with the related records joined on `incident_id`:

```json
{
  "incident": { "id": 1, "title": "Power Outage in Sector V", "...": "..." },
  "location": { "id": 12, "incident_id": 1, "display_name": "Sector V, Salt Lake, Kolkata", "...": "..." },
  "categories": { "id": 3, "incident_id": 1, "categories": [{ "name": "Utility / Infrastructure", "slug": "utility-infrastructure" }] },
  "incident_tags": { "id": 34, "incident_id": 1, "tags": [{ "name": "Power Outage", "tag": "power-outage" }] },
  "metadata": { "id": 101, "incident_id": 1, "source": "mobile_app", "...": "..." }
}
```

### `POST /incidents/create`

Request body (JSON object). `tags` and `categories` are comma-separated strings.

```json
{
  "location": "Behala, Kolkata",
  "tags": "Theft,Fraud,Assault",
  "categories": "Crime,Robbery",
  "title": "Theft in Broad Daylight",
  "text": "On October 11, 2026, a bold daytime robbery occurred ...",
  "occurred_at": "October 11, 2026"
}
```

Behavior:

- A random id (`100`–`1000`) is generated for the incident and each related record.
- `location` is geocoded via Nominatim; `latitude`/`longitude` are set from the
  result and `geocode_status` is `"success"` or `"failed"` (on a failed or empty
  lookup the coordinates are `null`).
- `categories` and `tags` are split on `,` and expanded into `{name, slug}` /
  `{name, tag}` rows.
- `status` defaults to `"pending"` and `duplicate_of_id` to `null`.

Response:

```json
{
  "incident": { "...": "..." },
  "location": { "...": "..." },
  "categories": { "...": "..." },
  "incident_tags": { "...": "..." },
  "metadata": { "...": "..." }
}
```

### `PUT /incidents/update/{incident_id}`

Partially updates an incident. Only the keys present in the body are applied, so
it behaves like a partial update.

The following fields are **immutable** and cannot be changed after creation:
`category`, `categories`, `tags`, `location`.

Status codes:

| Code | When |
| --- | --- |
| `200 OK` | Only mutable fields were sent; all applied |
| `207 Multi-Status` | Mutable **and** immutable fields were sent; mutable fields applied, immutable ones discarded (listed in `ignored_fields`) |
| `400 Bad Request` | Empty body, or body contained only immutable fields (nothing to update) |
| `404 Not Found` | No incident with that `incident_id` |

Request body — only include what you want to change:

```json
{
  "title": "Theft in Broad Daylight (updated)",
  "status": "needs review"
}
```

Response:

```json
{
  "new_incident": { "id": 2, "title": "Theft in Broad Daylight (updated)", "status": "needs review", "...": "..." },
  "ignored_fields": []
}
```

When immutable fields are discarded, `ignored_fields` lists them:

```json
{
  "new_incident": { "...": "..." },
  "ignored_fields": ["category", "location"]
}
```

### `DELETE /incidents/{incident_id}`

Removes the incident together with its related location, categories, tags, and
submission metadata.

- `204 No Content` — the incident was deleted.
- `404 Not Found` — no incident with that `incident_id`.

## Notes & limitations

- **In-memory serving.** Request handlers still operate on the module-level lists
  in `data.py`; created records are appended and updates mutate in place,
  persisting only for the lifetime of the process. Restarting the server (or
  `--reload`) resets the in-memory data.
- **SQLite layer.** `models.py` defines the SQLModel schema and `seed.py` writes
  the mock data into `incident_report.db` on startup. The handlers are not yet
  reading from this database — migrating them is pending.
- `created_at` / `received_at` use `datetime.now(...)` timestamps.
- Geocoding makes a live network call to Nominatim per create request; failures
  are swallowed and recorded as `geocode_status: "failed"`.
