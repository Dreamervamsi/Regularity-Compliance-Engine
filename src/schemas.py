from pydantic import BaseModel, Field

class Source(BaseModel):
    document_name:str
    section_title:str
    page_no:int

class ComplianceResult(BaseModel):
    answer:str
    sources:list[Source]
    confidence_score:float
    refused:bool