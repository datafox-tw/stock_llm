import mammoth
import os
original_filename = "測試複雜表格.docx"
with open(f"asset/test/{original_filename}", "rb") as docx_file:
    def convert_image(image):
        return {}

    result = mammoth.convert_to_html(docx_file, convert_image=mammoth.images.img_element(convert_image))
    html = result.value # The generated HTML
    messages = result.messages # Any messages, such as warnings during conversion
    print("END")
    original_filename_without_ext = os.path.splitext(original_filename)[0]
    html_filename = f"asset/test/{original_filename_without_ext}.html"
    with open(html_filename, "w", encoding="utf-8") as html_file:
        html_file.write(html)


# CLI用法
#  mammoth asset/test/測試複雜表格.docx asset/test/test.html