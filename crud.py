from datetime import datetime, timezone

from lnbits.db import Database, Filters, Page
from lnbits.helpers import urlsafe_short_hash

from .models import (
    Category,
    CreateCategory,
    CreateInventory,
    CreateItem,
    CreateManager,
    Inventory,
    Item,
    ItemFilters,
    Manager,
    PublicInventory,
    PublicItem,
)

db = Database("ext_inventory")


async def get_inventories(user_id: str) -> list[Inventory]:
    return await db.fetchall(
        """
        SELECT * FROM inventory.inventories
        WHERE user_id = :user_id
        """,
        {"user_id": user_id},
        model=Inventory,
    )


async def get_inventory(user_id: str, inventory_id: str) -> Inventory | None:
    return await db.fetchone(
        """
            SELECT * FROM inventory.inventories
            WHERE id = :inventory_id AND user_id = :user_id
        """,
        {"inventory_id": inventory_id, "user_id": user_id},
        Inventory,
    )


async def get_public_inventory(inventory_id: str) -> PublicInventory | None:
    return await db.fetchone(
        """
            SELECT * FROM inventory.inventories
            WHERE id = :inventory_id
        """,
        {"inventory_id": inventory_id},
        PublicInventory,
    )


async def create_inventory(user_id: str, data: CreateInventory) -> Inventory:
    inventory_id = urlsafe_short_hash()
    inventory = Inventory(
        id=inventory_id,
        user_id=user_id,
        **data.dict(),
    )
    await db.insert("inventory.inventories", inventory)
    return inventory


async def update_inventory(data: Inventory) -> Inventory:
    data.updated_at = datetime.now(timezone.utc)
    await db.update("inventory.inventories", data)
    return data


async def delete_inventory(user_id: str, inventory_id: str) -> None:
    await db.execute(
        """
        DELETE FROM inventory.inventories
        WHERE id = :inventory_id AND user_id = :user_id
        """,
        {"inventory_id": inventory_id, "user_id": user_id},
    )


async def get_inventory_categories(inventory_id: str) -> list[Category]:
    return await db.fetchall(
        """
        SELECT * FROM inventory.categories
        WHERE inventory_id = :inventory_id
        """,
        {"inventory_id": inventory_id},
        model=Category,
    )


async def create_category(data: CreateCategory) -> Category:
    category_id = urlsafe_short_hash()
    category = Category(
        id=category_id,
        **data.dict(),
    )
    await db.insert("inventory.categories", category)
    return category


async def is_category_unique(name: str, inventory_id: str) -> bool:
    existing_category = await db.fetchone(
        """
        SELECT * FROM inventory.categories
        WHERE name = :name AND inventory_id = :inventory_id
        """,
        {"name": name, "inventory_id": inventory_id},
        model=Category,
    )
    return existing_category is None


async def get_inventory_items_paginated(
    inventory_id: str, filters: Filters[ItemFilters] | None = None
) -> Page[Item]:
    where = ["inventory_id = :inventory_id"]
    params = {"inventory_id": inventory_id}

    print("Fetching items with filters:", filters)

    return await db.fetch_page(
        "SELECT * FROM inventory.items",
        where=where,
        values=params,
        filters=filters,
        model=Item,
    )


async def get_item(item_id: str) -> Item | None:
    return await db.fetchone(
        """
        SELECT * FROM inventory.items
        WHERE id = :item_id
        """,
        {"item_id": item_id},
        model=Item,
    )


async def create_item(data: CreateItem) -> Item:
    item_id = urlsafe_short_hash()
    item = Item(
        id=item_id,
        **data.dict(),
    )
    if item.manager_id is not None and item.manager_id != "":
        item.is_active = False  # Items created by managers are inactive by default
    await db.insert("inventory.items", item)
    return item


async def update_item(data: Item) -> Item:
    data.updated_at = datetime.now(timezone.utc)
    await db.update("inventory.items", data)
    return data


async def delete_item(item_id: str) -> None:
    await db.execute(
        """
        DELETE FROM inventory.items
        WHERE id = :item_id
        """,
        {"item_id": item_id},
    )


async def create_manager(data: CreateManager) -> Manager:
    manager_id = urlsafe_short_hash()
    manager = Manager(
        id=manager_id,
        **data.dict(),
    )
    await db.insert("inventory.managers", manager)
    return manager


async def update_manager(data: Manager) -> Manager:
    data.updated_at = datetime.now(timezone.utc)
    await db.update("inventory.managers", data)
    return data


async def get_managers(inventory_id: str) -> list[Manager]:
    return await db.fetchall(
        """
        SELECT * FROM inventory.managers
        WHERE inventory_id = :inventory_id
        """,
        {"inventory_id": inventory_id},
        model=Manager,
    )


async def get_manager(manager_id: str) -> Manager | None:
    return await db.fetchone(
        """
        SELECT * FROM inventory.managers
        WHERE id = :manager_id
        """,
        {"manager_id": manager_id},
        model=Manager,
    )


async def delete_manager(manager_id: str) -> None:
    await db.execute(
        """
        DELETE FROM inventory.managers
        WHERE id = :manager_id
        """,
        {"manager_id": manager_id},
    )
