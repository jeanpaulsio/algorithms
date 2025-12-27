# Algorithms Practice

An algorithm practice application built with FastAPI.

## Local Development

### Prerequisites

- Python 3.13.3 (managed via `.tool-versions` if using asdf)
- Poetry
- Poetry
- Node.js and yarn (for Tailwind CSS)

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
3. Install Node.js dependencies and build Tailwind CSS:
```bash
yarn install
yarn build:css
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
