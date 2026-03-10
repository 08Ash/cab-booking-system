from fastapi import APIRouter, Depends, Request, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import Ride, RideCreate, Driver, Payment, Review, ReviewCreate
from services.matching import calculate_distance
from websocket_manager import manager
from stripe_config import stripe
from config import endpoint_secret
from redis_config import redis_client
from services.fare_service import calculate_fare
from pydantic import BaseModel
from fastapi.responses import FileResponse

router = APIRouter()


class DriverLocationUpdate(BaseModel):
    driver_id: int
    lat: float
    lng: float


ALLOWED_TRANSITIONS = {
    "searching": ["assigned"],
    "assigned": ["accepted"],
    "accepted": ["started"],
    "started": ["completed"],
    "completed": []
}


@router.post("/rides/request")
def request_ride(data: RideCreate, session: Session = Depends(get_session)):

    fare = calculate_fare(
        data.pickup_lat,
        data.pickup_lng,
        data.drop_lat,
        data.drop_lng
    )

    ride = Ride(
        rider_id=data.rider_id,
        pickup_lat=data.pickup_lat,
        pickup_lng=data.pickup_lng,
        drop_lat=data.drop_lat,
        drop_lng=data.drop_lng,
        fare_estimate=fare,
        status="searching"
    )

    session.add(ride)
    session.commit()
    session.refresh(ride)

    nearby_drivers = redis_client.georadius(
        "drivers",
        data.pickup_lng,
        data.pickup_lat,
        50,
        unit="km",
        withdist=True,
        sort="ASC"
    )

    assigned_driver = None

    for driver in nearby_drivers:
        driver_id = int(driver[0])

        active_ride_check = select(Ride).where(
            Ride.driver_id == driver_id,
            Ride.status.in_(["accepted", "started"])
        )

        busy_ride = session.exec(active_ride_check).first()

        if not busy_ride:
            assigned_driver = driver_id
            break

    if assigned_driver:
        ride.driver_id = assigned_driver
        ride.status = "assigned"
    else:
        ride.status = "no_driver"

    session.commit()
    session.refresh(ride)

    return ride


@router.post("/rides/{ride_id}/update-status")
def update_ride_status(ride_id: int, status: str, session: Session = Depends(get_session)):

    ride = session.get(Ride, ride_id)

    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    current_status = ride.status

    if status not in ALLOWED_TRANSITIONS.get(current_status, []):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition from {current_status} to {status}"
        )

    ride.status = status
    session.commit()
    session.refresh(ride)

    return ride


@router.post("/rides/{ride_id}/accept")
async def accept_ride(ride_id: int, driver_id: int, session: Session = Depends(get_session)):

    ride = session.get(Ride, ride_id)

    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    if ride.status != "assigned":
        raise HTTPException(status_code=400, detail="Ride not in assigned state")

    if ride.driver_id != driver_id:
        raise HTTPException(status_code=403, detail="Driver not assigned to this ride")

    statement = select(Ride).where(
        Ride.driver_id == driver_id,
        Ride.status.in_(["accepted", "started"])
    )

    active_ride = session.exec(statement).first()

    if active_ride:
        raise HTTPException(status_code=400, detail="Driver already on active ride")

    ride.status = "accepted"
    session.commit()
    session.refresh(ride)

    await manager.send_to_rider(
        ride.rider_id,
        {
            "type": "ride_status_update",
            "ride_id": ride.id,
            "status": "accepted"
        }
    )

    return ride


@router.post("/drivers/location")
def update_driver_location(data: DriverLocationUpdate):

    redis_client.geoadd(
        "drivers",
        (data.lng, data.lat, data.driver_id)
    )

    redis_client.setex(
        f"driver_active:{data.driver_id}",
        30,
        "online"
    )

    return {"message": "Driver location updated"}


@router.post("/rides/{ride_id}/start")
def start_ride(ride_id: int, session: Session = Depends(get_session)):

    ride = session.get(Ride, ride_id)

    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    ride.status = "started"

    session.commit()
    session.refresh(ride)

    return ride


@router.post("/rides/{ride_id}/complete")
def complete_ride(ride_id: int, session: Session = Depends(get_session)):

    ride = session.get(Ride, ride_id)

    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    ride.status = "completed"
    ride.fare_actual = ride.fare_estimate

    session.add(ride)
    session.commit()
    session.refresh(ride)

    return {
        "message": "Ride completed. Please submit review.",
        "ride_id": ride.id,
        "driver_id": ride.driver_id
    }

@router.post("/rides/{ride_id}/create-payment")
async def create_payment(ride_id: int, session: Session = Depends(get_session)):

    ride = session.get(Ride, ride_id)

    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    if ride.status != "completed":
        raise HTTPException(status_code=400, detail="Ride must be completed first")

    payment_intent = stripe.PaymentIntent.create(
        amount=int(ride.fare_estimate * 100),
        currency="inr",
        metadata={"ride_id": ride.id}
    )

    payment = Payment(
        ride_id=ride.id,
        stripe_payment_intent=payment_intent.id,
        amount=payment_intent.amount,
        currency=payment_intent.currency
    )

    session.add(payment)
    session.commit()

    return {"client_secret": payment_intent.client_secret}

@router.post("/rides/{ride_id}/review")
def add_review(ride_id: int, data: ReviewCreate, session: Session = Depends(get_session)):

    ride = session.get(Ride, ride_id)

    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    review = Review(
        ride_id=ride.id,
        rider_id=ride.rider_id,
        driver_id=ride.driver_id,
        rating=data.rating,
        comment=data.comment
    )

    session.add(review)
    session.commit()
    session.refresh(review)

    return review

@router.get("/rides/{ride_id}/receipt")
def generate_receipt(ride_id: int, session: Session = Depends(get_session)):

    ride = session.get(Ride, ride_id)

    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    return {
        "ride_id": ride.id,
        "rider_id": ride.rider_id,
        "driver_id": ride.driver_id,
        "fare": ride.fare_estimate,
        "status": ride.status
    }

@router.get("/drivers/{driver_id}/reviews")
def get_driver_reviews(driver_id: int, session: Session = Depends(get_session)):

    statement = select(Review).where(Review.driver_id == driver_id)
    reviews = session.exec(statement).all()

    return reviews


@router.get("/rides/{ride_id}/receipt")
def generate_receipt(ride_id: int, session: Session = Depends(get_session)):

    ride = session.get(Ride, ride_id)

    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    html = f"""
    <h1>Ride Receipt</h1>
    <p>Ride ID: {ride.id}</p>
    <p>Rider: {ride.rider_id}</p>
    <p>Driver: {ride.driver_id}</p>
    <p>Fare: {ride.fare_estimate}</p>
    """

    HTML(string=html).write_pdf("receipt.pdf")

    return FileResponse("receipt.pdf")


@router.get("/admin/rides")
def get_all_rides(session: Session = Depends(get_session)):

    statement = select(Ride)
    rides = session.exec(statement).all()

    return rides


@router.get("/admin/drivers")
def get_all_drivers(session: Session = Depends(get_session)):

    statement = select(Driver)
    drivers = session.exec(statement).all()

    return drivers


@router.get("/admin/payments")
def get_all_payments(session: Session = Depends(get_session)):

    statement = select(Payment)
    payments = session.exec(statement).all()

    return payments