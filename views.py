from http import HTTPStatus

from fastapi import APIRouter, Depends, Query, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse

from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from lnbits.helpers import template_renderer

from .crud import get_inventory, get_manager

inventory_ext_generic = APIRouter(tags=["inventory"])


def inventory_renderer():
    return template_renderer(["inventory/templates"])


@inventory_ext_generic.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    user: User = Depends(check_user_exists),
):
    return inventory_renderer().TemplateResponse(
        request, "inventory/index.html", {"user": user.json()}
    )


@inventory_ext_generic.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    inventory_id: str = Query(...),
    user: User = Depends(check_user_exists),
):
    if not inventory_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="inventory_id is required"
        )
    inventory = await get_inventory(user_id=user.id, inventory_id=inventory_id)
    if not inventory:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Inventory not found"
        )
    return inventory_renderer().TemplateResponse(
        request,
        "inventory/display.html",
        {"user": user.json(), "inventory": inventory.json()},
    )


@inventory_ext_generic.get("/manager", response_class=HTMLResponse)
async def manager(
    request: Request,
    manager_id: str,
):
    manager = await get_manager(manager_id)
    if not manager:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Manager not found"
        )

    return inventory_renderer().TemplateResponse(
        request, "inventory/manager.html", {"manager": manager.json()}
    )
