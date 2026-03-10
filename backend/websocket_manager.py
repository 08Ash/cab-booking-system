from typing import Dict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_riders: Dict[int, WebSocket] = {}
        self.active_drivers: Dict[int, WebSocket] = {}
        
    async def connect_rider(self, rider_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_riders[rider_id] = websocket
        
    async def connect_driver(self, driver_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_drivers[driver_id] = websocket

    def disconnect_rider(self, rider_id: int):
        self.active_riders.pop(rider_id, None)

    def disconnect_driver(self, driver_id: int):
        self.active_drivers.pop(driver_id, None)

    async def send_to_rider(self, rider_id: int, message: dict):
        if rider_id in self.active_riders:
            await self.active_riders[rider_id].send_json(message)
            
    async def send_to_driver(self, driver_id: int, message: dict):
        if driver_id in self.active_drivers:
            await self.active_drivers[driver_id].send_json(message)

manager = ConnectionManager()