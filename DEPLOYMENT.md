# Deployment Guide - Reddit Worry Finder

## Quick Setup (Development)

### 1. Prerequisites
- Node.js 18+ with pnpm
- Python 3.11+ with uv (or pip)
- PostgreSQL with pgvector extension
- Redis server

### 2. Database Setup (Neon - Recommended)

```bash
# Sign up at https://neon.tech
# Create a new project with PostgreSQL 15+
# Enable pgvector extension in the Neon console
# Copy the connection string
```

### 3. Redis Setup (Upstash - Recommended)

```bash
# Sign up at https://upstash.com
# Create a new Redis database
# Copy the connection string
```

### 4. Reddit API Keys

```bash
# Go to https://www.reddit.com/prefs/apps
# Create a new "script" application
# Note down client_id and client_secret
```

### 5. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your credentials:

DATABASE_URL=postgresql+psycopg://user:pass@host/db
DATABASE_URL_SYNC=postgresql+psycopg://user:pass@host/db
REDIS_URL=redis://host:port
REDDIT_CLIENT_ID=your_client_id
REDDIT_SECRET=your_secret
REDDIT_USER_AGENT=your-app:v1.0.0 (by /u/yourusername)

# Optional for AI draft generation:
OPENROUTER_API_KEY=sk-or-v1-your-key
```

### 6. Installation & Setup

```bash
# Install dependencies
pnpm install

# Python API setup
cd services/api
uv venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
uv pip install -e .[dev]

# Database migration
alembic upgrade head

# Seed initial data
psql $DATABASE_URL < ../../infra/sql/002_seed_subreddits.sql
```

### 7. Start Development

```bash
# Terminal 1 - API
pnpm dev:api

# Terminal 2 - Web App
pnpm dev:web

# Terminal 3 - Worker (optional)
pnpm dev:worker

# Or all at once:
pnpm dev
```

### 8. Test the Application

```bash
# Open http://localhost:3000
# Try searching: "I have flaky scalp and dandruff issues"
# Check API directly: curl http://localhost:8000/v1/healthz
```

## Production Deployment

### Option 1: Vercel + Fly.io (Recommended)

#### Frontend (Vercel)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from apps/web directory
cd apps/web
vercel

# Set environment variables in Vercel dashboard:
# API_BASE_URL=https://your-api.fly.dev
```

#### Backend (Fly.io)
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Create Dockerfile for API
cat > services/api/Dockerfile << EOF
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install uv
RUN uv venv && uv pip install -e .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Deploy API
cd services/api
fly launch
fly deploy

# Deploy worker similarly
cd ../worker
fly launch
fly deploy
```

### Option 2: Railway (All-in-one)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy API
cd services/api
railway login
railway init
railway up

# Deploy worker
cd ../worker
railway init
railway up

# Deploy frontend
cd ../../apps/web
railway init
railway up
```

### Option 3: Docker Compose (Self-hosted)

```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_DB: reddit_finder
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build: ./services/api
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      DATABASE_URL: postgresql+psycopg://postgres:password@postgres:5432/reddit_finder
      REDIS_URL: redis://redis:6379/0

  worker:
    build: ./services/worker
    depends_on:
      - postgres
      - redis
    environment:
      REDIS_URL: redis://redis:6379/0

  web:
    build: ./apps/web
    ports:
      - "3000:3000"
    depends_on:
      - api
    environment:
      API_BASE_URL: http://api:8000

volumes:
  postgres_data:
```

## Environment Variables Reference

### Required
- `DATABASE_URL`: PostgreSQL connection string
- `DATABASE_URL_SYNC`: Same as above for migrations
- `REDIS_URL`: Redis connection string
- `REDDIT_CLIENT_ID`: Reddit API client ID
- `REDDIT_SECRET`: Reddit API secret
- `REDDIT_USER_AGENT`: Your app's user agent

### Optional
- `OPENROUTER_API_KEY`: For AI draft generation
- `USE_REDDIT_MOCK`: Set to "true" for development
- `USE_EMBEDDING_MOCK`: Set to "true" for faster development
- `DEBUG`: Set to "true" for debug logging

### Performance Tuning
- `MAX_SUBREDDITS_TO_SEARCH`: Default 10
- `MAX_POSTS_PER_SUBREDDIT`: Default 20
- `RATE_LIMIT_REQUESTS_PER_MINUTE`: Default 60

## Database Migration

```bash
# Check current version
cd services/api
source .venv/bin/activate
alembic current

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Monitoring & Logging

### Health Checks
- API: `GET /v1/healthz`
- Database: Check connection in health endpoint
- Redis: Check connection in health endpoint

### Logs
- API logs: Structured JSON logging
- Worker logs: Celery task logging
- Web logs: Next.js server logs

### Metrics (TODO)
- Request latency
- Search success rate
- User engagement
- Error rates

## Security Checklist

- [ ] Environment variables secured
- [ ] Database credentials rotated
- [ ] API rate limiting enabled
- [ ] CORS properly configured
- [ ] Input validation in place
- [ ] SQL injection protection
- [ ] XSS protection enabled

## Performance Optimization

### Database
- [ ] Enable pgvector indexes
- [ ] Connection pooling configured
- [ ] Query optimization
- [ ] Regular VACUUM and ANALYZE

### Caching
- [ ] Redis caching enabled
- [ ] Search result caching
- [ ] Subreddit metadata caching
- [ ] Rate limiting in place

### Frontend
- [ ] Build optimization
- [ ] Image optimization
- [ ] Code splitting
- [ ] CDN for static assets

## Backup & Recovery

### Database Backup
```bash
# Manual backup
pg_dump $DATABASE_URL > backup.sql

# Restore
psql $DATABASE_URL < backup.sql
```

### Automated Backups
- Use cloud provider backups (Neon, etc.)
- Set up monitoring for backup health
- Test restore procedures regularly

## Troubleshooting

### Common Issues

1. **Embedding model download fails**
   - Set `USE_EMBEDDING_MOCK=true` for development
   - Ensure sufficient disk space for model cache

2. **Reddit API rate limiting**
   - Check Reddit API status
   - Implement exponential backoff
   - Use `USE_REDDIT_MOCK=true` for testing

3. **Database connection issues**
   - Check connection string format
   - Verify pgvector extension enabled
   - Check firewall rules

4. **Worker not processing tasks**
   - Verify Redis connection
   - Check Celery logs
   - Restart worker service

### Debug Mode
```bash
# Enable debug logging
export DEBUG=true

# Check API logs
cd services/api && uvicorn main:app --log-level debug

# Check worker logs
cd services/worker && celery -A app worker --loglevel=debug
```

## Support

- GitHub Issues: Bug reports and feature requests
- Documentation: Check README.md and code comments
- Community: GitHub Discussions

---

**Next Steps After Deployment:**
1. Monitor application health
2. Set up error tracking
3. Configure automated backups
4. Plan scaling strategy
5. Implement authentication system
