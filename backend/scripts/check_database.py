from sqlalchemy import func
from app.db.database import SessionLocal
from app.db.models import Merchant, Product


def main():

    db = SessionLocal()

    try:
        merchant_count = db.query(
            func.count(Merchant.id)
        ).scalar()

        product_count = db.query(
            func.count(Product.id)
        ).scalar()

        active_count = db.query(
            func.count(Product.id)
        ).filter(
            Product.is_active == True
        ).scalar()

        out_of_stock = db.query(
            func.count(Product.id)
        ).filter(
            Product.stock == 0
        ).scalar()

        print("Merchants:", merchant_count)
        print("Products:", product_count)
        print("Active products:", active_count)
        print("Out of stock:", out_of_stock)

    finally:
        db.close()


if __name__ == "__main__":
    main()