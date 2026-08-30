import pandas as pd
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Merchant, Product


CSV_FILE = "scripts/data/croma_products_category_refined.csv"

MERCHANT_ID = "CROMA_DEMO"
BATCH_SIZE = 1000


def load_merchant(db: Session):
    merchant = db.get(Merchant, MERCHANT_ID)

    if merchant:
        print("Merchant already exists.")
        return

    merchant = Merchant(
        id=MERCHANT_ID,
        name="Croma Demo Store",
        currency="INR"
    )

    db.add(merchant)
    db.commit()

    print("Merchant created.")


def load_products(db: Session):

    df = pd.read_csv(CSV_FILE)

    print(f"Processing {len(df)} products...")

    df["final_brand"] = df["extracted_brand"].fillna(df["brand"])

    source_ids = df["source_id"].astype(int).tolist()

    existing_products = (
        db.query(Product)
        .filter(Product.source_id.in_(source_ids))
        .all()
    )

    existing_map = {
        product.source_id: product
        for product in existing_products
    }

    inserted = 0
    updated = 0

    for _, row in df.iterrows():

        source_id = int(row["source_id"])

        product = existing_map.get(source_id)

        if product:

            # Existing product
            # IMPORTANT: keep the existing product.id

            product.merchant_id = row["merchant_id"]
            product.link = row["link"]
            product.name = row["name"]
            product.brand = row["final_brand"]
            product.category = row["extracted_category"]

            product.overview = (
                row["overview"]
                if pd.notna(row["overview"])
                else None
            )

            product.images = (
                row["images"]
                if pd.notna(row["images"])
                else None
            )

            product.specification = row["specification"]
            product.search_text = row["search_text"]
            product.market_price = float(row["market_price"])
            product.discount_percent = float(row["discount_percent"])
            product.sale_price = float(row["sale_price"])
            product.stock = int(row["stock"])
            product.is_active = bool(row["is_active"])

            updated += 1

        else:

            # New product
            product = Product(
                id=row["product_id"],
                merchant_id=row["merchant_id"],
                source_id=source_id,
                link=row["link"],
                name=row["name"],
                brand=row["brand"],
                category=row["category"],
                overview=(
                    row["overview"]
                    if pd.notna(row["overview"])
                    else None
                ),
                images=(
                    row["images"]
                    if pd.notna(row["images"])
                    else None
                ),
                specification=row["specification"],
                search_text=row["search_text"],
                market_price=float(row["market_price"]),
                discount_percent=float(row["discount_percent"]),
                sale_price=float(row["sale_price"]),
                stock=int(row["stock"]),
                is_active=bool(row["is_active"])
            )

            db.add(product)

            inserted += 1

        if (updated + inserted) % BATCH_SIZE == 0:
            db.commit()

            print(
                f"Processed {updated + inserted} products..."
            )

    db.commit()

    print(f"Updated:  {updated}")
    print(f"Inserted: {inserted}")


def main():

    db = SessionLocal()

    try:
        load_merchant(db)
        load_products(db)

        print("\n✓ Dataset loaded successfully.")

    except Exception as e:
        db.rollback()
        print("\n✗ Error:", e)
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()