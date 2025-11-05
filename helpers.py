from lnbits.utils.crypto import random_secret_and_hash


def create_api_key() -> str:
    """Generate a new API key for external services."""
    key = random_secret_and_hash()
    return "sk_" + key[1]


async def verify_api_key(api_key: str) -> Optional[dict]:
    """
    Verify API key and return service info.
    Replace with your actual database lookup.
    """
    # TODO: Query your database
    # Example:
    # service = await db.query(ExternalService).filter(
    #     ExternalService.api_key == api_key,
    #     ExternalService.is_active == True
    # ).first()
    # if service:
    #     # Update last_used_at
    #     service.last_used_at = datetime.now(timezone.utc)
    #     await db.commit()
    #     return {"id": service.id, "name": service.service_name}
    # return None

    # Mock for demonstration
    valid_keys = {
        "sk_shopify_abc123": {"id": "shopify_001", "name": "Shopify Store"},
        "sk_pos_xyz789": {"id": "pos_002", "name": "POS System"},
    }
    return valid_keys.get(api_key)


async def check_idempotency(idempotency_key: str) -> bool:
    """
    Check if this request has already been processed.
    Returns True if already processed.
    """
    # TODO: Check your database
    # Example:
    # exists = await db.query(InventoryUpdateLog).filter(
    #     InventoryUpdateLog.idempotency_key == idempotency_key
    # ).first()
    # return exists is not None

    return False


async def get_current_stock(inventory_id: str, item_id: str) -> int:
    """Get current stock quantity for an item"""
    # TODO: Query your inventory database
    # Example:
    # item = await db.query(InventoryStock).filter(
    #     InventoryStock.inventory_id == inventory_id,
    #     InventoryStock.item_id == item_id
    # ).first()
    # return item.quantity if item else 0

    return 100  # Mock
