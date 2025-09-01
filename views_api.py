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
    create_category,
    create_inventory,
    create_item,
    delete_inventory,
    get_inventories,
    get_inventory,
    get_inventory_categories,
    get_inventory_items_paginated,
    get_item,
    get_public_inventory,
    is_category_unique,
    update_inventory,
    update_item,
)
from .models import (
    Category,
    CreateCategory,
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
    print(f"API: {filters}")
    page = await get_inventory_items_paginated(inventory_id, filters)

    if user_id and inventory.dict().get("user_id", None) == user_id:
        return Page(data=page.data, total=page.total)
    return Page(
        data=[PublicItem(**item.dict()) for item in page.data], total=page.total
    )


@inventory_ext_api.post("/api/v1/items", status_code=HTTPStatus.CREATED)
async def api_create_item(
    item: CreateItem,
    user: User = Depends(check_user_exists),
) -> Item | None:
    inventory = await get_inventory(user.id, item.inventory_id)
    if not inventory or inventory.user_id != user.id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Cannot create item.",
        )
    if item.inventory_id != inventory.id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Item does not belong to the specified inventory.",
        )
    return await create_item(user.id, item)


@inventory_ext_api.put("/api/v1/items/{item_id}", status_code=HTTPStatus.OK)
async def api_update_item(
    item_id: str,
    item: CreateItem,
    user: User = Depends(check_user_exists),
) -> Item | None:
    inventory = await get_inventory(user.id, item.inventory_id)
    if not inventory or inventory.user_id != user.id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Cannot update item.",
        )
    _item = await get_item(item_id)
    if not _item or _item.inventory_id != inventory.id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Item not found.",
        )
    for field, value in item.dict().items():
        setattr(_item, field, value)
    return await update_item(_item)


## CATEGORIES
@inventory_ext_api.get("/api/v1/categories/{inventory_id}", status_code=HTTPStatus.OK)
async def api_get_categories(
    inventory_id: str,
) -> list[Category]:
    inventory = await get_public_inventory(inventory_id)
    if not inventory:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Inventory not found.",
        )

    return await get_inventory_categories(inventory_id)


@inventory_ext_api.post("/api/v1/categories", status_code=HTTPStatus.CREATED)
async def api_create_category(
    category: CreateCategory,
    user: User = Depends(check_user_exists),
) -> Category:
    inventory = await get_inventory(user.id, category.inventory_id)
    if not inventory or inventory.user_id != user.id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Cannot create category.",
        )
    if not await is_category_unique(category.name, category.inventory_id):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Category name must be unique.",
        )

    return await create_category(category)
