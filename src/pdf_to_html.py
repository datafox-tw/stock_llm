import os
import io
import tempfile
import mammoth
from pdf2docx import Converter

def convert_pdf_to_html(pdf_bytes: bytes, original_filename: str) -> tuple[str, str, list]:
    """
    將 PDF 檔案的 bytes 直接轉換為 HTML 字串。
    
    這是一個兩階段的轉換過程：
    1. PDF -> DOCX (使用 pdf2docx，透過暫存檔案)
    2. DOCX -> HTML (使用 mammoth，在記憶體中)

    Args:
        pdf_bytes: PDF 檔案的二進位內容。
        original_filename: 原始 PDF 檔案的名稱，用於產生最終的 HTML 檔名。

    Returns:
        一個包含 (html_content, html_filename, messages) 的元組。
        - html_content: 最終轉換後的 HTML 字串。
        - html_filename: 建議的 HTML 檔案名稱 (例如：'document.html')。
        - messages: 從 mammoth 套件回傳的轉換訊息 (例如警告)。
    
    Raises:
        Exception: 如果轉換過程中任何一個環節發生錯誤。
    """
    temp_pdf_path = None
    temp_docx_path = None

    try:
        # --- 階段一：PDF -> DOCX ---
        
        # 建立一個暫存檔案來寫入 PDF 內容，因為 pdf2docx 需要檔案路徑
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(pdf_bytes)
            temp_pdf_path = temp_pdf.name

        # 建立一個暫存檔案路徑來接收轉換後的 DOCX 內容
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_docx:
            temp_docx_path = temp_docx.name

        # 執行 PDF 到 DOCX 的轉換
        cv = Converter(temp_pdf_path)
        cv.convert(temp_docx_path, start=0, end=None)
        cv.close()

        # 從暫存檔讀取 DOCX 的二進位內容
        with open(temp_docx_path, "rb") as f:
            docx_bytes = f.read()

    except Exception as e:
        raise Exception(f"階段一 (PDF -> DOCX) 轉換失敗: {str(e)}")
    
    finally:
        # 清理暫存檔案
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
        if temp_docx_path and os.path.exists(temp_docx_path):
            os.remove(temp_docx_path)

    try:
        # --- 階段二：DOCX -> HTML ---
        
        # 將 DOCX 的 bytes 傳入記憶體流
        docx_file_stream = io.BytesIO(docx_bytes)

        # 執行 DOCX 到 HTML 的轉換
        result = mammoth.convert_to_html(docx_file_stream)
        html_content = result.value
        #messages = result.messages

        # 產生最終的 HTML 檔名
        original_filename_without_ext = os.path.splitext(original_filename)[0]
        html_filename = f"{original_filename_without_ext}.html"

        return html_content, html_filename

    except Exception as e:
        raise Exception(f"階段二 (DOCX -> HTML) 轉換失敗: {str(e)}")