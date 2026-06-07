import pandas as pd

df = pd.read_csv("products.csv")

products = []

for _, row in df.iterrows():

    products.append({
        "name": str(row["name"]),
        "price": float(row["price"]),
        "image": str(row["image"]),
        "description": str(row["description"])
    })

df2 = pd.DataFrame(products)

df2.to_json(
    "products.json",
    orient="records",
    indent=4
)

print("Done")