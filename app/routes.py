import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.code_executor import execute_code_secure
from app.database import get_db
from app.models import Problem

template_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(template_dir))

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def problem_list(
    request: Request,
    category: str | None = None,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    query = select(Problem)
    if category:
        query = query.where(Problem.category == category)
    problems = db.scalars(query).all()
    return templates.TemplateResponse("problems/list.html", {"request": request, "problems": problems})


@router.get("/problems/{problem_id}", response_class=HTMLResponse)
async def problem_detail(problem_id: uuid.UUID, request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    problem = db.scalar(select(Problem).where(Problem.id == problem_id))
    if not problem:
        return templates.TemplateResponse("problems/404.html", {"request": request}, status_code=404)
    return templates.TemplateResponse("problems/detail.html", {"request": request, "problem": problem})


class CodeSubmission(BaseModel):
    code: str


@router.post("/api/problems/{problem_id}/run", response_class=JSONResponse)
async def run_code(
    problem_id: uuid.UUID,
    submission: CodeSubmission,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """Execute user code against test cases."""
    problem = db.scalar(select(Problem).where(Problem.id == problem_id))
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    if not submission.code or not submission.code.strip():
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Code cannot be empty", "test_results": [], "output": ""},
        )

    # Limit code length to prevent abuse
    if len(submission.code) > 10000:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": "Code is too long (max 10000 characters)",
                "test_results": [],
                "output": "",
            },
        )

    # Execute code securely
    result = execute_code_secure(
        user_code=submission.code,
        test_code=str(problem.test_code),
        module_path=problem.module_path,
        timeout=5,
    )

    return JSONResponse(content=result)
