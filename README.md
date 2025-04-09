# BiteBase Intelligence Backend

This is the backend API for the BiteBase Intelligence platform, providing data analytics and insights for restaurants and food businesses.

## Features

- User authentication with Firebase
- Data analytics APIs
- AI-powered insights
- Restaurant performance metrics
- Menu optimization
- Competitor analysis
- Demographic insights
- Foot traffic analysis

## Tech Stack

- Python 3.11+
- FastAPI
- Firebase Authentication
- Firestore Database
- Cloudflare Workers (for deployment)

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Firebase project with Authentication and Firestore enabled

### Installation

1. Clone the repository

```bash
git clone https://github.com/BiteBase-app/beta.backend.bitebase.app.git
cd beta.backend.bitebase.app
```

2. Set up a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Set up environment variables

Create a `.env` file in the root directory with the following variables:

```
ENVIRONMENT=development
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
```

For Firebase Admin SDK, either:
- Place your service account JSON file in the root directory as `bitebase-3d5f9-1475e1373cfa.json`
- Or add the following environment variables to your `.env` file:

```
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=your-client-email
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_CLIENT_CERT_URL=your-client-cert-url
```

5. Run the application

```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

When running in development mode, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Run tests with pytest:

```bash
pytest
```

For test coverage:

```bash
pytest --cov=app tests/
```

## Deployment

### Using Cloudflare Workers

1. Install Wrangler CLI

```bash
npm install -g wrangler
```

2. Deploy to Cloudflare Workers

```bash
wrangler deploy
```

### Using Docker

1. Build the Docker image

```bash
docker build -t bitebase-backend .
```

2. Run the container

```bash
docker run -p 8000:8000 bitebase-backend
```

## Project Structure

```
├── app/                    # Application code
│   ├── apis/               # API endpoints
│   ├── auth/               # Authentication logic
│   ├── core/               # Core functionality
│   ├── middleware/         # Middleware components
│   └── config.py           # Configuration
├── tests/                  # Test suite
├── .env                    # Environment variables
├── .env.production         # Production environment variables
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
└── wrangler.toml           # Cloudflare Workers configuration
```

## License

Proprietary - All rights reserved
