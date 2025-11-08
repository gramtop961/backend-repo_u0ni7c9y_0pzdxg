"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Add your own schemas here:
# --------------------------------------------------

class Order(BaseModel):
    """
    Orders collection schema
    Collection name: "order"
    """
    product_name: str = Field(..., description="Selected product or bundle name")
    quantity: int = Field(1, ge=1, description="Number of units")
    total_price: float = Field(..., ge=0, description="Total order price in EUR")

    full_name: str = Field(..., description="Customer full name")
    email: EmailStr = Field(..., description="Customer email")
    phone: str = Field(..., description="Customer phone or WhatsApp")

    address_line: str = Field(..., description="Street and number")
    city: str = Field(..., description="City")
    province: Optional[str] = Field(None, description="Province/Region")
    postal_code: str = Field(..., description="ZIP/Postal code")
    notes: Optional[str] = Field(None, description="Delivery notes or additional info")

    newsletter_opt_in: bool = Field(False, description="Marketing consent")
