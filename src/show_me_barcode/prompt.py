import csv
import pathlib
import pydantic


class Book(pydantic.BaseModel):
    code: str
    isbn: str
    title: str


class Books:
    def __init__(self, tsv_fpth: pathlib.Path):
        with open(tsv_fpth, "r", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter="\t")
            self.books = [Book(code=row[0], isbn=row[1], title=row[2]) for row in reader]

    def check_ai_return(self, books: dict):
        code = books["code"]
        isbn = books["isbn"]

        for book in self.books:
            if book.code == code and book.isbn == isbn:
                return True

        return False

    def get_pure_text_data(self):
        return "\n".join(
            [f"{book.code}\t{book.isbn}\t{book.title}" for book in self.books]
        )


# # Load ISBN data
# with open("data/isbn.tsv", "r", encoding="utf-8") as f:
#     reader = csv.reader(f, delimiter="\t")
#     isbn_data = [row for row in reader]

isbn_data = Books(pathlib.Path("data", "isbn.tsv"))


SYSTEM_PROMPT = f"""
```tsv
{isbn_data.get_pure_text_data()}
```

请你根据输入的片段信息，给出对应的书籍及其isbn编码

EXAMPLE INPUT 1: 
南方新课堂 五年级语文

EXAMPLE JSON OUTPUT 1:
{{
    "code": "J0033",
    "book": "南方新课堂金牌学案 语文 五年级(上)人教版（配送）",
    "isbn": "9787540691837"
}}

EXAMPLE INPUT 2: 
百年学典全优课堂，思想政治选择性必修一

EXAMPLE JSON OUTPUT 2:
{{
    "code": "L7081",
    "book": "百年学典全优课堂 思想政治 选择性必修1当代国际政治与经济人教版（教参）",
    "isbn": "9787554843772"
}}

"""

# L7081	9787554843772	百年学典全优课堂 思想政治 选择性必修1当代国际政治与经济人教版（教参）
