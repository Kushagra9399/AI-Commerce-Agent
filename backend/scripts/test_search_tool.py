from app.agent.tools import search_products


def main():

    result = search_products(
        query="55 inch 4K smart television",
        brand="Sony",
        max_price=60000,
        top_k=5
    )

    print("\nQUERY")
    print(result["query"])

    print("\nFILTERS")
    print(result["filters"])

    print(
        f"\nRESULTS: {result['count']}"
    )

    for i, product in enumerate(
        result["products"],
        start=1
    ):

        print(
            f"\n{i}. {product['name']}"
        )

        print(
            f"   Brand: {product['brand']}"
        )

        print(
            f"   Price: ₹{product['sale_price']}"
        )

        print(
            f"   Discount: "
            f"{product['discount_percent']}%"
        )

        print(
            f"   Stock: {product['stock']}"
        )


if __name__ == "__main__":
    main()