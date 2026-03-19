from pydantic import BaseModel


class CommodityOut(BaseModel):
    code: str
    name: str
    color: str
