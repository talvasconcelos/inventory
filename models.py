from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class CreateInventory(BaseModel):
    wallet: str
    name: str
    currency: str
    global_discount_percentage: float = 0.0
    default_tax_rate: float = 0.0
    is_tax_inclusive: bool = True


class Inventory(CreateInventory):
    id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CreateCategory(BaseModel):
    inventory_id: str
    name: str
    description: str | None = None


class Category(CreateCategory):
    id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CreateItem(BaseModel):
    inventory_id: str
    category_id: str | None = None
    name: str
    description: str | None = None
    sku: str
    quantity_in_stock: int
    price: float
    discount_percentage: float = 0.0
    tax_rate: float | None = None
    reorder_threshold: int | None = None
    unit_cost: float | None = None
    external_id: str | None = None


class Item(CreateItem):
    id: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class CreateOrder(BaseModel):
    inventory_id: str
    total_amount: float
    status: OrderStatus = OrderStatus.PENDING


class Order(CreateOrder):
    id: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CreateOrderItem(BaseModel):
    order_id: int
    item_id: str
    quantity: int
    base_price: float
    discount_amount: float = 0.0
    tax_amount: float = 0.0
    final_price: float


class OrderItem(BaseModel):
    id: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
