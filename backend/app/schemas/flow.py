from pydantic import BaseModel, Field


class FlowRecord(BaseModel):
    reporter_iso3: str
    reporter_name: str
    reporter_lat: float
    reporter_lon: float
    partner_iso3: str
    partner_name: str
    partner_lat: float
    partner_lon: float
    commodity: str
    year: int
    flow_type: str
    value_usd: int
    weight_kg: int | None


class FlowFilters(BaseModel):
    commodity: str | None = None
    year: int | None = None
    flow_type: str | None = None  # import/export/both
    reporter: str | None = None  # iso3
    partner: str | None = None  # iso3
    min_value: int = 0
    limit: int = Field(default=200, ge=1, le=1000)


class SankeyNode(BaseModel):
    id: str
    name: str


class SankeyLink(BaseModel):
    source: str
    target: str
    value: int


class SankeyData(BaseModel):
    nodes: list[SankeyNode]
    links: list[SankeyLink]


class TimeSeriesPoint(BaseModel):
    year: int
    value_usd: int
    weight_kg: int | None
