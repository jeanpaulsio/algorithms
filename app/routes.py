import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import select

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
