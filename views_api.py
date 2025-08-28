from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pytest import Item

from lnbits.core.models import User, WalletTypeInfo
from lnbits.db import Filters, Page
from lnbits.decorators import (
    check_user_exists,
    optional_user_id,
    parse_filters,
    require_admin_key,
    require_invoice_key,
)
from lnbits.helpers import generate_filter_params_openapi

from .crud import (
    create_inventory,
    delete_inventory,
    get_inventories,
    get_inventory,
    get_inventory_items_paginated,
    get_public_inventory,
    update_inventory,
)
from .models import (
    CreateInventory,
    CreateItem,
    Inventory,
    Item,
    ItemFilters,
    PublicItem,
)

inventory_ext_api = APIRouter()
items_filters = parse_filters(ItemFilters)


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


## ITEMS
@inventory_ext_api.get(
    "/api/v1/items/{inventory_id}/paginated",
    openapi_extra=generate_filter_params_openapi(ItemFilters),
    response_model=Page,
)
async def api_get_items(
    inventory_id: str,
    user_id: str | None = Depends(optional_user_id),
    filters: Filters = Depends(items_filters),
) -> Page:
    inventory = (
        await get_inventory(user_id, inventory_id)
        if user_id
        else await get_public_inventory(inventory_id)
    )

    if not inventory:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Inventory not found.",
        )
    page = await get_inventory_items_paginated(inventory_id, filters)

    if user_id and inventory.dict().get("user_id", None) == user_id:
        return Page(data=page.data, total=page.total)
    return Page(
        data=[PublicItem(**item.dict()) for item in page.data], total=page.total
    )
