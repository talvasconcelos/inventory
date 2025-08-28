# tasks.py is for asynchronous when invoices get paid

# add your dependencies here

import asyncio

from loguru import logger

from lnbits.core.models import Payment
from lnbits.tasks import register_invoice_listener


async def wait_for_paid_invoices():
    invoice_queue = asyncio.Queue()
    register_invoice_listener(invoice_queue, "ext_inventory")

    while True:
        payment = await invoice_queue.get()
        await on_invoice_paid(payment)


async def on_invoice_paid(payment: Payment) -> None:
    # Will grab any payment with the tag "inventory"
    if payment.extra.get("tag") == "inventory":
        logger.info("inventory extension received payment")
        logger.debug(payment)
