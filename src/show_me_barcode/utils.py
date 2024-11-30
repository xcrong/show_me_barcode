import io
import base64
import barcode
from barcode import generate


def isbn_to_barcode(isbn: str) -> str:
    """将ISBN转换为base64编码的条形码图片"""
    try:
        # 生成条形码到内存
        rv = io.BytesIO()
        generate("ean13", isbn, writer=barcode.writer.ImageWriter(), output=rv)

        # 转换为base64
        encoded = base64.b64encode(rv.getvalue()).decode()
        return f"data:image/png;base64,{encoded}"
    except Exception as e:
        print(f"Error generating barcode: {e}")
        return ""


if __name__ == "__main__":
    # 测试代码
    isbn = "9787540691837"
    print(isbn_to_barcode(isbn))
