import mammoth
import os
from pdf2docx import Converter
from bs4 import BeautifulSoup
import re
from langchain_core.documents import Document

def pdf2html(pdf_path):
    def convert_image(image):
        return {}
    docx_path = os.path.splitext(pdf_path)[0] + '.docx'
    cv = Converter(pdf_path)
    cv.convert(docx_path)
    cv.close()
    print(f"Converted {pdf_path} to {docx_path}")

    with open(docx_path, "rb") as docx_file:
        result = mammoth.convert_to_html(docx_file, convert_image=mammoth.images.img_element(convert_image))
        html_content = result.value
    print("Converted DOCX to HTML")
    return html_content



def html_preprocessing(pdf_path, html_content,chunk_size,chunk_overlap):
    def remove_links(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        for a in soup.find_all('a'):
            a.replace_with(a.text)
        text = str(soup)
        text = re.sub(r'\(https?://[^\s\)]+\)', '', text)
        return text
    def extract_tables(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        tables = soup.find_all('table')
        return [str(table) for table in tables]
    def html_to_plain_text(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()
    def find_substring_indices(main_string, sub_string, start_point):
        start = main_string[start_point:].find(sub_string)
        if start != -1:
            start += start_point
            end = start + len(sub_string)
            return (start, end)
        else:
            return None
    def remove_overlapping_ranges(html_loc_dict):
        items = list(html_loc_dict.items())
        items.sort(key=lambda x: x[1][0])
        result = {}
        for i in range(len(items)):
            current_html, current_range = items[i]
            is_contained = False
            
            for j in range(len(items)):
                if i != j:
                    _, other_range = items[j]
                    if (other_range[0] <= current_range[0] and 
                        current_range[1] <= other_range[1]):
                        is_contained = True
                        break
            if not is_contained:
                result[current_html] = current_range
        return result
    def create_chunks(text, chunk_size=chunk_size, overlap=chunk_overlap):
        chunks_dict = dict()
        start = 0
        while True:
            if start+ chunk_size < len(text):
                end = start + chunk_size
                chunk = text[start:end]
                chunks_dict[chunk] =  (start, end)
                start += chunk_size - overlap
            else:
                end = len(text)
                chunk = text[start:end]
                chunks_dict[chunk] =  (start, end)
                break
        return chunks_dict

    def extract_tables(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        tables = soup.find_all('table')
        return [str(table) for table in tables]
    def is_overlapping(chunks_loc, html_loc):
        target_start, target_end = chunks_loc[0], chunks_loc[1]
        start, end = html_loc[0], html_loc[1]
        return (start <= target_end) and (end >= target_start)

    def save_plain_text(text, output_path):
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)

    # 移除連結
    html_content = remove_links(html_content)
    print("Removed links from HTML")

    # HTML 轉純文字
    plain_text = html_to_plain_text(html_content)
    print("Converted HTML to plain text")

    tables = extract_tables(html_content)
    print(f"Extracted {len(tables)} tables from HTML")

    start_point = 0
    html_loc_dict = dict()
    for table in tables:
        table_texts = BeautifulSoup(table, 'html.parser').get_text()
        if table_texts != "":
            result = find_substring_indices(plain_text, table_texts, start_point)
            if result[0] != 0:
                start_point = result[0]
            html_loc_dict[table] = result

    html_loc_dict = remove_overlapping_ranges(html_loc_dict)
    print(f"Remove overlapping ranges")
    #往前和往後多抓100字元
    for table in html_loc_dict:
        original_loc = html_loc_dict[table]
        new_start = max(original_loc[0]-100, 0)
        new_end = min(original_loc[1]+100, len(plain_text))
        html_loc_dict[table] = (new_start, new_end)

    num_htmlloc_dict = dict()
    num_htmlloc_dict = {i:loc for i, loc in enumerate(html_loc_dict.values())}
    print(f"All accessible table has been linked with start and end point")
    
    chunk_loc_dict = create_chunks(plain_text, chunk_size=400, overlap=250)
    print(f"chunks created")

    
    result_docs = []
    for chunk in chunk_loc_dict:
        mt = dict()
        chunk_loc = chunk_loc_dict[chunk]
        data_tables = []
        should_end = 0
        start_search = 0
        for index in range(start_search, len(num_htmlloc_dict)):
            html_loc = num_htmlloc_dict[index]
            is_overlap = is_overlapping(chunk_loc, html_loc)
            if is_overlap:
                data_tables.append(index)
            if not is_overlap:
                should_end = index
            if index == should_end+3:
                break
        start_search = min(data_tables)
        mt["tables"] = data_tables
        mt["locs"] = chunk_loc
        mt["source"] = pdf_path
        new_doc = Document(page_content=chunk, metadata = mt)
        result_docs.append(new_doc)
        # mt["page"] = dict_content["start_page"]
    print("End of preprocessing")
    num_html_dict = {num_htmlloc_dict[loc]: html_loc_dict[loc] for loc in num_htmlloc_dict}
        
        
        
        
        
    return result_docs, num_html_dict


