import uuid
import os
from pypdf import PdfReader

def file_loader(file_info:list)->list:
    results=[]
    for file in file_info:   
        stream = file['stream']
        file_name = file['file_name']

        doc_content=[]

        doc=PdfReader(stream)
        for page in doc.pages:
            text=page.extract_text()
            if text:
                doc_content.append(text)
            
            extracted_content='\n'.join(doc_content)

        results.append({
            'id':str(uuid.uuid4()),
            'source_path':file_name,
            'text':extracted_content
        })
    
    return results