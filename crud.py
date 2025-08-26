# crud.py is for communication with your extensions database

# add your dependencies here
# from .models import createExample, Example
from lnbits.db import Database

db = Database("ext_inventory")

# add your fnctions here

# async def create_a_record(data: Example) -> createExample:
#     inventory_id = urlsafe_short_hash()
#     example = Example(id=inventory_id, **data.dict())
#     await db.insert("example.example", example)
#     return example


# async def get_a_record(inventory_id: str) -> Optional[Example]:
#     return await db.fetchone(
#         "SELECT * FROM example.example WHERE id = :id", {"id": inventory_id}, Example
#     )
