import csv
import pathlib

fpt = pathlib.Path("data", "isbn.tsv")

with open(fpt, "r", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter="\t") 
    # code isbn title
    # if isbn appeared before, ignore
    appeared_isbn = set()
    isbn_data = []
    for code, isbn, title in reader:
        if isbn in appeared_isbn:
            continue
        appeared_isbn.add(isbn)
        isbn_data.append([code, isbn, title])

with open(fpt, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerows(isbn_data)