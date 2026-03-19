from sqlalchemy import Column, Float, Integer, String

from app.database import Base


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True)
    iso3 = Column(String(3), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    region = Column(String(50))
    latitude = Column(Float)
    longitude = Column(Float)

    def __repr__(self) -> str:
        return f"<Country(iso3={self.iso3!r}, name={self.name!r})>"
