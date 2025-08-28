from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from lnbits.helpers import template_renderer

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
