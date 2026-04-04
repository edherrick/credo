from pydantic import BaseModel


class GeographyOut(BaseModel):
    id: str
    name: str
    state_fips: str
    geo_type: str

    model_config = {"from_attributes": True}
