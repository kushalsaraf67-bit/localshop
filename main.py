from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime
import motor.motor_asyncio
from bson import ObjectId

app = FastAPI(title="CampusLocal NITP Backend")

# Enable CORS for frontend testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to MongoDB (Requires MongoDB running locally on 27017)
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
db = client.campuslocal

# --- Pydantic Models ---
class Location(BaseModel):
    lat: float
    lng: float

class UserProfile(BaseModel):
    name: str
    mobile: str
    address: str
    location: Location

class CartItem(BaseModel):
    id: int
    name: str
    price: int
    qty: int
    vendorName: str

class Order(BaseModel):
    order_id: str
    user: dict # Saves the user profile snapshot
    items: List[CartItem]
    total: int
    payment_method: str
    timestamp: datetime

# --- Endpoints ---

@app.post("/api/users")
async def register_user(user: UserProfile):
    """Saves user data + Mandatory GPS location to MongoDB"""
    new_user = user.dict()
    result = await db.users.insert_one(new_user)
    new_user["id"] = str(result.inserted_id)
    return new_user

@app.post("/api/orders")
async def create_order(order: Order):
    """Processes the mocked payment and saves the order to DB"""
    new_order = order.dict()
    # Mock UPI/Payment validation could go here
    result = await db.orders.insert_one(new_order)
    return {"status": "success", "order_id": order.order_id, "db_id": str(result.inserted_id)}
class MenuItem(BaseModel):
    id: int
    name: str
    price: int
    desc: str

class Vendor(BaseModel):
    id: int
    name: str
    category: str
    rating: float
    delivery_time: str
    image: str
    menu: List[MenuItem]

@app.get("/api/vendors")
async def get_vendors():
    """Fetch all vendors from MongoDB"""
    # Exclude MongoDB's internal _id field from the response
    vendors = await db.vendors.find({}, {"_id": 0}).to_list(length=100)
    return vendors

@app.post("/api/vendors")
async def register_vendor(vendor: Vendor):
    """Save a newly registered shop to MongoDB"""
    new_vendor = vendor.dict()
    await db.vendors.insert_one(new_vendor)
    return {"status": "success", "message": "Vendor added globally"}