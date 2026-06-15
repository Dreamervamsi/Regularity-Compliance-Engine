import uuid
import re
from pypdf import PdfReader

def file_loader(file_info:list)->list:
    results=[]
    # pattern = r'(?m)^((?:Section|Article|Part|Chapter)\s+[\dIVXLC]+(?:\.\d+)*[.:]?\s*.+)$'
    pattern = r'^((?:Section|Article|Part|Chapter)\s+[\dIVXLC]+(?:\.\d+)*[.:]?\s*.+)$'
    
    for file in file_info:   
        stream = file['stream']
        file_name = file['file_name']
        doc=PdfReader(stream)

        page_content=[]
        for page_num,page in enumerate(doc.pages,start=1):
            text=page.extract_text()
            if text:    
                page_content.append({"page_num":page_num,"text":text})
        
        marked_pages = []
        for page in page_content:
            marked_text = f"__PAGE_NUM_{page['page_num']}__\n{page['text']}"
            marked_pages.append(marked_text)
        
        extracted_text = "\n".join(marked_pages)

        parts = re.split(pattern, extracted_text, flags=re.MULTILINE)

        for i in range(1,len(parts),2):
            section_title = parts[i].strip()

            content = parts[i+1].strip() if i+1 <len(parts) else ""

            page_match = re.search(r'__PAGE_NUM_(\d+)__', content)
            current_page = int(page_match.group(1)) if page_match else 1

            if section_title or content:
                results.append({
                    "id":str(uuid.uuid4()),
                    "section_title":section_title,
                    "text":content,
                    "source_path":file_name,
                    "page_no":current_page
                })
    
    return results