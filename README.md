# Algorithms Practice

An algorithm practice application built with FastAPI.

## Local Development

### Prerequisites

- Python 3.13.3 (managed via `.tool-versions` if using asdf)
- pip
- Node.js and yarn (for Tailwind CSS)

### Setup

1. Create a virtual environment:
```bash
python -m venv .venv
```

2. Activate the virtual environment:
```bash
source .venv/bin/activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Install Node.js dependencies and build Tailwind CSS:
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

If you modify `pyproject.toml`, regenerate `requirements.txt`:
```bash
pip-compile pyproject.toml -o requirements.txt
```
