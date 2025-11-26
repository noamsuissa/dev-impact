# Dev Impact Backend

FastAPI backend for Dev Impact application with GitHub OAuth Device Flow authentication.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
uvicorn main:app --reload
```

Or using Python directly:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

### GitHub OAuth Device Flow

- `POST /api/auth/github/device/code` - Initiate device flow
- `POST /api/auth/github/device/poll` - Poll for authorization
- `POST /api/auth/github/user` - Get user profile

## Environment Variables

See `.env.example` for configuration options.

