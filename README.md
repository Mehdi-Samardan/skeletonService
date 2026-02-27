# Skeleton Service

A FastAPI microservice that merges PowerPoint templates into reusable skeleton presentations, with SHA-256-based caching via MongoDB Atlas.

Built as a standalone component extracted from the [reportCreator](https://github.com/AlphaRainbow/reportCreator) system at AlphaRainbow.

---

## What It Does

Third-party applications use this service to:

1. **Discover** all available layouts and templates (`GET /saved_layouts`)
2. **Generate** a merged skeleton PPTX from a chosen combination (`POST /generate-skeleton`)
3. **Download** the resulting file (`GET /skeletons/{hash}`)

If the same combination is requested again, the service returns the cached result — no regeneration, no wasted CPU.

---

## Architecture

```
api/routes.py
    └── services/skeleton_service.py      ← orchestration
            ├── services/hash_service.py       ← SHA-256 hashing
            ├── services/ppt_service.py        ← zip-level PPTX merge
            ├── services/storage_loader.py     ← reads YAML from storage/
            └── repositories/skeleton_repository.py  ← MongoDB read/write
```

---

## Project Structure

```
skeletonService/
├── api/
│   └── routes.py                  # 3 API endpoints
├── models/
│   └── request_models.py          # Pydantic request validation
├── services/
│   ├── skeleton_service.py        # Main orchestration logic
│   ├── hash_service.py            # SHA-256 hash generation
│   ├── ppt_service.py             # PPTX merge engine (zip/XML level)
│   └── storage_loader.py          # YAML file reader
├── repositories/
│   └── skeleton_repository.py     # MongoDB CRUD
├── exceptions/
│   └── custom_exceptions.py       # Domain-specific exceptions
├── utils/
│   ├── logger.py                  # Centralized logging
│   ├── yaml_loader.py             # YAML parsing with error handling
│   ├── validators.py              # Slide name validation
│   └── mongo_serializer.py        # MongoDB → JSON serialization
├── storage/
│   ├── layouts/saved/             # Layout definitions (*.yaml)
│   └── templates/                 # Template files (*.pptx + *.yaml)
├── generated/                     # Output: merged skeleton PPTX files
├── tests/                         # 67 unit + integration tests
├── database.py                    # MongoDB connection management
├── main.py                        # FastAPI app entry point
├── run_tests.py                   # Test runner with coverage report
└── pyproject.toml                 # Project config + dependencies
```

---

## Storage Layout

```
storage/
├── layouts/
│   └── saved/
│       ├── Full report.yaml       # 41 slides
│       ├── One pager.yaml         # 2 slides
│       ├── PPG IR report.yaml     # 17 slides
│       └── PPG report.yaml        # 20 slides
└── templates/
    ├── Front slide.pptx + .yaml
    ├── Summary.pptx + .yaml
    ├── PPG/
    │   ├── Front.pptx + .yaml
    │   └── NPS.pptx + .yaml
    └── ...                        # 82 templates total
```

Each template is a **single-slide PPTX** paired with a **YAML** file describing its placeholder fields (English and Dutch).

Generated skeletons are stored in:
```
generated/{sha256_hash}.pptx
```

---

## Prerequisites

- Python 3.12+
- `uv` package manager (`pip install uv` or see [uv docs](https://docs.astral.sh/uv/))
- MongoDB Atlas account (or any MongoDB instance)

---

## Installation

```bash
git clone https://github.com/Mehdi-Samardan/skeletonService.git
cd skeletonService
uv sync
```

Create a `.env` file in the project root:

```env
MONGO_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=skeleton_db
```

---

## Running the Service

```bash
uv run uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs`

---

## API Endpoints

### `GET /saved_layouts`

Returns all available layouts and templates.

**Response:**
```json
{
  "layouts": [
    {
      "name": "Full report",
      "content": ["Front slide", "Summary", "Contents - 1", "..."]
    },
    {
      "name": "One pager",
      "content": ["One pager - front - cohort - coverage", "One pager - back - revenue"]
    }
  ],
  "templates": [
    {
      "name": "Front slide",
      "content": { "Texts": { "title": { "English": "...", "Dutch": "..." } } }
    },
    {
      "name": "PPG/Front",
      "content": { "Texts": { "..." } }
    }
  ]
}
```

---

### `POST /generate-skeleton`

Generates (or retrieves from cache) a merged skeleton PPTX.

At least one of `layout_name` or `slides` is required. When both are provided, `slides` takes priority.

**Option A — use a saved layout:**
```json
{
  "layout_name": "Full report"
}
```

**Option B — provide a custom slide list:**
```json
{
  "slides": ["Front slide", "Summary", "Final sheet"]
}
```

**Option C — saved layout name + custom override:**
```json
{
  "layout_name": "Full report",
  "slides": ["Front slide", "Summary"]
}
```

**Response:**
```json
{
  "cached": false,
  "data": {
    "_id": "507f1f77bcf86cd799439011",
    "skeleton_hash": "739af880f57e35a8d7fd76a59086e852474f245d7962d1a74aaccab6c2deed6a",
    "layout_name": "Full report",
    "slides": ["Front slide", "Summary", "..."],
    "file_path": "generated/739af880...pptx",
    "created_at": "2026-02-27T15:18:14+00:00"
  }
}
```

- `cached: true` → returned from cache, no file was generated
- `cached: false` → newly generated and stored

**Error responses:**

| Status | Reason |
|--------|--------|
| `400` | Invalid input (blank layout_name, malformed body) |
| `404` | layout_name does not exist in storage |
| `422` | A slide name references a template file that does not exist |
| `500` | Unexpected server error |

---

### `GET /skeletons/{skeleton_hash}`

Downloads the generated skeleton PPTX file.

```
GET /skeletons/739af880f57e35a8d7fd76a59086e852474f245d7962d1a74aaccab6c2deed6a
```

Returns the `.pptx` file as a binary download (`application/vnd.openxmlformats-officedocument.presentationml.presentation`).

**Error responses:**

| Status | Reason |
|--------|--------|
| `404` | No skeleton found for the given hash |

---

## Hashing

The cache key is a **SHA-256 hash** of the layout name and ordered slide list:

```python
payload = {"layout": "Full report", "slides": ["Front slide", "Summary", "..."]}
hash    = sha256(json.dumps(payload).encode()).hexdigest()
```

- Same slides in the **same order** → same hash → cache hit
- Same slides in a **different order** → different hash → new skeleton

---

## Testing

Run all 67 tests:

```bash
uv run pytest tests/ -v
```

Run with coverage report (HTML output in `coverage_html/`):

```bash
python run_tests.py
```

**Test files:**

| File | What it tests |
|------|--------------|
| `test_hash_service.py` | SHA-256 hash determinism and uniqueness |
| `test_validators.py` | Slide name validation edge cases |
| `test_request_models.py` | Pydantic model validation |
| `test_storage_loader.py` | YAML loading from storage directories |
| `test_skeleton_service.py` | Service orchestration with mocked DB |
| `test_api.py` | All API endpoints (integration tests) |

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `MONGO_URI` | Full MongoDB connection string |
| `DATABASE_NAME` | Database name (e.g. `skeleton_db`) |

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `fastapi` | Web framework |
| `uvicorn` | ASGI server |
| `pymongo` | MongoDB driver |
| `python-pptx` | PPTX inspection (slide count validation) |
| `pyyaml` | YAML parsing |
| `python-dotenv` | `.env` file loading |

Dev dependencies: `pytest`, `pytest-cov`, `httpx`

---

## Author

**Mehdi Samardan** — Internship project at AlphaRainbow, supervised by Marco Strijker (2026)
