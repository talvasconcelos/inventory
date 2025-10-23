from lnbits.db import Database


async def m001_initial(db: Database):
    """
    -- Table: inventories
    -- Purpose: Stores user-created inventories, each representing a collection of items
       (e.g., a store or warehouse). Supports global discount and tax settings for all
       items in the inventory.
    """
    await db.execute(
        f"""
       CREATE TABLE inventory.inventories (
           id TEXT PRIMARY KEY,
           user_id TEXT NOT NULL,
           name TEXT NOT NULL,
           currency TEXT NOT NULL,
           global_discount_percentage REAL DEFAULT 0.00,
           default_tax_rate REAL DEFAULT 0.00,
           is_tax_inclusive BOOLEAN DEFAULT TRUE,
           created_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now},
           updated_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now}
       );
   """
    )

    """
    -- Table: categories
    -- Purpose: Stores categories for organizing items within an inventory
       (e.g., "Clothing", "Electronics").
       Facilitates filtering in POS, webshop, or reports.
    """
    await db.execute(
        f"""
       CREATE TABLE inventory.categories (
           id TEXT PRIMARY KEY,
           inventory_id TEXT NOT NULL,
           name TEXT,
           description TEXT,
           created_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now},
           updated_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now}
       );
   """
    )

    """
    -- Table: items
    -- Purpose: Stores individual items within an inventory, including stock, pricing,
       discounts, and optional category assignment. Core table for inventory management
       and API callbacks.
    """

    await db.execute(
        f"""
       CREATE TABLE inventory.items (
           id TEXT PRIMARY KEY,
           inventory_id TEXT NOT NULL,
           categories TEXT,
           name TEXT NOT NULL,
           description TEXT,
           images TEXT,
           sku TEXT,
           quantity_in_stock INTEGER CHECK (quantity_in_stock IS NULL OR quantity_in_stock >= 0),
           price REAL NOT NULL,
           discount_percentage REAL DEFAULT 0.00,
           tax_rate REAL,
           reorder_threshold INTEGER,
           unit_cost REAL,
           external_id TEXT,
           is_active BOOLEAN DEFAULT TRUE,
           omit_from_extension TEXT,
           internal_note TEXT,
           manager_id TEXT,
           created_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now},
           updated_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now}
       );
   """
    )

    """
    -- Table: orders
    -- Purpose: Stores high-level order information for completed checkouts.
        Links to an inventory and records total amount for auditing.
    """
    await db.execute(
        f"""
       CREATE TABLE inventory.orders (
           id {db.serial_primary_key},
           inventory_id TEXT NOT NULL,
           total_amount REAL NOT NULL,
           status TEXT DEFAULT 'pending',
           created_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now},
           updated_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now}
       );
   """
    )

    """
    -- Table: order_items
    -- Purpose: Stores details of items purchased in an order, including pricing,
    discounts, and taxes at checkout.
    """
    await db.execute(
        f"""
       CREATE TABLE inventory.order_items (
           id {db.serial_primary_key},
           order_id INTEGER NOT NULL,
           item_id TEXT NOT NULL,
           quantity INTEGER NOT NULL CHECK (quantity > 0),
           base_price REAL NOT NULL,
           discount_amount REAL DEFAULT 0.00,
           tax_amount REAL DEFAULT 0.00,
           final_price REAL NOT NULL,
           created_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now}
       );
   """
    )

    """
    -- Table: Managers
    -- Purpose: Stores managers assigned to specific inventories for better item and stock management.
    """
    await db.execute(
        f"""
       CREATE TABLE inventory.managers (
           id TEXT PRIMARY KEY,
           inventory_id TEXT NOT NULL,
           name TEXT,
           created_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now},
           updated_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now}
       );
   """
    )
