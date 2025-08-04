from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.pdf_to_docx import convert_pdf_to_docx_in_memory
from src.docx_to_html import convert_docx_to_html
from src.pdf_to_html import convert_pdf_to_html
from src.gcs_utils import download_from_gcs, upload_to_gcs, generate_signed_url
import io

app = FastAPI()

# ✅ 顯示主頁資訊
@app.get("/")
def index():
    return {"message": "👋 Hello! Upload a PDF to /convert_pdf2word (file) or /convert_pdf2word_from_gcs (GCS params)."}

# ✅ 使用者上傳 PDF → 轉換成 DOCX 回傳
@app.post("/convert_pdf2word")
async def convert_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="請上傳 PDF 檔案")

    try:
        pdf_bytes = await file.read()
        docx_output, docx_filename = convert_pdf_to_docx_in_memory(pdf_bytes, file.filename)

        return StreamingResponse(
            content=docx_output,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{docx_filename}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 轉換失敗：{str(e)}")

# ✅ 定義用於 GCS 轉換的 JSON 請求格式
class ConvertRequest(BaseModel):
    source_bucket: str
    source_filename: str
    output_bucket: str = "converted-docx-output"

# ✅ 從 GCS 中下載 PDF → 轉換成 DOCX → 上傳回 GCS → 傳回下載連結
@app.post("/convert_pdf2word_from_gcs")
def convert_pdf_from_gcs(request: ConvertRequest):
    try:
        # Step 1: 從 GCS 抓 PDF
        pdf_bytes = download_from_gcs(request.source_bucket, request.source_filename)

        # Step 2: 轉換 PDF → DOCX
        docx_output, docx_filename = convert_pdf_to_docx_in_memory(pdf_bytes, request.source_filename)

        # Step 3: 上傳 DOCX 回 GCS
        upload_to_gcs(request.output_bucket, docx_filename, docx_output.getvalue())

        # Step 4: 產生可下載連結
        signed_url = generate_signed_url(request.output_bucket, docx_filename, expiration_minutes=60)

        return {
            "message": "轉換成功 ✅",
            "download_url": signed_url,
            "expires_in_minutes": 60
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"雲端轉換失敗：{str(e)}")
# ✅ 使用者上傳 PDF → 轉換成 DOCX 回傳
@app.post("/convert_word2html")
async def convert_word2html(file: UploadFile = File(...)):
    if not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="請上傳 DOCX 檔案")

    try:
        docx_bytes = await file.read()
        html_output, html_filename = convert_docx_to_html(docx_bytes, file.filename)

        return StreamingResponse(
            content=html_output,
            media_type="text/html",
            headers={"Content-Disposition": f'attachment; filename="{html_filename}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DOCX 轉換失敗：{str(e)}")

# ✅ 定義用於 GCS 轉換的 JSON 請求格式
class ConvertRequestWord(BaseModel):
    source_bucket: str
    source_filename: str
    output_bucket: str = "converted-html-output"

# ✅ 從 GCS 中下載 PDF → 轉換成 DOCX → 上傳回 GCS → 傳回下載連結
@app.post("/convert_word2html_from_gcs")
def convert_word2html_from_gcs(request: ConvertRequestWord):
    try:
        pdf_bytes = download_from_gcs(request.source_bucket, request.source_filename)
        html_output, html_filename = convert_pdf_to_html(pdf_bytes, request.source_filename)
        upload_to_gcs(request.output_bucket, html_filename, html_output.getvalue(), content_type="text/html")

        # Step 4: 產生可下載連結
        signed_url = generate_signed_url(request.output_bucket, html_filename, expiration_minutes=60)

        return {
            "message": "轉換成功 ✅",
            "download_url": signed_url,
            "expires_in_minutes": 60
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"雲端轉換失敗：{str(e)}")


# ✅ 使用者上傳 PDF → 轉換成 DOCX 回傳
@app.post("/convert_pdf2html")
async def convert_pdf2html(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="請上傳 PDF 檔案")

    try:
        pdf_bytes = await file.read()
        html_output, html_filename = convert_pdf_to_html(pdf_bytes, file.filename)

        return StreamingResponse(
            content=html_output,
            media_type="text/html",
            headers={"Content-Disposition": f'attachment; filename="{html_filename}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DOCX 轉換失敗：{str(e)}")


# ✅ 從 GCS 中下載 PDF → 轉換成 DOCX → 上傳回 GCS → 傳回下載連結
@app.post("/convert_word2pdf_from_gcs")
def convert_word2pdf_from_gcs(request: ConvertRequestWord):
    try:
        pdf_bytes = download_from_gcs(request.source_bucket, request.source_filename)
        html_output, html_filename = convert_pdf_to_html(pdf_bytes, request.source_filename)
        upload_to_gcs(request.output_bucket, html_filename, html_output.getvalue(), content_type="text/html")

        # Step 4: 產生可下載連結
        signed_url = generate_signed_url(request.output_bucket, html_filename, expiration_minutes=60)

        return {
            "message": "轉換成功 ✅",
            "download_url": signed_url,
            "expires_in_minutes": 60
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"雲端轉換失敗：{str(e)}")
