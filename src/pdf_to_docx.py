import os
import io
import tempfile
from pdf2docx import Converter

def convert_pdf_to_docx_in_memory(pdf_bytes: bytes, original_filename: str) -> tuple[io.BytesIO, str]:
    try:
        # 寫入暫存 PDF 檔
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(pdf_bytes)
            temp_pdf_path = temp_pdf.name

        # 建立暫存 DOCX 輸出檔案路徑
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_docx:
            temp_docx_path = temp_docx.name

        # 執行轉換
        cv = Converter(temp_pdf_path)
        cv.convert(temp_docx_path)
        cv.close()

        # 讀回 DOCX 結果並存入 memory buffer
        with open(temp_docx_path, "rb") as f:
            docx_output = io.BytesIO(f.read())

        # 清除暫存檔案
        os.remove(temp_pdf_path)
        os.remove(temp_docx_path)

        # 設定回傳檔名
        original_filename_without_ext = os.path.splitext(original_filename)[0]
        docx_filename = f"{original_filename_without_ext}.docx"

        return docx_output, docx_filename

    except Exception as e:
        raise Exception(f"PDF 轉換 DOCX 失敗: {str(e)}")
