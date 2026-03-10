from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    role: str
    rating_avg: float = 5.0

class Driver(SQLModel, table=True):
    user_id: int = Field(primary_key=True)
    vehicle_info: str
    current_lat: float
    current_lng: float
    status: str

class Ride(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    rider_id: int
    driver_id: Optional[int] = None
    pickup_lat: float
    pickup_lng: float
    drop_lat: float
    drop_lng: float
    status: str = "requested"
    fare_estimate: float
    fare_actual: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RideCreate(BaseModel):
    rider_id: int
    pickup_lat: float
    pickup_lng: float
    drop_lat: float
    drop_lng: float

class DriverLocationUpdate(BaseModel):
    driver_id: int
    lat: float
    lng: float

class DriverCreate(BaseModel):
    user_id: int
    vehicle_info: str
    current_lat: float
    current_lng: float

class Payment(SQLModel, table=True):
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    ride_id: int
    stripe_payment_intent: str
    amount: int
    currency: str = "inr"
    status: str = "pending"

class Review(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    ride_id: int
    rider_id: int
    driver_id: int
    rating: int
    comment: str | None = None

class ReviewCreate(SQLModel):
    rating: int
    comment: str | None = None