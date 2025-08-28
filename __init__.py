import asyncio

from fastapi import APIRouter
from loguru import logger

from .crud import db
from .tasks import wait_for_paid_invoices
from .views import inventory_ext_generic
from .views_api import inventory_ext_api

inventory_ext: APIRouter = APIRouter(prefix="/inventory", tags=["inventory"])
inventory_ext.include_router(inventory_ext_generic)
inventory_ext.include_router(inventory_ext_api)

inventory_static_files = [
    {
        "path": "/inventory/static",
        "name": "inventory_static",
    }
]

scheduled_tasks: list[asyncio.Task] = []


def inventory_stop():
    for task in scheduled_tasks:
        try:
            task.cancel()
        except Exception as ex:
            logger.warning(ex)


def inventory_start():
    from lnbits.tasks import create_permanent_unique_task

    task = create_permanent_unique_task("ext_testing", wait_for_paid_invoices)
    scheduled_tasks.append(task)


__all__ = [
    "db",
    "inventory_ext",
    "inventory_start",
    "inventory_static_files",
    "inventory_stop",
]
