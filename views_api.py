from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from lnbits.core.models import User, WalletTypeInfo
from lnbits.decorators import check_user_exists, require_admin_key, require_invoice_key

from .crud import (
    create_inventory,
    delete_inventory,
    get_inventories,
    get_inventory,
    update_inventory,
)
from .models import CreateInventory, Inventory

inventory_ext_api = APIRouter()


@inventory_ext_api.get("/api/v1/inventories", status_code=HTTPStatus.OK)
async def api_get_inventories(
    user: User = Depends(check_user_exists),
) -> list[Inventory]:
    return await get_inventories(user.id)


@inventory_ext_api.post("/api/v1/inventories", status_code=HTTPStatus.CREATED)
async def api_create_inventory(
    inventory: CreateInventory,
    user: User = Depends(check_user_exists),
) -> Inventory:
    return await create_inventory(user.id, inventory)


@inventory_ext_api.put("/api/v1/inventories/{inventory_id}", status_code=HTTPStatus.OK)
async def api_update_inventory(
    inventory_id: str,
    data: CreateInventory,
    user: User = Depends(check_user_exists),
) -> Inventory:
    inventory = await get_inventory(user.id, inventory_id)
    if not inventory or inventory.user_id != user.id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Cannot update inventory.",
        )
    for field, value in data.dict().items():
        setattr(inventory, field, value)
    return await update_inventory(inventory)


@inventory_ext_api.delete(
    "/api/v1/inventories/{inventory_id}", status_code=HTTPStatus.NO_CONTENT
)
async def api_delete_inventory(
    inventory_id: str,
    user: User = Depends(check_user_exists),
) -> None:
    inventory = await get_inventory(user.id, inventory_id)
    if not inventory or inventory.user_id != user.id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Cannot delete inventory.",
        )
    await delete_inventory(user.id, inventory_id)
