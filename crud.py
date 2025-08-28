from datetime import datetime, timezone

from lnbits.db import Database
from lnbits.helpers import urlsafe_short_hash

from .models import CreateInventory, Inventory, PublicInventory

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
