"""
Database Schemas

Define MongoDB collection schemas for the Smart Food Waste Management app.
Each Pydantic model corresponds to a collection; collection name is the lowercase
class name (e.g., WasteStat -> "wastestat").
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal
from datetime import datetime

# Core domain schemas

class Contributor(BaseModel):
    """
    Contributors collection schema
    Represents a restaurant, household, or community joining the network.
    """
    type: Literal["restaurant", "household", "community"] = Field(..., description="Type of contributor")
    name: str = Field(..., description="Name of the contributor")
    email: Optional[EmailStr] = Field(None, description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone")
    city: Optional[str] = Field(None, description="City or locality")
    notes: Optional[str] = Field(None, description="Additional information")

class PickupRequest(BaseModel):
    """
    Pickup requests from contributors for local collection scheduling.
    """
    contributor_id: str = Field(..., description="Contributor ObjectId as string")
    scheduled_for: datetime = Field(..., description="Scheduled pickup datetime (ISO)")
    estimated_kg: float = Field(..., ge=0, description="Estimated kilograms of waste")
    notes: Optional[str] = Field(None)

class WasteStat(BaseModel):
    """
    Aggregated statistics used for the impact section on the website.
    """
    tons_recycled: int = Field(..., ge=0)
    biogas_kg: int = Field(..., ge=0)
    landfill_reduction_pct: int = Field(..., ge=0, le=100)

# Retain example schemas for reference (not used by the app directly)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = Field(None, ge=0, le=120)
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    category: str
    in_stock: bool = True
