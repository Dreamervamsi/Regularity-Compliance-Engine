import config
import asyncio
import hashlib
from fastapi import Depends
from redis.commands.search.field import TextField, VectorField
from redis.commands.search.query import Query
from redis.asyncio import Redis, ConnectionPool
import numpy as np

# redis is single threaded.
# redis has logical databases 0-15 so using db=0
# is best way rather than relying on other dbs.

redis_pool:ConnectionPool = ConnectionPool(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    db=config.REDIS_DB,
    decode_responses=False
)

async def get_redis():
    client = Redis(connection_pool = redis_pool)
    try:
        yield client
    except:
        raise Exception("Unable to connect to Redis")
    finally:
        await client.close()

""" Searching for exact query (1st phase of dual redis search) """

def get_query_hash(query:str):
    return hashlib.sha256(query.encode('utf-8')).hexdigest()

async def search_exact_query(query:str,redis:Redis = Depends(get_redis)):
    try:
        query_hash = get_query_hash(query)
        cache_data = await redis.get(query_hash)
        if cache_data:
            return cache_data.decode('utf-8') if isinstance(cache_data, bytes) else cache_data
        return None

    except Exception as e:
        print(e)
        return None

async def store_exact_query(query:str,value:str,redis:Redis = Depends(get_redis)):
    try:
        query_hash = get_query_hash(query)
        await redis.set(query_hash,value)
        return "Query stored successfully!"
    except Exception as e:
        print(e)
        return None

""" Searching for similar query (2nd phase of dual redis search) """

async def _init_index(redis:Redis = Depends(get_redis)):
    try:
        schema = (
            TextField("query"),
            TextField("response"),
            VectorField(
                "embedding",
                "HNSW",
                {
                    "TYPE":"FLOAT32",
                    "DIM":config.SEMANTIC_CACHE_DIM,
                    "DISTANCE_METRIC":"COSINE"
                }
            )
        )
        await redis.ft(config.REDIS_INDEX).create_index(fields=schema)
        print("Index created!")
    except:
        raise Exception("Cannot create index")

async def store_semantic_query(query:str,query_embedding, response: str, redis: Redis=Depends(get_redis)):
    try:
        query_id = get_query_hash(query)
        key = f"{config.REDIS_PREFIX}{query_id}"
        await redis.hset(key, mapping={
            "query":query,
            "response":response
        })
        query_embedding_bytes = np.array(query_embedding, dtype=np.float32).tobytes()

        await redis.hset(key,"embedding",query_embedding_bytes)
        await redis.expire(key,time=60*60*24)
        return "Query stored successfully!"
    except Exception as e:
        print(e)
        return None

async def search_semantic_query(query_embeddings, redis: Redis=Depends(get_redis), threshold: float = 0.25):
    try:
        query_embedding_bytes = np.array(query_embeddings, dtype=np.float32).tobytes()

        search_query = (
            Query("*=>[KNN 1 @embedding $query_vector AS vector_score]")
            .return_fields("query", "response", "embedding")
            .sort_by("vector_score")
            .dialect(2)
        )
        result = await redis.ft(config.REDIS_INDEX).search(
            search_query,
            query_params={"query_vector": query_embeddings}
        )

        if result.docs:
            matched_doc = result.docs[0]
            # In COSINE distance, a smaller score means the vectors are closer together (0.0 = identical)
            distance_score = float(matched_doc.vector_score)
            if distance_score <= threshold:
                return {
                    "query": matched_doc.query.decode('utf-8') if isinstance(matched_doc.query, bytes) else matched_doc.query,
                    "response": matched_doc.response.decode('utf-8') if isinstance(matched_doc.response, bytes) else matched_doc.response,
                    "score": distance_score
                }
        return {"match_found": False, "message": "No semantically similar query found inside threshold."}

    except Exception as e:
        print(e)
        return None
 