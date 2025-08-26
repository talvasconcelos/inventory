from http import HTTPStatus

import httpx
from fastapi import APIRouter, Depends, HTTPException
from lnbits.decorators import require_invoice_key

from .models import Example

inventory_ext_api = APIRouter()

# views_api.py is for you API endpoints that could be hit by another service


@inventory_ext_api.get(
    "/api/v1/test/{inventory_data}", description="Example API endpoint"
)
async def api_example(inventory_data: str) -> Example:
    if inventory_data != "00000000":
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid example data",
        )
    # Do some python things and return the data
    return Example(id="2", wallet=inventory_data)


@inventory_ext_api.get(
    "/api/v1/vetted",
    description="Get the vetted extension readme",
    dependencies=[Depends(require_invoice_key)],
)
async def api_get_vetted():
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://raw.githubusercontent.com/lnbits/lnbits-extensions/main/README.md"
        )
        return resp.text
