import uuid
import re
from pypdf import PdfReader

def file_loader(file_info:list)->list:
    results=[]
    for file in file_info:   
        stream = file['stream']
        file_name = file['file_name']
        extracted_text=""
        doc=PdfReader(stream)
        for page in doc.pages:
            text=page.extract_text()
            if text:
                extracted_text+='text' + "\n"

        pattern = r'^(?:Section|Article|Part|Chapter)\s+[\dIVXLC]+(?:\.\d+)*[.:]?\s*.+$',

        parts = re.split(pattern,extracted_text)

        for i in range(1,len(parts),2):
            section_title = parts[i].strip()

            content = parts[i+1].strip() if i<len(parts) else ""

            if content:
                results.append({
                    "section_title":section_title,
                    "text":content,
                    "source_path":file_name
                })
    
    return results