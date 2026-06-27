import uuid
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models.agenda import Agenda
from models.credo import (
    Belief,
    CredoBelief,
    Credo,
    CredoEntity,
    CredoSubscription,
    Entity,
    EntityEvent,
)
from models.user import User
from routes.auth import current_active_user
from schemas.belief import CredoBeliefCreate, CredoBeliefOut
from schemas.credo import CredoCreate, CredoOut, CredoSummaryOut, CredoUpdate
from schemas.entity import CredoEntityOut, EntityEventOut
from serializers import build_agenda_outs

router = APIRouter(prefix="/api/v1/credos", tags=["credos"])


async def _load_credo(username: str, db: AsyncSession) -> Credo:
    """Resolve a credo by handle or raise 404. Shared by owner-scoped and follow writes."""
    credo = await db.scalar(select(Credo).where(Credo.username == username))
    if not credo:
        raise HTTPException(status_code=404, detail="Credo not found")
    return credo


async def get_owned_credo(
    username: str,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Credo:
    """Load a credo by handle and assert the caller owns it.

    This is the reference authorization pattern for mutating a resource: resolve
    the object, 404 if missing, 403 if the authenticated user is not the owner.
    Reuse it as a dependency on any owner-only write endpoint under /{username}.
    """
    credo = await _load_credo(username, db)
    if credo.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this credo")
    return credo


@router.get("", response_model=list[CredoSummaryOut])
async def list_credos(db: AsyncSession = Depends(get_db)) -> list[CredoSummaryOut]:
    result = await db.scalars(select(Credo).order_by(Credo.created_at.desc()))
    return [CredoSummaryOut.model_validate(c) for c in result.all()]


@router.get("/following", response_model=list[CredoSummaryOut])
async def list_following(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[CredoSummaryOut]:
    """Credos the authenticated user follows, newest first.

    Declared before the dynamic ``/{username}`` route so "following" isn't parsed
    as a credo handle.
    """
    result = await db.scalars(
        select(Credo)
        .join(CredoSubscription, CredoSubscription.credo_id == Credo.id)
        .where(CredoSubscription.user_id == user.id)
        .order_by(Credo.created_at.desc())
    )
    return [CredoSummaryOut.model_validate(c) for c in result.all()]


@router.get("/{username}", response_model=CredoOut)
async def get_credo(username: str, db: AsyncSession = Depends(get_db)) -> CredoOut:
    credo = await db.scalar(select(Credo).where(Credo.username == username))
    if not credo:
        raise HTTPException(status_code=404, detail="Credo not found")

    # Founding beliefs for this credo, ordered by display_order
    beliefs_rows = await db.scalars(
        select(CredoBelief)
        .where(CredoBelief.credo_id == credo.id)
        .options(selectinload(CredoBelief.belief))
        .order_by(CredoBelief.display_order)
    )
    beliefs = [CredoBeliefOut.model_validate(cb) for cb in beliefs_rows.all()]

    # Agendas belonging to this credo, with their means assembled
    agendas = (
        await db.scalars(
            select(Agenda)
            .where(Agenda.credo_id == credo.id, Agenda.status == "active")
            .options(selectinload(Agenda.geographies))
        )
    ).all()
    agenda_outs = await build_agenda_outs(db, agendas)

    # Entities linked to this credo via junction, ordered by score
    rows = (
        await db.execute(
            select(CredoEntity, Entity)
            .join(Entity, CredoEntity.entity_id == Entity.id)
            .where(CredoEntity.credo_id == credo.id)
            .order_by(CredoEntity.impact_score.desc())
        )
    ).all()

    if rows:
        entity_ids = [row.Entity.id for row in rows]
        events_result = await db.scalars(
            select(EntityEvent)
            .where(EntityEvent.entity_id.in_(entity_ids), EntityEvent.reviewed == True)  # noqa: E712
            .order_by(EntityEvent.event_date.desc())
        )
        events_by_entity: dict = defaultdict(list)
        for ev in events_result.all():
            events_by_entity[ev.entity_id].append(EntityEventOut.model_validate(ev))
    else:
        events_by_entity = defaultdict(list)

    return CredoOut(
        id=credo.id,
        username=credo.username,
        title=credo.title,
        description=credo.description,
        owner_id=credo.owner_id,
        beliefs=beliefs,
        agendas=agenda_outs,
        entities=[
            CredoEntityOut(
                id=row.Entity.id,
                name=row.Entity.name,
                type=row.Entity.type,
                description=row.Entity.description,
                impact_score=row.CredoEntity.impact_score,
                events=events_by_entity[row.Entity.id],
            )
            for row in rows
        ],
    )


# ── Writes ──────────────────────────────────────────────────────────────────
# Reference pattern for authenticated, owner-scoped mutations. New write
# resources should follow this shape: a *Create / *Update schema for input
# validation, current_active_user for authn, and (for owner-only operations)
# the get_owned_credo dependency for authz.


@router.post("", response_model=CredoSummaryOut, status_code=status.HTTP_201_CREATED)
async def create_credo(
    payload: CredoCreate,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
) -> CredoSummaryOut:
    """Create a credo owned by the authenticated user. 409 if the handle is taken."""
    existing = await db.scalar(select(Credo).where(Credo.username == payload.username))
    if existing:
        raise HTTPException(status_code=409, detail="That handle is already taken")

    credo = Credo(
        username=payload.username,
        title=payload.title,
        description=payload.description,
        owner_id=user.id,
    )
    db.add(credo)
    await db.commit()
    await db.refresh(credo)
    return CredoSummaryOut.model_validate(credo)


@router.patch("/{username}", response_model=CredoSummaryOut)
async def update_credo(
    payload: CredoUpdate,
    credo: Credo = Depends(get_owned_credo),
    db: AsyncSession = Depends(get_db),
) -> CredoSummaryOut:
    """Update a credo the caller owns. Only fields present in the body are changed."""
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(credo, field, value)
    await db.commit()
    await db.refresh(credo)
    return CredoSummaryOut.model_validate(credo)


@router.delete("/{username}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_credo(
    credo: Credo = Depends(get_owned_credo),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a credo the caller owns. 409 if other rows still reference it."""
    await db.delete(credo)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Credo still has linked agendas; detach them before deleting.",
        ) from exc


# ── Follow / unfollow ────────────────────────────────────────────────────────
# Self-membership writes: the caller toggles only their own subscription row, so
# no ownership check — any authenticated user may follow any credo. Both verbs are
# idempotent (the (user, credo) primary key makes a repeat follow a no-op).


@router.post("/{username}/follow", status_code=status.HTTP_204_NO_CONTENT)
async def follow_credo(
    username: str,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Follow a credo. No-op if already following."""
    credo = await _load_credo(username, db)
    existing = await db.get(CredoSubscription, (user.id, credo.id))
    if existing is None:
        db.add(CredoSubscription(user_id=user.id, credo_id=credo.id))
        await db.commit()


@router.delete("/{username}/follow", status_code=status.HTTP_204_NO_CONTENT)
async def unfollow_credo(
    username: str,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Unfollow a credo. No-op if not currently following."""
    credo = await _load_credo(username, db)
    existing = await db.get(CredoSubscription, (user.id, credo.id))
    if existing is not None:
        await db.delete(existing)
        await db.commit()


# ── Credo founding beliefs (owner-scoped) ────────────────────────────────────
# Mutating a credo's belief set is an owner-scoped write on the credo itself, so
# it reuses get_owned_credo — no new authz mechanism needed. (A credo's beliefs
# are a sub-resource of the credo, unlike the self-membership saves on /beliefs.)


@router.post("/{username}/beliefs", status_code=status.HTTP_201_CREATED)
async def add_credo_belief(
    payload: CredoBeliefCreate,
    credo: Credo = Depends(get_owned_credo),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Adopt an existing library belief into a credo you own. 409 if already present."""
    belief = await db.get(Belief, payload.belief_id)
    if belief is None:
        raise HTTPException(status_code=404, detail="Belief not found")
    existing = await db.get(CredoBelief, (credo.id, payload.belief_id))
    if existing is not None:
        raise HTTPException(status_code=409, detail="That belief is already in this credo")
    db.add(
        CredoBelief(
            credo_id=credo.id,
            belief_id=payload.belief_id,
            display_order=payload.display_order,
            notes=payload.notes,
        )
    )
    await db.commit()


@router.delete(
    "/{username}/beliefs/{belief_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_credo_belief(
    belief_id: uuid.UUID,
    credo: Credo = Depends(get_owned_credo),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove a belief from a credo you own. No-op if not present."""
    existing = await db.get(CredoBelief, (credo.id, belief_id))
    if existing is not None:
        await db.delete(existing)
        await db.commit()
