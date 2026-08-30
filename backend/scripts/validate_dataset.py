import pandas as pd


FILE = "scripts/data/croma_products_enriched.csv"


def main():
    df = pd.read_csv(FILE)

    print("=" * 60)
    print("DATASET VALIDATION")
    print("=" * 60)

    print("\nShape:")
    print(df.shape)

    print("\nColumns:")
    for column in df.columns:
        print(f"- {column}")

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nDuplicate product IDs:")
    print(df["product_id"].duplicated().sum())

    print("\nDuplicate product names:")
    print(df["name"].duplicated().sum())

    print("\nPrice statistics:")
    print(df["market_price"].describe())

    print("\nSale price statistics:")
    print(df["sale_price"].describe())

    print("\nDiscount statistics:")
    print(df["discount_percent"].describe())

    print("\nStock statistics:")
    print(df["stock"].describe())

    print("\nOut-of-stock products:")
    print((df["stock"] == 0).sum())

    print("\nActive products:")
    print(df["is_active"].sum())

    print("\nInactive products:")
    print((~df["is_active"]).sum())

    print("\nCategory count:")
    print(df["category"].nunique())

    print("\nTop categories:")
    print(df["category"].value_counts().head(20))

    print("\nPrice consistency check:")

    calculated_sale_price = (
        df["market_price"]
        * (1 - df["discount_percent"] / 100)
    ).round(2)

    inconsistent = (
        (calculated_sale_price - df["sale_price"]).abs() > 0.05
    ).sum()

    print(
        "Inconsistent prices:",
        inconsistent
    )

    print("\nDiscount range:")
    print(
        df["discount_percent"].min(),
        "to",
        df["discount_percent"].max()
    )

    print("\nStock range:")
    print(
        df["stock"].min(),
        "to",
        df["stock"].max()
    )

    print("\nSample:")
    print(
        df[
            [
                "product_id",
                "name",
                "category",
                "market_price",
                "discount_percent",
                "sale_price",
                "stock",
                "is_active"
            ]
        ].head(10)
    )


if __name__ == "__main__":
    main()