import json
import os

from fastapi import FastAPI, Request, Form
from openai import OpenAI

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from .utils import isbn_to_barcode
from .prompt import SYSTEM_PROMPT, isbn_data

app = FastAPI()

# Set up templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# deepseek config
api_key = os.getenv("DEEPSEEK_API_KEY")
base_url = os.getenv("DEEPSEEK_BASE_URL")
client = OpenAI(api_key=api_key, base_url=base_url)
MOUDLE_NAME = "deepseek-chat"

# # openai config
# client = OpenAI(
#     api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL")
# )
# MOUDLE_NAME = "gpt-4o-mini"


ISBN_SUFFIX = "L"


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

        for _ in range(3):
            response = client.chat.completions.create(
                model=MOUDLE_NAME,
                messages=messages,  # type: ignore
                temperature=0.1,
                max_tokens=1000,
                response_format={"type": "json_object"},
            )
            try:
                print(response.choices[0].message.content)
                books = json.loads(response.choices[0].message.content)  # type: ignore
            except Exception as e:
                print(f"Error parsing response: {e}")
                books = {}
                continue

            print(books)
            if isbn_data.check_ai_return(books):
                break

        if len(books) > 0:
            # 生成条形码
            books["barcode"] = isbn_to_barcode(books["isbn"] + ISBN_SUFFIX)
            # books["barcode"] = text_to_qrcode(books["isbn"] + "T")
            return {
                "book": books["code"] + " " + books["book"],
                "isbn": books["isbn"] + ISBN_SUFFIX,
                "barcode": books["barcode"],
            }

        return {"error": "未找到匹配的图书"}
    except Exception as e:
        return {"error": str(e)}


def main() -> int:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
    return 0


if __name__ == "__main__":
    main()
