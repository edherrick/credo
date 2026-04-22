from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models.agenda import Agenda, AgendaMeans, Means
from schemas.agenda import AgendaMeansOut, AgendaOut, MeansCategoryOut, MeansEvidenceOut, MeansOut

router = APIRouter(prefix="/api/v1/agendas", tags=["agendas"])


@router.get("", response_model=list[AgendaOut])
async def list_agendas(db: AsyncSession = Depends(get_db)) -> list[AgendaOut]:
    agendas_result = await db.scalars(
        select(Agenda)
        .where(Agenda.status == "active")
        .options(selectinload(Agenda.geographies))
    )
    agendas = agendas_result.all()

    agenda_ids = [a.id for a in agendas]
    means_by_agenda: dict = defaultdict(list)
    if agenda_ids:
        # Load junction rows; Means + MeansCategory + MeansEvidence are
        # eager-loaded via the relationships defined on AgendaMeans and Means.
        junction_result = await db.scalars(
            select(AgendaMeans)
            .where(AgendaMeans.agenda_id.in_(agenda_ids))
            .options(
                selectinload(AgendaMeans.means).selectinload(Means.category),
                selectinload(AgendaMeans.means).selectinload(Means.evidence),
            )
        )
        for jrow in junction_result.all():
            m = jrow.means
            means_by_agenda[jrow.agenda_id].append(
                AgendaMeansOut(
                    means_id=m.id,
                    notes=jrow.notes,
                    means=MeansOut(
                        id=m.id,
                        title=m.title,
                        description=m.description,
                        canonical=m.canonical,
                        category=MeansCategoryOut(
                            id=m.category.id,
                            label=m.category.label,
                            family=m.category.family,
                            description=m.category.description,
                        ),
                        evidence=[
                            MeansEvidenceOut(
                                id=e.id,
                                title=e.title,
                                description=e.description,
                                source_url=e.source_url,
                                geography_id=e.geography_id,
                                outcome=e.outcome,
                            )
                            for e in m.evidence
                        ],
                    ),
                )
            )

    return [
        AgendaOut(
            id=a.id,
            title=a.title,
            metric_id=a.metric_id,
            credo_id=a.credo_id,
            geography_ids=[g.geography_id for g in a.geographies],
            direction=a.direction,
            target_value=float(a.target_value) if a.target_value is not None else None,
            target_date=a.target_date,
            status=a.status,
            means=means_by_agenda[a.id],
        )
        for a in agendas
    ]
