def construct_metadata_filter(regulations:list,section):
    filters=[]
    
    if regulations:
        for regulation_name in regulations:
            filters.append({
                "regulation_name":regulation_name
            })
    
    if section:
        filters.append({
            "section_title":section
        })

    if not filters:
        return None
    
    if len(filters) > 1:
        return {"$or":filters}
    
    return filters[0]

def filter_chunks(chunks:list, regulation:list=None, section:str=None):
    if regulation is None and section is None:
        return chunks

    filtered_chunks = []
    for chunk in chunks:
        metadata = chunk.get("metadata",{})
        for regulation_name in regulation:
            match_reg = True if not regulation else (metadata.get("regulation_name") == regulation)
            match_sec = True if not section else (metadata.get("section_name") == section)

            if match_reg and match_sec:
                filtered_chunks.append(chunk)

    return filtered_chunks