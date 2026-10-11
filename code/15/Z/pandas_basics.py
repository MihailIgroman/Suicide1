from pathlib import Path

import pandas as pd

STUDENT_NAME = "Andrii Zeliuk"   # ім'я та прізвище транслітерацією
STUDENT_GROUP = "IT-41"   # група
N = 11   # номер у списку групи + 5

print(f"{STUDENT_NAME}, {STUDENT_GROUP}, N = {N}")

# --- Завдання 1. Series: створення і доступ ---
print("--- Task 1 ---")
pages = pd.Series(
    {"Dune": 412, "Neuromancer": 271, "Hyperion": 482, "Solaris": 204, "Foundation": 255},
    name="pages",
)
print(pages)
print(pages["Hyperion"])
print(pages.iloc[0])
print(pages.loc["Neuromancer":"Solaris"].tolist())   # права межа входить
print(pages[["Dune", "Foundation"]].tolist())
print(pages.mean(), pages.max(), pages.idxmax())
big = pages > 50 * N
print(big)
print(pages[big].tolist())

# --- Завдання 2. Вирівнювання за мітками і NaN ---
print("--- Task 2 ---")
march = pd.Series({"Dune": 12.0, "Hyperion": 5.0, "Solaris": 8.0})
april = pd.Series({"Hyperion": 7.0, "Dune": 10.0, "Ubik": 4.0})

total = march + april
# NaN з'являється там, де мітка є лише в одній із серій (Solaris, Ubik),
# бо pandas складає значення за мітками, а не за позиціями.
print(total)
print(total.isna().sum())
print(total.dropna())
print(march.add(april, fill_value=0))

# --- Завдання 3. DataFrame і огляд таблиці ---
print("--- Task 3 ---")
books = pd.DataFrame({
    "title": ["Dune", "Neuromancer", "Hyperion", "Solaris", "Foundation", "Ubik"],
    "genre": ["sci-fi", "cyberpunk", "sci-fi", "classic", "classic", "cyberpunk"],
    "year": [1965, 1984, 1989, 1961, 1951, 1969],
    "pages": [412, 271, 482, 204, 255, 224],
    "price": [320.0, 275.5, 410.0, 189.9, 240.0, 295.0],
})
print(books)
print("shape:", books.shape)
print("columns:", list(books.columns))
print(books.dtypes)
books.info()   # info() друкує сам, print() не потрібен
print(books.describe())
print(books.head(2))
print(books.tail(2))

# --- Завдання 4. Вибір стовпців і рядків ---
print("--- Task 4 ---")
print(type(books["price"]))
print(type(books[["price"]]))
print(books[["title", "price"]])
print(books.loc[2])
print(books.iloc[0])
print(books.loc[1:3, ["title", "pages"]])   # .loc включає мітку 3
print(books.iloc[:3, :2])
print(books.loc[4, "price"], books.iloc[4, 4])

# --- Завдання 5. Замовлення книгарні ---
CSV_TEXT = """# export from bookshop-export v3
date;code;title;genre;copies;price
2026-03-01;0042;Dune;sci-fi;3;320,00
2026-03-01;0007;Ubik;cyberpunk;;295,00
2026-03-02;0113;Hyperion;sci-fi;2;410,00
2026-03-02;0042;Dune;sci-fi;5;320,00
2026-03-03;0085;Solaris;classic;4;189,90
2026-03-04;0007;Ubik;cyberpunk;6;295,00
2026-03-05;0261;Neuromancer;cyberpunk;-;275,50
2026-03-05;0330;Foundation;classic;7;240,00
2026-03-06;0113;Hyperion;sci-fi;4;410,00
2026-03-07;0042;Dune;sci-fi;1;320,00
"""
# створюємо файл поруч зі скриптом
csv_path = Path(__file__).with_name("orders.csv")
csv_path.write_text(CSV_TEXT, encoding="utf-8")

print("--- Task 5.1 ---")
orders = pd.read_csv(
    csv_path,
    comment="#",
    sep=";",
    decimal=",",
    na_values=["-"],
    dtype={"code": "str"},
    parse_dates=["date"],
)
print(orders)
print(orders.dtypes)

print("--- Task 5.2 ---")
print("shape:", orders.shape)
print(orders.isna().sum())

print("--- Task 5.3 ---")
# fillna повертає копію, тому присвоюємо результат назад
orders["copies"] = orders["copies"].fillna(0).astype("int64")
orders["revenue"] = orders["copies"] * orders["price"]
print(orders)

print("--- Task 5.4 ---")
print("total revenue:", round(orders["revenue"].sum(), 2))
print(orders.sort_values("revenue", ascending=False).head(3)[["date", "title", "revenue"]])

print("--- Task 5.5 ---")
mask = (orders["genre"] == "sci-fi") & (orders["revenue"] > 100 * N)
print(mask.sum())
print(orders.loc[mask, ["date", "title", "revenue"]])

print("--- Task 5.6 ---")
print(orders["genre"].value_counts())
