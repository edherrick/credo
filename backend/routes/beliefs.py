import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.credo import Belief, UserBelief
from models.user import User
from routes.auth import current_active_user
from schemas.belief import BeliefOut

router = APIRouter(prefix="/api/v1/beliefs", tags=["beliefs"])


@router.get("", response_model=list[BeliefOut])
async def list_beliefs(db: AsyncSession = Depends(get_db)) -> list[BeliefOut]:
    result = await db.scalars(select(Belief).order_by(Belief.category, Belief.title))
    return [BeliefOut.model_validate(b) for b in result.all()]


# ── Personal saved beliefs ───────────────────────────────────────────────────
# Self-membership writes (same shape as credo follow): the caller toggles only
# their own (user, belief) row — idempotent, no ownership check. Declared before
# any dynamic belief route so "saved" isn't parsed as an id.


@router.get("/saved", response_model=list[BeliefOut])
async def list_saved_beliefs(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[BeliefOut]:
    """Beliefs the authenticated user has saved to their personal collection."""
    result = await db.scalars(
        select(Belief)
        .join(UserBelief, UserBelief.belief_id == Belief.id)
        .where(UserBelief.user_id == user.id)
        .order_by(Belief.category, Belief.title)
    )
    return [BeliefOut.model_validate(b) for b in result.all()]


async def _load_belief(belief_id: uuid.UUID, db: AsyncSession) -> Belief:
    belief = await db.get(Belief, belief_id)
    if belief is None:
        raise HTTPException(status_code=404, detail="Belief not found")
    return belief


@router.get("/{belief_id}", response_model=BeliefOut)
async def get_belief(
    belief_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> BeliefOut:
    """A single belief's full detail. (Declared after /saved so it isn't shadowed.)"""
    return BeliefOut.model_validate(await _load_belief(belief_id, db))


@router.post("/{belief_id}/save", status_code=status.HTTP_204_NO_CONTENT)
async def save_belief(
    belief_id: uuid.UUID,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Save a belief to the caller's collection. No-op if already saved."""
    await _load_belief(belief_id, db)
    existing = await db.get(UserBelief, (user.id, belief_id))
    if existing is None:
        db.add(UserBelief(user_id=user.id, belief_id=belief_id))
        await db.commit()


@router.delete("/{belief_id}/save", status_code=status.HTTP_204_NO_CONTENT)
async def unsave_belief(
    belief_id: uuid.UUID,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove a belief from the caller's collection. No-op if not saved."""
    existing = await db.get(UserBelief, (user.id, belief_id))
    if existing is not None:
        await db.delete(existing)
        await db.commit()
