
def construct_metadata_filter(regulation,section):
    filters=[]
    
    if regulation:
        filters.append({
            "regulation_name":regulation
        })
    
    if section:
        filters.append({
            "section_name":section
        })

    if not filters:
        return None
    
    if len(filters) > 1:
        return {"$and":filters}
    
    return filters[0]

def filter_chunks(chunks:list, regulation, section):
    if regulation is None and section is None:
        return chunks

    filtered_chunks = []
    for chunk in chunks:
        metadata = chunk.get("metadata",{})

        match_reg = True if not regulation else (metadata.get("regulation_name") == regulation)
        match_sec = True if not section else (metadata.get("section_name") == section)

        if match_reg and match_sec:
            filtered_chunks.append(chunk)
    
    return filtered_chunks