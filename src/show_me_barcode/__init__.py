import csv
import json
import os

from fastapi import FastAPI, Request, Form
from openai import OpenAI

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from .utils import isbn_to_barcode

app = FastAPI()

# Set up templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# OpenAI configuration
api_key = os.getenv("DEEPSEEK_API_KEY")
base_url = os.getenv("DEEPSEEK_API_BASE")
client = OpenAI(api_key=api_key, base_url=base_url)

# Load ISBN data
with open("data/isbn.tsv", "r", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter="\t")
    isbn_data = [row for row in reader]


SYSTEM_PROMPT = f"""
```tsv
{isbn_data}
```

请你根据输入的片段信息，给出对应的书籍及其isbn编码

EXAMPLE INPUT: 
南方新课堂 五年级语文

EXAMPLE JSON OUTPUT:
{{
    "book": "南方新课堂金牌学案 语文 五年级(上)人教版（配送）",
    "isbn": "9787540691837",
}}


"""


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/search")
async def search(query: str = Form(...)):
    try:
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {"role": "user", "content": query},
        ]

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
            response_format={"type": "json_object"},
        )

        books = json.loads(response.choices[0].message.content)

        if len(books) > 0:
            # 生成条形码
            books["barcode"] = isbn_to_barcode(books["isbn"])
            return books

        return {"error": "未找到匹配的图书"}
    except Exception as e:
        return {"error": str(e)}


def main() -> int:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
    return 0


if __name__ == "__main__":
    main()
