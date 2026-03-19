from pydantic import BaseModel


class TradeShift(BaseModel):
    reporter_iso3: str
    reporter_name: str
    partner_iso3: str
    partner_name: str
    commodity: str
    year_from: int
    year_to: int
    value_from: int
    value_to: int
    change_pct: float
    change_abs: int
    shift_type: str  # surge, collapse, new, abandoned


class ShiftSummary(BaseModel):
    commodity: str
    total_shifts: int
    surges: int
    collapses: int
    new_flows: int
    abandoned_flows: int
    top_shifts: list[TradeShift]
