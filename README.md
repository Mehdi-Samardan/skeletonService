# Skeleton Service

A FastAPI-based service for generating and managing document skeletons and layouts. This service allows you to define templates and layouts in YAML format and dynamically generate presentations, reports, and other documents based on user-specified combinations.

## Features

- **REST API** built with FastAPI for flexible skeleton and layout generation
- **MongoDB Integration** for persistent storage of generated skeletons
- **YAML-based Templates** for defining flexible document structures
- **Hashing System** for efficient caching and lookup of previously generated skeletons
- **Modular Architecture** with clear separation of concerns (routes, services, repositories)

## Project Structure

```
skeletonService/
├── api/
│   └── routes.py              # API endpoint definitions
├── models/
│   ├── request_models.py      # Pydantic request schemas
│   └── response_models.py     # Pydantic response schemas
├── repositories/
│   └── skeleton_repository.py # MongoDB data access layer
├── services/
│   └── skeleton_service.py    # Business logic
├── storage/
│   ├── layouts/              # Saved layout templates
│   │   ├── saved/            # Predefined layouts
│   │   └── skeletons/        # Generated skeleton outputs
│   └── templates/            # Template definitions
├── utils/
│   ├── hashing.py            # Hash generation for skeletons
│   ├── logger.py             # Logging utilities
│   ├── yaml_loader.py        # YAML file loading
│   └── validators.py         # Input validation
├── exceptions/
│   └── custom_exceptions.py  # Custom exception classes
├── database.py               # MongoDB connection management
├── main.py                   # FastAPI application entry point
└── requirements.txt          # Python dependencies
```

## Prerequisites

- Python 3.14+
- MongoDB (local or remote instance)
- pip or `uv` package manager

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Mehdi-Samardan/skeletonService.git
   cd skeletonService
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or with `uv`:
   ```bash
   uv pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the project root with the following variables:
   ```
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=skeleton_service
   DEBUG=True
   ```

4. **Ensure MongoDB is running:**
   ```bash
   # If using local MongoDB
   mongod
   ```

## Running the Service

Start the FastAPI server with hot reload:

```bash
uvicorn main:app --reload
```

Or with `uv`:
```bash
uv run uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
- **GET** `/health` - Check service status
  ```json
  {"status": "ok"}
  ```

### Root
- **GET** `/` - Welcome message
  ```json
  {"message": "Welcome to the Skeleton Service API!"}
  ```

### Skeleton Generation
- **POST** `/generate-skeleton` - Generate a new skeleton
  ```json
  {
    "layouts": ["Layout1", "Layout2"],
    "templates": ["Template1", "Template2"]
  }
  ```

### Layouts
- **GET** `/saved_layouts` - Retrieve all available layouts and templates
  ```json
  {
    "layouts": {...},
    "templates": {...}
  }
  ```

### Testing Endpoints
- **GET** `/test-yaml` - Test YAML loading
- **GET** `/test-hash` - Test hash generation
- **POST** `/test-insert` - Test MongoDB insertion

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `DATABASE_NAME` | Database name | `skeleton_service` |
| `DEBUG` | Enable debug logging | `False` |

### MongoDB Setup

The service automatically creates the necessary collections on startup. Ensure your MongoDB instance has proper permissions for read/write operations.

## Development

### Project Dependencies

- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **pymongo** - MongoDB driver
- **python-dotenv** - Environment variable management
- **pyyaml** - YAML file parsing

### Adding New Endpoints

1. Create request/response models in `models/`
2. Add business logic in `services/`
3. Add data access methods in `repositories/`
4. Define routes in `api/routes.py`

### Logging

The service uses a custom logger. Access it in any module:
```python
from utils.logger import logger
logger.info("Your message")
```

## Testing

Run the test endpoints to verify service functionality:

```bash
# Health check
curl http://localhost:8000/health

# Get available layouts
curl http://localhost:8000/saved_layouts

# Generate skeleton
curl -X POST http://localhost:8000/generate-skeleton \
  -H "Content-Type: application/json" \
  -d '{"layouts": ["Full report"], "templates": ["AlphaRainbow - tools.yaml"]}'
```

## Documentation

Once the server is running, access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## License

See [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.
