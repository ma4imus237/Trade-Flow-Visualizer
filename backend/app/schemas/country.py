from pydantic import BaseModel


class CountryProfile(BaseModel):
    iso3: str
    name: str
    region: str | None
    total_exports: int
    total_imports: int
    top_export_partners: list[dict]
    top_import_partners: list[dict]
    top_commodities: list[dict]


class CountryPartner(BaseModel):
    iso3: str
    name: str
    value_usd: int
    flow_type: str
