# PostgreSQL Setup Guide

This project now supports PostgreSQL as the production database.

## Prerequisites

### Option 1: Local PostgreSQL Installation

**Windows:**
1. Download from https://www.postgresql.org/download/windows/
2. Run the installer and remember your password for the `postgres` user
3. PostgreSQL service will start automatically

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Option 2: Cloud PostgreSQL (Production)

**Railway** (Recommended - Free tier available)
1. Sign up at https://railway.app
2. Create new project → Add PostgreSQL
3. Copy the connection URL from the database settings

**Render** (Free tier available)
1. Sign up at https://render.com
2. Create new PostgreSQL database
3. Copy the external connection string

**Supabase** (Free tier available)
1. Sign up at https://supabase.com
2. Create new project
3. Get connection string from project settings

## Setup Steps

### 1. Install PostgreSQL Driver

The driver is already installed in your venv:
```bash
pip install psycopg2-binary
```

### 2. Create Database

**Local PostgreSQL:**
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE plates_db;

# Create user (optional)
CREATE USER plates_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE plates_db TO plates_user;

# Exit
\q
```

### 3. Configure Connection

Update your `.env` file or set environment variable:

**Local:**
```bash
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/plates_db
```

**Cloud (Railway/Render/AWS):**
```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

### 4. Initialize Database

The tables will be created automatically when you start the app:

```bash
python backend/app.py
```

Or manually:
```python
from backend.app import app, db
with app.app_context():
    db.create_all()
```

### 5. Verify Connection

Test the connection:
```bash
python -c "from backend.app import app; c=app.test_client(); print(c.get('/api/health').data.decode())"
```

## Migration from SQLite

If you have existing SQLite data:

**Option 1: Fresh Start**
- Just switch `DATABASE_URL` - tables will be created empty

**Option 2: Migrate Data**
```bash
# Export SQLite data
sqlite3 plates.db .dump > data.sql

# Import to PostgreSQL (may need manual adjustments)
psql -U postgres -d plates_db < data.sql
```

## Troubleshooting

**Connection refused:**
- Ensure PostgreSQL is running: `sudo systemctl status postgresql` (Linux)
- Check firewall settings
- Verify host/port in connection string

**Authentication failed:**
- Double-check username/password
- For local PostgreSQL, check `pg_hba.conf` authentication method

**Table doesn't exist:**
- Run `db.create_all()` or restart the app to auto-create tables

**SSL required (cloud databases):**
Add `?sslmode=require` to your connection string:
```bash
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
```

## Performance Tips

1. **Add indexes** for frequently queried fields (already configured in models)
2. **Connection pooling** - SQLAlchemy handles this automatically
3. **Use environment variables** - never commit credentials to git

## Production Checklist

- [ ] Set strong `SECRET_KEY` in environment
- [ ] Use PostgreSQL (not SQLite)
- [ ] Enable SSL for database connection
- [ ] Set up regular backups
- [ ] Monitor connection pool size
- [ ] Use read replicas for heavy read workloads (advanced)

## Reverting to SQLite

Simply change back in `.env`:
```bash
DATABASE_URL=sqlite:///plates.db
```
