from google.cloud import storage
from datetime import timedelta

def download_from_gcs(bucket_name: str, file_name: str) -> bytes:
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    return blob.download_as_bytes()

def upload_to_gcs(
    bucket_name: str,
    file_name: str,
    content: bytes,
    content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
) -> None:
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    blob.upload_from_string(content, content_type=content_type)

    # ❌ 不再使用這行！會觸發 ACL 錯誤：
    # blob.make_public()

    # ✅ 不回傳 public_url，改由簽名網址 generate_signed_url 處理，避免了公開權限錯誤
    # 只要拿到 signed_url，誰都可以下載，只要在有效期限內！
    # 因為你不想讓全世界的人都能隨便下載你的檔案，但你還是想要「有權限的人能短時間下載它」。

def generate_signed_url(bucket_name: str, file_name: str, expiration_minutes: int = 60) -> str:
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=expiration_minutes),
        method="GET"
    )
    return url