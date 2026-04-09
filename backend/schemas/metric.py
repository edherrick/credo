import datetime

from pydantic import BaseModel


class MetricOut(BaseModel):
    id: str
    display_name: str
    unit: str
    description: str | None
    data_source: str | None

    model_config = {"from_attributes": True}


class MetricValuePoint(BaseModel):
    period_start: datetime.date
    period_end: datetime.date | None = None
    value: float


class MetricValuesOut(BaseModel):
    metric_id: str
    geography_id: str
    unit: str
    values: list[MetricValuePoint]


class CountySeries(BaseModel):
    id: str
    name: str
    values: list[float | None]


class MetricAggregateOut(BaseModel):
    metric_id: str
    dates: list[str]
    avg_values: list[float]
    counties: list[CountySeries]
