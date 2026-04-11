# Skeleton Service

FastAPI microservice that merges PowerPoint templates into skeleton presentations. Uses SHA-256 caching via MongoDB and GroupDocs Merger Cloud for merging.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/saved_layouts` | List all layouts and templates |
| `POST` | `/generate-skeleton` | Generate (or fetch cached) merged PPTX |
| `GET` | `/skeletons/{hash}` | Download PPTX by hash |

**POST /generate-skeleton** body:
```json
{ "slides": ["Front slide", "PPG/NPS motivation", "Summary"] }
```

Returns `{ "cached": true/false, "data": { ... } }`. If `cached: true`, no regeneration occurs.

## Setup

**Prerequisites:** Python 3.12+, [uv](https://docs.astral.sh/uv/), MongoDB Atlas account, GroupDocs Cloud account.

```bash
git clone https://github.com/your-org/skeletonService.git
cd skeletonService
uv sync
cp .env.example .env   # fill in credentials
uv run uvicorn app.main:app --app-dir src --reload
```

Visit `http://127.0.0.1:8000/docs` for Swagger UI.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `MONGO_URI` | MongoDB Atlas connection string |
| `DATABASE_NAME` | Database name (auto-created) |
| `GROUPDOCS_CLIENT_ID` | GroupDocs Cloud client ID |
| `GROUPDOCS_CLIENT_SECRET` | GroupDocs Cloud client secret |

## Storage

```
storage/
├── layouts/saved/     # Pre-defined slide collections (.yaml)
└── templates/         # Single-slide PPTX + YAML pairs
    ├── APE/ BUR/ KMDA/ NPDHV/ PPG/
    └── *.pptx / *.yaml

generated/             # Merged output (served by GET /skeletons/{hash})
```

Subdirectory templates referenced as `"PPG/Front"`.

## Tests

```bash
uv run pytest tests/ -v
# or with coverage:
python run_tests.py
```

No credentials needed — external dependencies are mocked.
