# Skeleton Service

A FastAPI microservice that merges PowerPoint templates into reusable skeleton presentations, with SHA-256 content-based caching via MongoDB Atlas and cloud-based merging via GroupDocs Merger Cloud API.

---

## What It Does

Third-party applications use this service to:

1. **Discover** all available layouts and templates (`GET /saved_layouts`)
2. **Generate** a merged skeleton PPTX from a chosen list of slides (`POST /generate-skeleton`)
3. **Download** the resulting file (`GET /skeletons/{hash}`)

If the same combination of slides is requested again, the service returns the cached result instantly — no regeneration, no unnecessary API calls.

---

## Project Structure

```
skeletonService/
├── src/
│   └── app/
│       ├── api/
│       │   └── routes.py           # FastAPI router — all HTTP endpoints
│       ├── core/
│       │   └── database.py         # MongoDB connection lifecycle
│       ├── exceptions/
│       │   └── custom_exceptions.py
│       ├── models/
│       │   └── request_models.py   # Pydantic request schemas
│       ├── repositories/
│       │   └── skeleton_repository.py  # MongoDB CRUD
│       ├── services/
│       │   ├── hash_service.py     # SHA-256 hashing helpers
│       │   ├── ppt_service.py      # GroupDocs merge + upload/download
│       │   ├── skeleton_service.py # Orchestration: cache → generate → store
│       │   └── storage_loader.py   # YAML layout/template loader
│       ├── utils/
│       │   ├── logger.py
│       │   ├── mongo_serializer.py
│       │   ├── validators.py
│       │   └── yaml_loader.py
│       └── main.py                 # FastAPI app entry point
├── tests/                          # 58 tests, all passing
├── storage/
│   ├── layouts/
│   │   ├── saved/                  # Pre-defined layout YAML files
│   │   └── skeletons/              # Cached merged PPTX files + index
│   └── templates/                  # Single-slide PPTX + YAML pairs
│       ├── APE/
│       ├── KMDA/
│       ├── NPDHV/
│       ├── PPG/
│       └── *.pptx / *.yaml
├── generated/                      # Output directory for merged PPTX files
├── .env                            # Local environment variables (never commit)
├── .env.example                    # Template for required environment variables
├── pyproject.toml
└── run_tests.py
```

---

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | Runtime |
| [uv](https://docs.astral.sh/uv/) | latest | Package & virtualenv manager |
| MongoDB Atlas | any | Cache storage (free tier works) |
| GroupDocs Cloud | any | PPTX merging API (free tier works) |

---

## Setup From Scratch

### 1. Clone the repository

```bash
git clone https://github.com/your-org/skeletonService.git
cd skeletonService
```

### 2. Install dependencies

```bash
uv sync
```

This creates a `.venv` and installs all runtime and dev dependencies from `pyproject.toml`.

### 3. Configure environment variables

Copy the example file and fill in your credentials:

```bash
cp .env.example .env
```

Open `.env` and set each value:

```env
MONGO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=skeleton_db
GROUPDOCS_CLIENT_ID=your-groupdocs-client-id
GROUPDOCS_CLIENT_SECRET=your-groupdocs-client-secret
```

#### Getting MongoDB Atlas credentials

1. Go to [https://cloud.mongodb.com](https://cloud.mongodb.com) and create a free account.
2. Create a new **Project**, then a **Cluster** (M0 free tier is sufficient).
3. Under **Database Access**, create a database user with read/write privileges. Note the username and password.
4. Under **Network Access**, add your IP address (or `0.0.0.0/0` for development).
5. On the cluster overview page, click **Connect → Drivers**, choose Python, and copy the connection string.
6. Replace `<username>` and `<password>` in the string with your database user credentials.
7. Set `DATABASE_NAME` to any name you like (e.g. `skeleton_db`). The database is created automatically on first write.

#### Getting GroupDocs Cloud credentials

1. Go to [https://dashboard.groupdocs.cloud](https://dashboard.groupdocs.cloud) and create a free account.
2. After logging in, navigate to **Applications**.
3. Your `Client ID` and `Client Secret` are shown on the dashboard. Copy both.

### 4. Verify the setup

```bash
uv run uvicorn app.main:app --app-dir src --reload
```

You should see:

```
INFO | skeleton_service | Connected to MongoDB: skeleton_db
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the interactive Swagger UI.

---

## API Endpoints

### `GET /saved_layouts`

Returns all available pre-defined layouts and individual templates.

**Response:**
```json
{
  "layouts": [
    { "name": "Full report", "content": ["Front slide", "Summary", "..."] }
  ],
  "templates": [
    { "name": "PPG/Front", "content": { "Texts": { ... } } }
  ]
}
```

---

### `POST /generate-skeleton`

Generates (or retrieves from cache) a merged skeleton PPTX.

**Request body:**
```json
{
  "slides": ["Front slide", "PPG/NPS motivation", "Summary"]
}
```

**Response:**
```json
{
  "cached": false,
  "data": {
    "_id": "...",
    "skeleton_hash": "abc123...",
    "slides": ["Front slide", "PPG/NPS motivation", "Summary"],
    "slide_hashes": { "Front slide": "sha256...", ... },
    "file_path": "generated/abc123....pptx",
    "created_at": "2026-01-01T12:00:00+00:00"
  }
}
```

- `cached: true` means the result was retrieved from MongoDB — no PPTX generation occurred.
- `cached: false` means a new PPTX was generated, merged via GroupDocs, and stored.

**Error codes:**
| Code | Reason |
|------|--------|
| 400 | Slide list is empty or malformed |
| 422 | One or more slide template files not found |
| 500 | Unexpected server error |

---

### `GET /skeletons/{skeleton_hash}`

Downloads the generated `.pptx` file by its SHA-256 hash.

**Response:** Binary PPTX file (`application/vnd.openxmlformats-officedocument.presentationml.presentation`)

**Error codes:**
| Code | Reason |
|------|--------|
| 404 | No file found for the given hash |

---

## How Caching Works

```
POST /generate-skeleton
        │
        ▼
  hash each slide's PPTX binary (SHA-256)
        │
        ▼
  query MongoDB: slides list + per-slide hashes match?
        │
   ┌────┴─────┐
  YES        NO
   │          │
   │     merge via GroupDocs
   │          │
   │     hash merged PPTX binary
   │          │
   │     save to generated/{hash}.pptx
   │          │
   │     insert metadata into MongoDB
   │          │
   └────┬─────┘
        │
   return { cached, data }
```

Per-slide hashing means that if any individual template file changes on disk, the cache is automatically invalidated for any skeleton that includes that slide.

---

## Storage Layout

```
storage/
├── layouts/saved/          # Pre-defined slide collections
│   ├── Full report.yaml    # List of ~41 slide names
│   ├── One pager.yaml
│   ├── PPG IR report.yaml
│   └── PPG report.yaml
├── layouts/skeletons/      # Cached merged PPTX files + index YAML
└── templates/              # Single-slide PPTX + YAML metadata pairs
    ├── APE/
    ├── KMDA/
    ├── NPDHV/
    ├── PPG/
    └── *.pptx / *.yaml     # Root-level templates
```

Each template consists of two files with the same stem:
- `<name>.pptx` — the single-slide PowerPoint file
- `<name>.yaml` — metadata (text fields, placeholders, etc.)

Subdirectory templates are referenced using forward-slash notation: `"PPG/Front"`.

---

## Running Tests

```bash
uv run pytest tests/ -v
```

Or with coverage:

```bash
python run_tests.py
```

Tests use mocked external dependencies (MongoDB, GroupDocs) so no credentials are needed to run the test suite.

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `MONGO_URI` | Yes | MongoDB Atlas connection string |
| `DATABASE_NAME` | Yes | MongoDB database name (created automatically) |
| `GROUPDOCS_CLIENT_ID` | Yes | GroupDocs Cloud API client ID |
| `GROUPDOCS_CLIENT_SECRET` | Yes | GroupDocs Cloud API client secret |

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `fastapi` | Web framework |
| `uvicorn` | ASGI server |
| `pymongo` | MongoDB driver |
| `python-dotenv` | Load `.env` file |
| `python-pptx` | PPTX file inspection |
| `pyyaml` | YAML layout/template loading |
| `groupdocs-merger-cloud` | Server-side PPTX merging |
| `groupdocs-conversion-cloud` | GroupDocs file upload/download |
| `httpx` *(dev)* | HTTP client for tests |
| `pytest` *(dev)* | Test runner |
| `pytest-cov` *(dev)* | Coverage reporting |
