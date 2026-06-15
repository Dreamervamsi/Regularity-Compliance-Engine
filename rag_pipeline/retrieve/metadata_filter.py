
def metadata_filter(regulation,section):
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