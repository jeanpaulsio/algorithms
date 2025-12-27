# Algorithms Practice

An algorithm practice application built with FastAPI.

## Local Development

### Prerequisites

- Python 3.13.3 (managed via `.tool-versions` if using asdf)
- pip

### Setup

1. Create a virtual environment:
```bash
python -m venv .venv
```

2. Activate the virtual environment:
```bash
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

Start the development server:
```bash
uvicorn app.main:app --reload
```

The application will be available at `http://localhost:8000`

### Updating Dependencies

If you modify `pyproject.toml`, regenerate `requirements.txt`:
```bash
pip-compile pyproject.toml -o requirements.txt
```
