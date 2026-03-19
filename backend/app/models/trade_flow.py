from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class TradeFlow(Base):
    __tablename__ = "trade_flows"

    id = Column(Integer, primary_key=True)
    reporter_id = Column(Integer, ForeignKey("countries.id"), nullable=False, index=True)
    partner_id = Column(Integer, ForeignKey("countries.id"), nullable=False, index=True)
    commodity_id = Column(Integer, ForeignKey("commodities.id"), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    flow_type = Column(String(10), nullable=False)  # 'import' or 'export'
    value_usd = Column(BigInteger, nullable=False)
    weight_kg = Column(BigInteger)
    is_estimated = Column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint(
            "reporter_id",
            "partner_id",
            "commodity_id",
            "year",
            "flow_type",
            name="uq_trade_flow",
        ),
        Index("idx_flow_commodity_year", "commodity_id", "year"),
    )

    reporter = relationship("Country", foreign_keys=[reporter_id])
    partner = relationship("Country", foreign_keys=[partner_id])
    commodity = relationship("Commodity")

    def __repr__(self) -> str:
        return (
            f"<TradeFlow(reporter_id={self.reporter_id}, partner_id={self.partner_id}, "
            f"commodity_id={self.commodity_id}, year={self.year}, "
            f"flow_type={self.flow_type!r}, value_usd={self.value_usd})>"
        )
