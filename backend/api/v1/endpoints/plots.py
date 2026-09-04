"""
Plot Management REST API Endpoints
Allows creating and retrieving agricultural plot profiles.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.db_models import DBPlot
from backend.schemas.contracts import PlotProfile, Location
from backend.services.fallback_fixture import get_tukaram_plot_profile

router = APIRouter(prefix="/plots", tags=["Plot Management"])

@router.post("", response_model=PlotProfile, status_code=status.HTTP_201_CREATED)
def create_plot(plot: PlotProfile, db: Session = Depends(get_db)):
    """Creates a new agricultural plot profile in the SQLite database."""
    existing = db.query(DBPlot).filter(DBPlot.plot_id == plot.plot_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plot with ID '{plot.plot_id}' already exists."
        )

    db_plot = DBPlot(
        plot_id=plot.plot_id,
        farmer_name=plot.farmer_name,
        district=plot.location.district,
        latitude=plot.location.latitude,
        longitude=plot.location.longitude,
        crop_type=plot.crop_type,
        sowing_date=plot.sowing_date,
        soil_type=plot.soil_type,
        plot_area_ha=plot.plot_area_ha
    )
    db.add(db_plot)
    db.commit()
    db.refresh(db_plot)

    return PlotProfile(
        plot_id=db_plot.plot_id,
        farmer_name=db_plot.farmer_name,
        location=Location(
            district=db_plot.district,
            latitude=db_plot.latitude,
            longitude=db_plot.longitude
        ),
        crop_type=db_plot.crop_type,
        sowing_date=db_plot.sowing_date,
        soil_type=db_plot.soil_type,
        plot_area_ha=db_plot.plot_area_ha
    )

@router.get("/{plot_id}", response_model=PlotProfile)
def get_plot(plot_id: str, db: Session = Depends(get_db)):
    """Retrieves plot profile by ID. Auto-seeds Tukaram benchmark plot if requested and absent."""
    db_plot = db.query(DBPlot).filter(DBPlot.plot_id == plot_id).first()

    if not db_plot:
        if plot_id == "tukaram_beed_01":
            tukaram = get_tukaram_plot_profile()
            db_plot = DBPlot(
                plot_id=tukaram.plot_id,
                farmer_name=tukaram.farmer_name,
                district=tukaram.location.district,
                latitude=tukaram.location.latitude,
                longitude=tukaram.location.longitude,
                crop_type=tukaram.crop_type,
                sowing_date=tukaram.sowing_date,
                soil_type=tukaram.soil_type,
                plot_area_ha=tukaram.plot_area_ha
            )
            db.add(db_plot)
            db.commit()
            db.refresh(db_plot)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plot '{plot_id}' not found."
            )

    return PlotProfile(
        plot_id=db_plot.plot_id,
        farmer_name=db_plot.farmer_name,
        location=Location(
            district=db_plot.district,
            latitude=db_plot.latitude,
            longitude=db_plot.longitude
        ),
        crop_type=db_plot.crop_type,
        sowing_date=db_plot.sowing_date,
        soil_type=db_plot.soil_type,
        plot_area_ha=db_plot.plot_area_ha
    )

@router.get("", response_model=List[PlotProfile])
def list_plots(db: Session = Depends(get_db)):
    """Lists all registered plot profiles."""
    plots = db.query(DBPlot).all()
    return [
        PlotProfile(
            plot_id=p.plot_id,
            farmer_name=p.farmer_name,
            location=Location(district=p.district, latitude=p.latitude, longitude=p.longitude),
            crop_type=p.crop_type,
            sowing_date=p.sowing_date,
            soil_type=p.soil_type,
            plot_area_ha=p.plot_area_ha
        )
        for p in plots
    ]
