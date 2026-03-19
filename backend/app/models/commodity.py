from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Commodity(Base):
    __tablename__ = "commodities"

    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    color = Column(String(7))  # hex color

    hs_codes = relationship("HSCodeMapping", back_populates="commodity", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Commodity(code={self.code!r}, name={self.name!r})>"


class HSCodeMapping(Base):
    __tablename__ = "hs_code_mappings"

    id = Column(Integer, primary_key=True)
    commodity_id = Column(Integer, ForeignKey("commodities.id"), nullable=False)
    hs6 = Column(String(6), nullable=False, index=True)
    description = Column(String(200))

    commodity = relationship("Commodity", back_populates="hs_codes")

    def __repr__(self) -> str:
        return f"<HSCodeMapping(hs6={self.hs6!r}, description={self.description!r})>"
