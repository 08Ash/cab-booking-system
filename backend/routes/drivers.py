from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from database import get_session
from models import Driver, DriverCreate

router = APIRouter()


@router.post("/drivers/register")
def register_driver(data: DriverCreate, session: Session = Depends(get_session)):
    driver = Driver(
        user_id=data.user_id,
        vehicle_info=data.vehicle_info,
        current_lat=data.current_lat,
        current_lng=data.current_lng,
        status="active"
    )

    session.add(driver)
    session.commit()
    session.refresh(driver)

    return driver


@router.get("/drivers/active")
def get_active_drivers(session: Session = Depends(get_session)):
    statement = select(Driver).where(Driver.status == "active")
    drivers = session.exec(statement).all()

    return drivers