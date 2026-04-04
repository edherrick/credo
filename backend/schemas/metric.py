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
    date: datetime.date
    value: float


class MetricValuesOut(BaseModel):
    metric_id: str
    geography_id: str
    unit: str
    values: list[MetricValuePoint]
