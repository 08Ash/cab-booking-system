from fastapi import FastAPI
from database import create_db_and_tables
import models
from routes import rides
from routes import drivers
from fastapi import WebSocket, WebSocketDisconnect
from websocket_manager import manager
import stripe
from fastapi import Request
from redis_config import redis_client
from fastapi.middleware.cors import CORSMiddleware
from maps_config import gmaps

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(rides.router)
app.include_router(drivers.router)

@app.get("/")
def root():
    return {"message": "Cab Booking API Running"}

@app.websocket("/ws/rider/{rider_id}")
async def rider_socket(websocket: WebSocket, rider_id: int):
    await manager.connect_rider(rider_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_rider(rider_id)

@app.websocket("/ws/driver/{driver_id}")
async def driver_socket(websocket: WebSocket, driver_id: int):
    await manager.connect_driver(driver_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.send_to_rider(
                data.get("rider_id"),
                {
                    "type": "driver_location",
                    "lat": data.get("lat"),
                    "lng": data.get("lng"),
                    },
            )
    except WebSocketDisconnect:
        manager.disconnect_driver(driver_id)

