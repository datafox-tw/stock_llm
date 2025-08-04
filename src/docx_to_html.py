import io
import os
import mammoth

def convert_docx_to_html(docx_bytes: bytes, original_filename: str) -> tuple[str, str, list]:
    """
    將 DOCX 檔案的 bytes 轉換為 HTML 字串。
    這個函式直接在記憶體中操作，不需寫入暫存檔。

    Args:
        docx_bytes: DOCX 檔案的二進位內容。
        original_filename: 原始 DOCX 檔案的名稱，用於產生新的檔名。

    Returns:
        一個包含 (html_content, html_filename, messages) 的元組。
        - html_content: 轉換後的 HTML 字串。
        - html_filename: 建議的 HTML 檔案名稱 (例如：'document.html')。
        - messages: 轉換過程中產生的任何訊息 (例如警告)。
    
    Raises:
        Exception: 如果轉換過程中發生任何錯誤。
    """
    try:
        # 將傳入的 bytes 包裝成一個二進位檔案流 (file-like object)
        # 這樣 mammoth 套件就可以直接從記憶體中讀取，而不用操作實體檔案
        docx_file = io.BytesIO(docx_bytes)

        # 執行轉換
        result = mammoth.convert_to_html(docx_file)

        # 從結果中取得 HTML 內容
        html_content = result.value

        # 取得轉換過程中的訊息 (通常是警告，例如無法轉換某些格式)
        messages = result.messages
        if messages:
            print(f"處理檔案 '{original_filename}' 時，Mammoth 套件回報了以下訊息：")
            for message in messages:
                print(f"- [{message.type}] {message.message}")

        # 從原始檔名產生新的 HTML 檔名
        # 例如： "mydoc.docx" -> "mydoc.html"
        original_filename_without_ext = os.path.splitext(original_filename)[0]
        html_filename = f"{original_filename_without_ext}.html"

        return html_content, html_filename

    except Exception as e:
        # 捕捉所有可能的例外狀況，並拋出一個更具體的錯誤訊息
        raise Exception(f"將 DOCX 轉換為 HTML 時失敗: {str(e)}")

# --- 以下是使用範例 ---
# 執行此範例前，請先準備一個名為 "document.docx" 的 Word 檔案，並與此 Python 檔放在同一個資料夾。

def main():
    """主函式，用於示範如何使用轉換函式。"""
    sample_docx_file = "document.docx"
    
    try:
        # 1. 讀取 DOCX 檔案的二進位內容
        print(f"正在讀取檔案 '{sample_docx_file}'...")
        with open(sample_docx_file, "rb") as f:
            docx_bytes_content = f.read()
        
        print("檔案讀取成功。")

        # 2. 呼叫轉換函式
        print("開始進行 DOCX -> HTML 轉換...")
        html_output, output_filename, conversion_messages = convert_docx_to_html(
            docx_bytes=docx_bytes_content,
            original_filename=sample_docx_file
        )
        print("轉換完成！")

        # 3. 將產生的 HTML 內容儲存到檔案
        print(f"正在將結果儲存至 '{output_filename}'...")
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(html_output)
        
        print(f"成功儲存檔案！您可以開啟 '{output_filename}' 來查看結果。")

        # 如果有任何轉換訊息，再次顯示提醒
        if conversion_messages:
            print("\n提醒：轉換過程產生了一些訊息，可能部分內容或格式未被完整轉換。")

    except FileNotFoundError:
        print(f"\n錯誤：找不到檔案 '{sample_docx_file}'。")
        print("請確認您已經將一個 Word 檔案命名為 'document.docx' 並放在正確的位置。")
    except Exception as e:
        print(f"\n發生了無法預期的錯誤：{e}")


if __name__ == "__main__":
    main()
