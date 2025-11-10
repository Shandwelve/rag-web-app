# API Documentation

FastAPI backend for the RAG Web Application.

## Setup

### 1. Install Dependencies

This project uses [UV](https://github.com/astral-sh/uv) for Python package management.

```bash
# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync
```

### 2. Environment Configuration

**Important**: Create a `.env` file in the `api` directory using `.env.example` as a template:

```bash
cp .env.example .env
```

Edit the `.env` file and complete it with your actual values:

```env
# Frontend Configuration
FRONTEND_URL=http://localhost:5173

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rag_web_app
DB_USER=postgres
DB_PASS=your_password_here

# Storage Configuration
STORAGE_PATH=storage

# WorkOS Authentication
WORKOS_API_KEY=your_workos_api_key_here
WORKOS_CLIENT_ID=your_workos_client_id_here
WORKOS_REDIRECT_URI=http://localhost:5173/auth/callback
WORKOS_COOKIE_SECRET=your_cookie_secret_here

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_DEFAULT_ASSISTANT_ID=your_openai_assistant_id_here

# RAG Configuration
CHAT_MODEL=gpt-4o-mini
MAX_TOKENS=1000

# Logging
LOG_LEVEL=INFO
```

### 3. Database Setup

Ensure PostgreSQL is running with the pgvector extension. You can use Docker Compose:

```bash
docker-compose up -d
```

Run database migrations:

```bash
make db.up
```

To create a new migration:

```bash
make db.make_migrations m="your migration message"
```

### 4. Start the Server

```bash
uv run python -m app.main
```

The API will be available at `http://localhost:8000`

API documentation (Swagger UI) is available at `http://localhost:8000/docs`

## Project Structure

```
api/
├── app/
│   ├── core/              # Core application modules
│   │   ├── config.py      # Configuration management
│   │   ├── exceptions.py  # Custom exceptions
│   │   └── logging.py     # Logging configuration
│   ├── modules/           # Feature modules
│   │   ├── auth/          # Authentication & authorization
│   │   │   ├── models.py           # User models
│   │   │   ├── repository.py      # Database access
│   │   │   ├── schema.py           # Pydantic schemas
│   │   │   ├── views.py            # API endpoints
│   │   │   ├── middleware.py       # Auth middleware
│   │   │   └── services/           # Business logic
│   │   ├── files/         # File management
│   │   │   ├── models.py           # File models
│   │   │   ├── repository.py       # Database access
│   │   │   ├── schema.py            # Pydantic schemas
│   │   │   ├── views.py             # API endpoints
│   │   │   └── service.py           # Business logic
│   │   └── rag/           # RAG functionality
│   │       ├── models.py            # QA models
│   │       ├── schema.py            # Pydantic schemas
│   │       ├── views.py             # API endpoints
│   │       ├── repositories/        # Database access
│   │       └── services/            # RAG services
│   │           ├── document_service.py        # Main RAG service
│   │           ├── vector_store_manager.py     # Vector store operations
│   │           ├── embeddings_service.py      # Embedding generation
│   │           ├── openai_service.py          # OpenAI integration
│   │           ├── audio_processing_service.py # Voice processing
│   │           ├── pdf_content_manager.py      # PDF processing
│   │           └── docx_content_manager.py     # DOCX processing
│   └── main.py           # FastAPI application entry point
├── migrations/            # Alembic database migrations
├── storage/               # Uploaded file storage directory
├── logs/                  # Application logs
└── tests/                 # Test suite
```

## API Endpoints

### Authentication (`/auth`)

| Method | Endpoint         | Description                  | Auth Required |
|--------|------------------|------------------------------|---------------|
| GET    | `/auth/login`    | Get WorkOS authorization URL | No            |
| GET    | `/auth/callback` | Handle OAuth callback        | No            |
| GET    | `/auth/logout`   | Logout user                  | No            |
| GET    | `/auth/me`       | Get current user information | Yes           |

### File Management (`/files`) - Admin Only

| Method | Endpoint                    | Description              |
|--------|-----------------------------|--------------------------|
| POST   | `/files/upload`             | Upload a file (PDF/DOCX) |
| GET    | `/files/`                   | List all uploaded files  |
| GET    | `/files/{file_id}`          | Get file details         |
| GET    | `/files/{file_id}/download` | Download a file          |
| DELETE | `/files/{file_id}`          | Delete a file            |

### RAG (`/rag`)

| Method | Endpoint                      | Description                  | Auth Required |
|--------|-------------------------------|------------------------------|---------------|
| POST   | `/rag/ask`                    | Ask a text-based question    | Yes           |
| POST   | `/rag/ask-voice`              | Ask a voice-based question   | Yes           |
| GET    | `/rag/history`                | Get question history         | Admin         |
| GET    | `/rag/session/{session_id}`   | Get session-specific history | Admin         |
| DELETE | `/rag/question/{question_id}` | Delete a question            | Admin         |
| GET    | `/rag/stats`                  | Get user statistics          | Admin         |

### User Management (`/auth/users`) - Admin Only

| Method | Endpoint                | Description       |
|--------|-------------------------|-------------------|
| POST   | `/auth/users`           | Create a new user |
| GET    | `/auth/users`           | List all users    |
| GET    | `/auth/users/{user_id}` | Get user details  |
| PUT    | `/auth/users/{user_id}` | Update a user     |
| DELETE | `/auth/users/{user_id}` | Delete a user     |

## Features

### Document Processing
- Supports PDF and DOCX file formats
- Automatic content extraction and chunking
- Duplicate detection using content hashing
- Vector embedding generation for semantic search

### RAG (Retrieval-Augmented Generation)
- Semantic search using vector similarity
- Context-aware answer generation with OpenAI
- Source citation and confidence scoring
- Support for images in documents

### Voice Processing
- Audio transcription using Whisper
- Voice-to-text conversion for questions
- Session-based conversation tracking

### Authentication & Authorization
- WorkOS integration for SSO
- Role-based access control (Admin/User)
- Secure session management

## Database Schema

### Users
- User accounts with WorkOS integration
- Role-based permissions (admin/user)

### Files
- File metadata storage
- Content hash for deduplication
- File type classification

### RAG
- Question and answer storage
- Session tracking
- Document chunk storage
- Image references

## Development

### Code Quality

```bash
# Format code
make black.run

# Lint and format
make ruff.run

# Type checking
make mypy.run
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app
```

### Database Migrations

```bash
# Create a new migration
make db.make_migrations m="description"

# Apply migrations
make db.up

# Rollback migrations
make db.down
```

## Dependencies

Key dependencies:
- `fastapi` - Web framework
- `sqlmodel` - SQL ORM
- `alembic` - Database migrations
- `openai` - OpenAI API client
- `sentence-transformers` - Embedding models
- `pgvector` - Vector similarity search
- `unstructured[all-docs]` - Document processing
- `whisper` - Audio transcription
- `workos` - Authentication provider

See `pyproject.toml` for the complete list.

## Configuration

All configuration is managed through environment variables. See `.env.example` for available options.

Important settings:
- Database connection details
- WorkOS credentials for authentication
- OpenAI API key for RAG functionality
- Storage paths and directories
- Logging configuration

## Logging

Logs are written to:
- `logs/api.log` - General application logs
- `logs/error.log` - Error logs

Log level is controlled by `LOG_LEVEL` environment variable.

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Verify database credentials in `.env`
- Check pgvector extension is installed

### File Upload Issues
- Ensure `STORAGE_PATH` directory exists and is writable
- Check file size limits
- Verify file type is PDF or DOCX

### Vector Store Issues
- Ensure `CHROMA_PERSIST_DIRECTORY` exists
- Check database connection for vector storage
- Verify embeddings service is working

### Authentication Issues
- Verify WorkOS credentials are correct
- Check redirect URI matches WorkOS configuration
- Ensure frontend URL is correctly configured
