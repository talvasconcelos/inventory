from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field

from lnbits.db import FilterModel


class CreateInventory(BaseModel):
    name: str
    currency: str
    global_discount_percentage: float = 0.0
    default_tax_rate: float = 0.0
    is_tax_inclusive: bool = True


class PublicInventory(CreateInventory):
    id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Inventory(PublicInventory):
    user_id: str


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
    categories: list[Category] = Field(default_factory=list)
    name: str
    description: str | None = None
    image: str | None = None
    sku: str | None = None
    quantity_in_stock: int | None = None
    price: float
    discount_percentage: float | None = None
    tax_rate: float | None = None
    reorder_threshold: int | None = None
    unit_cost: float | None = None
    external_id: str | None = None
    omit_from_extension: list[str] = Field(default_factory=list)
    internal_note: str | None = None
    images: list[str] = Field(default_factory=list)
    manager_id: str | None = None


class PublicItem(CreateItem):
    id: str
    inventory_id: str
    categories: list[Category] = Field(default_factory=list)
    name: str
    description: str | None = None
    image: str | None = None
    sku: str | None = None
    quantity_in_stock: int | None = None
    price: float
    discount_percentage: float | None = None
    tax_rate: float | None = None
    omit_from_extension: list[str] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Item(PublicItem):
    external_id: str | None = None
    manager_id: str | None = None
    internal_note: str | None = None
    unit_cost: float | None = None
    reorder_threshold: int | None = None


class ItemFilters(FilterModel):
    __search_fields__ = ["name", "sku", "is_active", "internal_note", "manager_id"]

    __sort_fields__ = ["name", "created_at", "price", "quantity_in_stock"]

    name: str | None = None
    sku: str | None = None
    is_active: bool | None = None
    internal_note: str | None = None
    manager_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


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


# Inventory owner can assign managers to help manage items and stock
class CreateManager(BaseModel):
    inventory_id: str
    name: str | None = None


class Manager(CreateManager):
    id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
