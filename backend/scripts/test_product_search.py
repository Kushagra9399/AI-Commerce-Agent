from app.services.product_search_service import (
    ProductSearchService
)


def main():

    service = ProductSearchService()

    queries = [
        "Sony 55 inch 4K TV",
        "Samsung smart television under 60000",
        "LG 43 inch television",
        "large screen TV for gaming"
    ]

    for query in queries:

        print("\n" + "=" * 70)
        print("QUERY:", query)
        print("=" * 70)

        results = service.search(
            query=query,
            top_k=5,
            max_price=60000
        )

        for i, product in enumerate(
            results,
            start=1
        ):

            print(
                f"\n{i}. {product['name']}"
            )

            print(
                f"   Brand: {product['brand']}"
            )

            print(
                f"   Sale price: ₹{product['sale_price']}"
            )

            print(
                f"   Discount: "
                f"{product['discount_percent']}%"
            )

            print(
                f"   Stock: {product['stock']}"
            )

            print(
                f"   Similarity: "
                f"{product['similarity_score']}"
            )


if __name__ == "__main__":
    main()