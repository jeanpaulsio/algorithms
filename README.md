# Algorithms Practice

An algorithm practice application built with FastAPI.

## Local Development

### Prerequisites

- Python 3.13.3 (managed via `.tool-versions` if using asdf)
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

3. Activate the Poetry virtual environment:
```bash
poetry shell
```

4. Install Node.js dependencies and build Tailwind CSS:
```bash
yarn install
yarn build:css
```

**Note:** Poetry creates its own virtual environment. You can use `poetry shell` to activate it, or use `poetry run <command>` to run commands within the Poetry environment.

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

```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```
