import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.agenda import Issue

router = APIRouter(prefix="/api/v1/issues", tags=["issues"])


class IssueListOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    category: str | None
    canonical: bool


@router.get("/", response_model=list[IssueListOut])
async def list_issues(db: AsyncSession = Depends(get_db)) -> list[IssueListOut]:
    result = await db.scalars(select(Issue).order_by(Issue.category, Issue.title))
    return [
        IssueListOut(
            id=i.id,
            title=i.title,
            description=i.description,
            category=i.category,
            canonical=i.canonical,
        )
        for i in result.all()
    ]
