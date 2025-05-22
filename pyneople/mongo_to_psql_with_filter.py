from motor.motor_asyncio import AsyncIOMotorClient
from typing import Callable
from pyneople.config.config import Settings
from pyneople.metadata.metadata_generated import PSQL_TABLE_COLUMNS_MAP
import asyncpg
import asyncio

async def _mongo_to_psql_with_filter(
    filter : dict,
    psql_table_name : str,
    batch_size : int = 5000,
    preprocess : Callable = lambda x: x
    ):
    mongo_client = AsyncIOMotorClient(Settings.MONGO_URL)
    mongo_db = mongo_client[Settings.MONGO_DB_NAME]
    mongo_collection = mongo_db[Settings.MONGO_COLLECTION_NAME]

    psql_conn = await asyncpg.connect(
        user=Settings.POSTGRES_USER,
        password=Settings.POSTGRES_PASSWORD,
        database=Settings.POSTGRES_DB,
        host=Settings.POSTGRES_HOST
    )
    try:
        async with await mongo_client.start_session() as session:
            mongo_cursor = mongo_collection.find(filter, no_cursor_timeout=True, batch_size=batch_size, session=session)
            batch = []
            
            async for doc in mongo_cursor:
                doc = doc.get('data')
                doc = preprocess(doc, PSQL_TABLE_COLUMNS_MAP[psql_table_name])
                
                if isinstance(doc, list):
                    batch.extend(doc)
                else:
                    batch.append(doc)            
                
                if len(batch) >= batch_size:
                    await psql_conn.copy_records_to_table(
                        psql_table_name,
                        records=[tuple(row.values()) for row in batch],
                        columns=batch[0].keys()
                    )
                    batch = []
            if batch:
                await psql_conn.copy_records_to_table(
                        psql_table_name,
                        records=[tuple(row.values()) for row in batch],
                        columns=batch[0].keys()
                    )
    finally:
        await psql_conn.close()
        mongo_client.close()            

def mongo_to_psql_with_filter(
    filter : dict,
    psql_table_name : str,
    batch_size : int = 5000,
    preprocess : Callable = lambda x: x
):
    asyncio.run(_mongo_to_psql_with_filter(
        filter=filter,
        psql_table_name=psql_table_name,
        batch_size=batch_size,
        preprocess=preprocess
    ))