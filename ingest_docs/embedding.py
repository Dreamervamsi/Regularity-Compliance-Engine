from fastembed import TextEmbedding
import config

# if we put this inside a function, model is created on every function call, which increases latency
model = TextEmbedding(model_name=config.EMBED_MODEL)

def dense_embed(chunks:list) -> list:
    text = [chunk['text'] for chunk in chunks]
    
    # batch_size will process only 32 (since we have set) chunks at a time to avoid RAM overloading when there are thousands of chunks.
    embeddings = list(model.embed(text,batch_size=config.BATCH_SIZE))

    return embeddings