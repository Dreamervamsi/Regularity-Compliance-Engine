import hashlib
from redis.asyncio import Redis, ConnectionPool

# redis is single threaded.
# redis has logical databases 0-15 so using db=0
# is best way rather than relying on other dbs.

redis_pool:ConnectionPool = ConnectionPool(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True # by setting it True, it will automatically 
                          #converts redis bytes to strings
)

async def get_redis():
    client = Redis(connection_pool = redis_pool)
    try:
        yield client
    except:
        raise Exception("Unable to connect to Redis")
    finally:
        await client.close()

def get_query_hash(query:str):
    return hashlib.sha256(query.encode('utf-8')).hexdigest()

async def search_query(query:str,redis:Redis = Depends(get_redis)):
    try:
        query_hash = get_query_hash(query)
        cache_data = await redis.get(query_hash)
        if cache_data:
            return cache_data
        return "Query missing!"

    except Exception as e:
        print(e)
        return None

async def store_query(query:str,value:str,redis:Redis = Depends(get_redis)):
    try:
        query_hash = get_query_hash(query)
        await redis.set(query_hash,value)
        return "Query stored successfully!"
    except Exception as e:
        print(e)
        return None

async def main():
    async for client in get_redis():
        await store_query("What is the capital of France?","Paris",client)
        res1 = await search_query("What is the capital of France?",client)
        res2 = await search_query("What is the capital of Germany?",client)

        print(res1)
        print(res2)

if __name__ == "__main__":
    asyncio.run(main())
