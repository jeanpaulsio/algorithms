# Algorithms Practice

An algorithm practice application built with FastAPI.

## Local Development

### Prerequisites

- Python 3.13.3 (managed via `.tool-versions` if using asdf)
- Poetry
- Node.js and yarn (for Tailwind CSS)
- PostgreSQL (for local database)

### Setup

1. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install Python dependencies:
```bash
poetry install
```

3. Install Node.js dependencies and build Tailwind CSS:
```bash
yarn install
yarn build:css
```

4. Set up the database:
```bash
# Create the database (PostgreSQL must be running)
createdb algorithms

# Or if you prefer a different name, set DATABASE_URL:
# export DATABASE_URL="postgresql+asyncpg://localhost/your_db_name"

# Run migrations to create tables
poetry run alembic upgrade head

# Seed initial data
poetry run python -m app.seed

# To reseed (clear and re-add):
poetry run python -m app.seed --clear
```

### Running the Application

**Using Overmind:**
```bash
overmind start -f Procfile.dev
```

The application will be available at `http://localhost:8000`

### Updating Dependencies

**Add a dependency:**
```bash
poetry add package-name
```

**Add a dev dependency:**
```bash
poetry add --group dev package-name
```

**Update dependencies:**
```bash
poetry update
```
