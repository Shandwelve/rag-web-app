# RAG Web Application

A full-stack Retrieval-Augmented Generation (RAG) web application that allows users to upload documents and interact with them through natural language questions and voice queries.

## Features

- **Document Management**: Upload and manage PDF and DOCX documents
- **RAG Question Answering**: Ask questions about uploaded documents using natural language
- **Voice Input**: Submit questions via voice recordings
- **Authentication**: Secure authentication using WorkOS
- **User Management**: Admin panel for managing users
- **Question History**: View and manage question-answer history
- **Statistics**: View usage statistics and analytics
- **Vector Search**: Advanced semantic search using embeddings and vector similarity

## Project Structure

```
rag-web-app/
├── api/                 # FastAPI backend
│   ├── app/
│   │   ├── core/       # Core functionality (config, logging, exceptions)
│   │   ├── modules/    # Feature modules
│   │   │   ├── auth/   # Authentication & user management
│   │   │   ├── files/  # File upload & management
│   │   │   └── rag/    # RAG functionality
│   │   └── main.py     # FastAPI application entry point
│   ├── migrations/     # Database migrations (Alembic)
│   ├── storage/        # Uploaded file storage
│   └── tests/          # Test suite
├── client/             # React frontend
│   ├── src/
│   │   ├── components/ # React components
│   │   ├── services/   # API service clients
│   │   └── contexts/  # React contexts
└── docker-compose.yml  # Docker configuration
```

## Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL with pgvector extension
- **Vector Store**: PG Vector
- **Authentication**: WorkOS
- **AI/ML**: OpenAI GPT models, Sentence Transformers
- **File Processing**: Unstructured library
- **Audio Processing**: Whisper, librosa, pydub

### Frontend
- **Framework**: React 19 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui (built on Radix UI primitives)
- **State Management**: React Context API

## Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL 14+ with pgvector extension
- Docker and Docker Compose (optional, for database)
- UV package manager (for Python)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd rag-web-app
```

### 2. Database Setup

Start the PostgreSQL database using Docker Compose:

```bash
docker-compose up -d
```

Or use your own PostgreSQL instance with pgvector extension installed.

### 3. Backend Setup

Navigate to the API directory:

```bash
cd api
```

Install dependencies using UV:

```bash
uv sync
```

Create a `.env` file from `.env.example` and configure your environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration values
```

See [API README](api/README.md) for detailed environment variable configuration.

Run database migrations:

```bash
make db.up
```

Start the API server:

```bash
uv run python -m app.main
```

The API will be available at `http://localhost:8000`

### 4. Frontend Setup

Navigate to the client directory:

```bash
cd client
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage

### Makefile Commands

The project includes a Makefile with convenient commands:

```bash
# Database
make db.make_migrations  # Generate migrations (requires m=<message>)
make db.up              # Run migrations
make db.down            # Rollback migrations

# Code Quality
make black.run          # Format code with Black
make ruff.run           # Lint and format with Ruff
make mypy.run           # Type check with MyPy

# Application
make app.start          # Start both API and client servers
make app.stop           # Stop all running processes
```

### Workflow

1. **Start Services**: Use `make app.start` to start both backend and frontend
2. **Login**: Access the application and authenticate via WorkOS
3. **Upload Documents**: Admin users can upload PDF or DOCX files
4. **Ask Questions**: Use the chat interface to ask questions about uploaded documents
5. **Voice Queries**: Record audio questions for voice-based interaction
6. **View History**: Access question history and statistics in the admin panel

## API Endpoints

### Authentication
- `GET /auth/login` - Get authorization URL
- `GET /auth/callback` - Handle OAuth callback
- `GET /auth/logout` - Logout user
- `GET /auth/me` - Get current user info

### Files (Admin Only)
- `POST /files/upload` - Upload a file
- `GET /files/` - List all files
- `GET /files/{file_id}` - Get file details
- `GET /files/{file_id}/download` - Download a file
- `DELETE /files/{file_id}` - Delete a file

### RAG
- `POST /rag/ask` - Ask a text question
- `POST /rag/ask-voice` - Ask a voice question
- `GET /rag/history` - Get question history (Admin)
- `GET /rag/session/{session_id}` - Get session history (Admin)
- `DELETE /rag/question/{question_id}` - Delete a question (Admin)
- `GET /rag/stats` - Get user statistics (Admin)

### Users (Admin Only)
- `POST /auth/users` - Create a user
- `GET /auth/users` - List users
- `GET /auth/users/{user_id}` - Get user details
- `PUT /auth/users/{user_id}` - Update a user
- `DELETE /auth/users/{user_id}` - Delete a user

## Development

### Running Tests

```bash
cd api
uv run pytest
```

### Code Formatting

```bash
make black.run
make ruff.run
```

### Type Checking

```bash
make mypy.run
```

## Environment Variables

See [API README](api/README.md) for detailed environment variable configuration.
