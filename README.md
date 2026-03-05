# Skeleton Service

A FastAPI microservice that merges PowerPoint templates into reusable skeleton presentations, with SHA-256 content-based caching via MongoDB Atlas and cloud-based merging via GroupDocs Merger Cloud API.

Built as a standalone component extracted from the [reportCreator](https://github.com/AlphaRainbow/reportCreator) system at AlphaRainbow.

---

## What It Does

Third-party applications use this service to:

1. **Discover** all available layouts and templates (`GET /saved_layouts`)
2. **Generate** a merged skeleton PPTX from a chosen list of slides (`POST /generate-skeleton`)
3. **Download** the resulting file (`GET /skeletons/{hash}`)

If the same combination of slides (producing identical file content) is requested again, the service returns the cached result — no regeneration, no unnecessary API calls.

### Typical Usage Scenario

1. Call `GET /saved_layouts` to browse all available slide templates and pre-defined layouts.
2. Pick the slides you want (from a saved layout or your own selection).
3. Call `POST /generate-skeleton` with your slide list.
4. Receive a `skeleton_hash` in the response.
5. Call `GET /skeletons/{skeleton_hash}` to download the merged `.pptx` file.
6. Repeat step 3 with the same slides → get an instant cache hit, no waiting.

---

## Architecture

```
api/routes.py
    └── services/skeleton_service.py      ← orchestration
            ├── services/hash_service.py       ← SHA-256 content hashing
            ├── services/ppt_service.py        ← GroupDocs Merger Cloud integration
            ├── services/storage_loader.py     ← reads YAML from storage/
            └── repositories/skeleton_repository.py  ← MongoDB read/write
```

### How Caching Works

1. Request arrives with a list of slide names.
2. Templates are merged into a single PPTX via GroupDocs Merger Cloud API.
3. The **binary content** of the merged file is hashed with SHA-256.
4. MongoDB is checked for this hash.
   - **Cache hit** → temp file is deleted, existing record returned immediately.
   - **Cache miss** → file is saved as `generated/{hash}.pptx`, metadata stored in MongoDB.

This content-based approach means that two different slide lists that happen to produce identical output will correctly share a single cached file.

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
│   ├── hash_service.py            # SHA-256 content hash
│   ├── ppt_service.py             # GroupDocs Merger Cloud integration
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
├── tests/                         # Unit + integration tests
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
- GroupDocs account with Merger Cloud and Conversion Cloud API access

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
GROUPDOCS_CLIENT_ID=your-groupdocs-client-id
GROUPDOCS_CLIENT_SECRET=your-groupdocs-client-secret
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

Returns all available layouts and templates. Use this to discover which slides exist before building your slide list.

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

**Error responses:**

| Status | Reason |
|--------|--------|
| `500`  | Storage directory is missing or unreadable |

---

### `POST /generate-skeleton`

Generates (or retrieves from cache) a merged skeleton PPTX from an ordered list of slide names.

**Request body:**
```json
{
  "slides": ["Front slide", "Summary", "Final sheet"]
}
```

- `slides` — required, non-empty list of template names. Sub-folder names are supported (e.g. `"PPG/Front"`).

**Example — use slides from a saved layout:**
```bash
# 1. Get the layout's slide list
GET /saved_layouts  →  layouts[0].content = ["Front slide", "Summary", "..."]

# 2. Pass it to generate-skeleton
POST /generate-skeleton
{
  "slides": ["Front slide", "Summary", "..."]
}
```

**Example — use a custom selection:**
```json
{
  "slides": ["PPG/Front", "Summary", "Final sheet"]
}
```

**Response:**
```json
{
  "cached": false,
  "data": {
    "_id": "507f1f77bcf86cd799439011",
    "skeleton_hash": "739af880f57e35a8d7fd76a59086e852474f245d7962d1a74aaccab6c2deed6a",
    "slides": ["Front slide", "Summary", "Final sheet"],
    "file_path": "generated/739af880...pptx",
    "created_at": "2026-02-27T15:18:14+00:00"
  }
}
```

- `cached: true` → returned from cache, no file was regenerated
- `cached: false` → newly merged and stored

**Error responses:**

| Status | Reason |
|--------|--------|
| `400`  | Invalid input (blank slide name, malformed body) |
| `422`  | A slide name references a template file that does not exist |
| `500`  | Unexpected server error (e.g. GroupDocs API failure, missing credentials) |

---

### `GET /skeletons/{skeleton_hash}`

Downloads the generated skeleton PPTX file by its content hash.

```
GET /skeletons/739af880f57e35a8d7fd76a59086e852474f245d7962d1a74aaccab6c2deed6a
```

Returns the `.pptx` file as a binary download (`application/vnd.openxmlformats-officedocument.presentationml.presentation`).

**Error responses:**

| Status | Reason |
|--------|--------|
| `404`  | No skeleton found for the given hash |

---

## Hashing

The cache key is a **SHA-256 hash of the binary content** of the merged PPTX file:

```python
with open(merged_file_path, "rb") as f:
    hash = sha256(f.read()).hexdigest()
```

This means:
- Same slides in the **same order** producing the **same output** → cache hit
- Different slides **or** same slides in a **different order** → different file → different hash → new skeleton
- Two different slide lists that happen to merge into identical binary content → same hash → shared cache entry

---

## PPTX Merging

Templates are merged using the **GroupDocs Merger Cloud API**:

1. All template PPTX files are uploaded to GroupDocs cloud storage in parallel (up to 20 concurrent uploads).
2. A server-side merge request is submitted with the slides in order.
3. The merged file is downloaded and saved to a temporary location.
4. The file is content-hashed, cache-checked, then either discarded (cache hit) or moved to `generated/{hash}.pptx`.

If only a single slide is requested, the merge step is skipped and the template is copied directly.

---

## Testing

Run all tests:

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
| `test_hash_service.py` | SHA-256 content hash determinism and uniqueness |
| `test_validators.py` | Slide name validation edge cases |
| `test_request_models.py` | Pydantic model validation |
| `test_storage_loader.py` | YAML loading from storage directories |
| `test_skeleton_service.py` | Service orchestration with mocked DB and file system |
| `test_api.py` | All API endpoints (integration tests with mocked dependencies) |

**All external dependencies (MongoDB, GroupDocs API) are fully mocked in tests**, so the test suite runs without any network access or credentials.

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `MONGO_URI` | Full MongoDB connection string |
| `DATABASE_NAME` | Database name (e.g. `skeleton_db`) |
| `GROUPDOCS_CLIENT_ID` | GroupDocs Cloud application client ID |
| `GROUPDOCS_CLIENT_SECRET` | GroupDocs Cloud application client secret |

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `fastapi` | Web framework |
| `uvicorn` | ASGI server |
| `pymongo` | MongoDB driver |
| `groupdocs-merger-cloud` | Server-side PPTX merging via GroupDocs |
| `groupdocs-conversion-cloud` | File upload/download for GroupDocs |
| `python-pptx` | PPTX inspection (slide count validation) |
| `pyyaml` | YAML parsing |
| `python-dotenv` | `.env` file loading |

Dev dependencies: `pytest`, `pytest-cov`, `httpx`

---

## Author

**Mehdi Samardan** — Internship project at AlphaRainbow, supervised by Marco Strijker (2026)
