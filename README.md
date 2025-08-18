# reddit this. - Find Your Community

A modern web application that helps users discover meaningful conversations and get personalized advice from Reddit communities.

## Features

- **Semantic Search**: Uses AI embeddings to find relevant Reddit posts based on meaning, not just keywords
- **Smart Subreddit Discovery**: Automatically finds the most relevant subreddits for your concern
- **Post Ranking**: Composite scoring algorithm considering relevance, recency, community quality, and engagement
- **Draft Generation**: AI-powered or template-based Reddit post generation
- **Alert System**: (Coming soon) Get notified when new relevant posts are found

## Tech Stack

### Frontend
- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** + **shadcn/ui** for styling
- **TanStack Query** for data fetching
- **Zod** for validation

### Backend
- **FastAPI** for the REST API
- **SQLAlchemy 2.x** with **Alembic** for database management
- **Postgres** with **pgvector** for vector similarity search
- **Redis** for caching and rate limiting
- **Celery** for background tasks

### AI & Search
- **sentence-transformers** (E5-small-v2) for embeddings
- **asyncpraw** for Reddit API integration
- **YAKE** for keyphrase extraction
- **RapidFuzz** for fuzzy matching

### Infrastructure
- **Turborepo** monorepo setup
- **GitHub Actions** CI/CD
- **Docker** ready (TODO)

## Project Structure

```
.
├─ apps/
│  └─ web/                  # Next.js frontend
├─ services/
│  ├─ api/                  # FastAPI backend
│  └─ worker/               # Celery worker
├─ packages/
│  └─ types/                # Shared TypeScript types
├─ infra/
│  └─ sql/                  # Database setup and seeds
└─ .github/workflows/       # CI/CD pipelines
```

## Getting Started

### Prerequisites

- Node.js 18+ and pnpm
- Python 3.11+
- PostgreSQL with pgvector extension
- Redis

### Environment Setup

1. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your configuration:
   ```bash
   # Database (use Neon for easy pgvector setup)
   DATABASE_URL=postgresql+psycopg://user:pass@host/db
   DATABASE_URL_SYNC=postgresql+psycopg://user:pass@host/db
   
   # Redis (use Upstash for managed Redis)
   REDIS_URL=redis://localhost:6379/0
   
   # Reddit API (get from https://www.reddit.com/prefs/apps)
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_SECRET=your_secret
   REDDIT_USER_AGENT=your-app:v1.0.0 (by /u/yourusername)
   
   # Optional: OpenRouter for AI draft generation
   OPENROUTER_API_KEY=sk-or-v1-your-key
   ```

### Development

1. Install dependencies:
   ```bash
   pnpm install
   cd services/api && uv venv && uv pip install -e .[dev]
   ```

2. Set up database:
   ```bash
   cd services/api
   source .venv/bin/activate
   alembic upgrade head
   ```

3. Start development servers:
   ```bash
   # Terminal 1: API
   pnpm dev:api
   
   # Terminal 2: Web app
   pnpm dev:web
   
   # Terminal 3: Worker (optional)
   pnpm dev:worker
   
   # Or all at once:
   pnpm dev
   ```

4. Open http://localhost:3000

### Testing the API

```bash
# Health check
curl http://localhost:8000/v1/healthz

# Search example
curl -X POST http://localhost:8000/v1/ingest/search \\
  -H "Content-Type: application/json" \\
  -d '{"text": "I have flaky scalp and dandruff, what products work?"}'

# Generate draft
curl -X POST http://localhost:8000/v1/draft \\
  -H "Content-Type: application/json" \\
  -d '{"text": "Need help with dry hair", "region": "Australia"}'
```

## Development Workflow

### Code Quality

- **Linting**: ESLint (TS/JS), Ruff (Python)
- **Formatting**: Prettier (TS/JS), Black (Python)
- **Type Checking**: TypeScript, mypy
- **Pre-commit hooks**: Configured for all tools

### Scripts

```bash
# Frontend
pnpm dev:web          # Start Next.js dev server
pnpm build            # Build all packages
pnpm lint             # Lint all packages
pnpm typecheck        # Type check all packages

# Backend
pnpm dev:api          # Start FastAPI with auto-reload
pnpm python:lint      # Lint Python code
pnpm python:format    # Format Python code

# Type generation
pnpm gen:types        # Generate TS types from OpenAPI schema
```

## Configuration

### Development Flags

- `USE_REDDIT_MOCK=true`: Use mock Reddit responses
- `USE_EMBEDDING_MOCK=true`: Use mock embeddings (faster, no model download)
- `DEBUG=true`: Enable debug logging

### Search Configuration

- `MAX_SUBREDDITS_TO_SEARCH`: Limit subreddits searched (default: 10)
- `MAX_POSTS_PER_SUBREDDIT`: Limit posts per subreddit (default: 20)
- `EMBEDDING_DIMENSION`: Vector dimension for pgvector (default: 384)

## API Endpoints

### Search
- `POST /v1/ingest/search` - Semantic search for relevant posts
- `GET /v1/metrics` - Search metrics and statistics

### Draft Generation
- `POST /v1/draft` - Generate Reddit post draft

### Alerts (TODO)
- `POST /v1/alerts` - Create new alert
- `GET /v1/alerts` - List user alerts
- `PATCH /v1/alerts/{id}` - Update alert
- `DELETE /v1/alerts/{id}` - Delete alert

### Health
- `GET /v1/healthz` - Health check

## Ranking Algorithm

Posts are ranked using a composite score:

- **45%** Semantic similarity (embedding cosine similarity)
- **20%** Recency (sigmoid function, peaks at ~9 months)
- **15%** Subreddit quality (subscriber count, activity)
- **10%** Post score (normalized per subreddit)
- **10%** Comment count (normalized per subreddit)

## Deployment

### Production Setup

1. **Database**: Neon PostgreSQL with pgvector
2. **Cache**: Upstash Redis
3. **Frontend**: Vercel
4. **Backend**: Fly.io or Railway
5. **Monitoring**: (TODO) OpenTelemetry + dashboards

### Environment Variables

See `.env.example` for all required variables.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Roadmap

- [ ] **Authentication**: Clerk or NextAuth integration
- [ ] **Alert System**: Background scanning and notifications
- [ ] **Advanced Search**: Cross-encoder reranking
- [ ] **Offline Indexing**: Pre-index popular subreddits
- [ ] **Mobile App**: React Native app
- [ ] **Analytics**: Usage analytics and insights
- [ ] **API Rate Limiting**: More sophisticated rate limiting
- [ ] **Caching**: Intelligent result caching

## License

MIT License - see LICENSE file for details.

## Support

- GitHub Issues for bug reports and feature requests
- Discussions for questions and community support

---

Built with ❤️ for the Reddit community
