import uuid

from app.db.database import SessionLocal
from app.db.models import Product, ProductRelation


MERCHANT_ID = "CROMA_DEMO"


# Category -> recommended categories
CROSS_SELL_RULES = {
    "Television": [
        ("Audio Devices", 5),
        ("Cables", 4),
        ("Protection", 3),
        ("Home Accessories", 2),
    ],

    "Audio Devices": [
        ("Audio", 5),
        ("Cables", 4),
        ("Protection", 3),
        ("Charger", 2),
    ],

    "Audio": [
        ("Audio Devices", 5),
        ("Cables", 4),
        ("Protection", 3),
        ("Charger", 2),
    ],

    "Mobile": [
        ("Case/Cover", 5),
        ("Protection", 4),
        ("Charger", 3),
        ("Power Bank", 2),
        ("Cables", 1),
    ],

    "Laptop": [
        ("Computer Accessories", 5),
        ("Backpack", 4),
        ("Mouse", 3),
        ("Cables", 2),
        ("Protection", 1),
    ],

    "Computer Accessories": [
        ("Laptop", 4),
        ("Monitor", 3),
        ("Cables", 2),
        ("Protection", 1),
    ],

    "Camera": [
        ("Memory Card", 5),
        ("Battery", 4),
        ("Camera Accessories", 3),
        ("Protection", 2),
        ("Backpack", 1),
    ],

    "Gaming": [
        ("Audio Devices", 5),
        ("Cables", 4),
        ("Computer Accessories", 3),
        ("Protection", 2),
    ],

    "Printer": [
        ("Cables", 4),
        ("Computer Accessories", 3),
        ("Protection", 2),
    ],

    "Projector": [
        ("Cables", 5),
        ("Computer Accessories", 3),
        ("Home Accessories", 2),
        ("Protection", 1),
    ],

    "Router": [
        ("Cables", 5),
        ("Computer Accessories", 3),
        ("Power Bank", 1),
    ],

    "Air Conditioner": [
        ("Protection", 4),
        ("Home Accessories", 3),
    ],

    "Refrigerator": [
        ("Protection", 4),
        ("Home Accessories", 3),
    ],

    "Geyser": [
        ("Protection", 4),
        ("Home Accessories", 3),
    ],

    "Air Cooler": [
        ("Protection", 3),
        ("Home Accessories", 2),
    ],

    "Air Purifier": [
        ("Protection", 3),
        ("Home Accessories", 2),
    ],

    "Fan": [
        ("Protection", 3),
        ("Home Accessories", 2),
    ],

    "Kettle": [
        ("Home Accessories", 3),
        ("Protection", 2),
    ],

    "Charger": [
        ("Cables", 5),
        ("Power Bank", 4),
        ("Protection", 2),
    ],

    "Power Bank": [
        ("Cables", 5),
        ("Charger", 4),
        ("Protection", 2),
    ],

    "Memory Card": [
        ("Camera", 4),
        ("Computer Accessories", 3),
        ("Protection", 2),
    ],

    "Pendrive": [
        ("Computer Accessories", 4),
        ("Cables", 3),
        ("Protection", 2),
    ],

    "Monitor": [
        ("Computer Accessories", 5),
        ("Cables", 4),
        ("Protection", 2),
    ],

    "Backpack": [
        ("Laptop", 3),
        ("Computer Accessories", 2),
        ("Protection", 1),
    ],

    "Case/Cover": [
        ("Mobile", 3),
        ("Protection", 2),
    ],

    "Cables": [
        ("Charger", 4),
        ("Computer Accessories", 3),
        ("Mobile", 2),
        ("Audio Devices", 1),
    ],
}


def main():

    db = SessionLocal()

    try:

        # Prevent duplicate relationships
        existing = db.query(ProductRelation).count()

        if existing > 0:
            print(
                f"{existing} product relations already exist."
            )
            return

        # Get all active products for this merchant
        products = (
            db.query(Product)
            .filter(
                Product.merchant_id == MERCHANT_ID,
                Product.is_active.is_(True)
            )
            .all()
        )

        print(f"Active products: {len(products)}")

        # Group products by category
        products_by_category = {}

        for product in products:

            category = product.category

            if not category:
                continue

            products_by_category.setdefault(
                category,
                []
            ).append(product)

        print(
            f"Categories found: {len(products_by_category)}"
        )

        relations = []

        for product in products:

            category = product.category

            if category not in CROSS_SELL_RULES:
                continue

            recommendations = CROSS_SELL_RULES[category]

            for target_category, priority in recommendations:

                candidates = products_by_category.get(
                    target_category,
                    []
                )

                if not candidates:
                    continue

                # Add a limited number of products
                # from the recommended category
                for accessory in candidates[:3]:

                    # Never recommend the same product
                    if accessory.id == product.id:
                        continue

                    relation = ProductRelation(
                        id=str(uuid.uuid4()),
                        source_product_id=product.id,
                        target_product_id=accessory.id,
                        relation_type="cross_sell",
                        priority=priority
                    )

                    relations.append(relation)
                    db.add(relation)

        db.commit()

        print("=" * 60)
        print("PRODUCT RELATIONS CREATED")
        print("=" * 60)

        print(
            f"Relations inserted: {len(relations)}"
        )

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()


if __name__ == "__main__":
    main()
