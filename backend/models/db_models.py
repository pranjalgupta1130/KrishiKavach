import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Text, Boolean
from backend.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class DBPlot(Base):
    __tablename__ = "plots"

    plot_id = Column(String, primary_key=True, index=True)
    farmer_name = Column(String, nullable=False, default="Tukaram")
    district = Column(String, nullable=False, default="Beed")
    latitude = Column(Float, nullable=False, default=18.99)
    longitude = Column(Float, nullable=False, default=75.76)
    crop_type = Column(String, nullable=False, default="bt_cotton")
    sowing_date = Column(String, nullable=False, default="2026-06-25")
    soil_type = Column(String, nullable=False, default="medium_black_vertisol")
    plot_area_ha = Column(Float, nullable=False, default=1.5)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class DBDecisionRecord(Base):
    __tablename__ = "decision_records"

    decision_id = Column(String, primary_key=True, index=True, default=generate_uuid)
    plot_id = Column(String, index=True, nullable=False)
    date = Column(String, nullable=False, index=True)
    primary_action = Column(Text, nullable=False)
    critical_prohibition = Column(Text, nullable=False)
    scientific_rationale = Column(Text, nullable=False)
    confidence_indicator = Column(String, nullable=False)
    explainability_id = Column(String, nullable=False)
    explainability_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class DBWeatherCache(Base):
    __tablename__ = "weather_cache"

    id = Column(String, primary_key=True, default=generate_uuid)
    plot_id = Column(String, index=True, nullable=False)
    date = Column(String, index=True, nullable=False)
    payload_json = Column(Text, nullable=False)
    fetched_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
