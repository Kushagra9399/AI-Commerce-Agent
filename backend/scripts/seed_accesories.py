import uuid

from app.db.database import SessionLocal
from app.db.models import Product


MERCHANT_ID = "CROMA_DEMO"


ACCESSORIES = [
    {
        "name": "Croma 2.1 Channel Bluetooth Soundbar",
        "brand": "Croma",
        "category": "Audio",
        "overview": "2.1 channel soundbar suitable for TVs and home entertainment.",
        "specification": "Bluetooth, 2.1 Channel, Wireless Subwoofer",
        "price": 7999,
    },
    {
        "name": "Sony 2.1 Channel Bluetooth Soundbar",
        "brand": "Sony",
        "category": "Audio",
        "overview": "Sony soundbar for enhanced TV audio experience.",
        "specification": "Bluetooth, 2.1 Channel, Dolby Audio",
        "price": 12999,
    },
    {
        "name": "Croma HDMI 2.1 Cable 2 Meter",
        "brand": "Croma",
        "category": "TV Accessories",
        "overview": "High speed HDMI cable suitable for modern televisions and gaming consoles.",
        "specification": "HDMI 2.1, 2 Meter, 8K Support",
        "price": 999,
    },
    {
        "name": "Croma HDMI 2.0 Cable 1.5 Meter",
        "brand": "Croma",
        "category": "TV Accessories",
        "overview": "High speed HDMI cable for televisions and media devices.",
        "specification": "HDMI 2.0, 1.5 Meter, 4K Support",
        "price": 599,
    },
    {
        "name": "Croma Universal TV Wall Mount",
        "brand": "Croma",
        "category": "TV Accessories",
        "overview": "Universal wall mount for LED and smart televisions.",
        "specification": "Universal, VESA Compatible, Tilt Support",
        "price": 1499,
    },
    {
        "name": "Croma Full Motion TV Wall Mount",
        "brand": "Croma",
        "category": "TV Accessories",
        "overview": "Adjustable full-motion wall mount for large televisions.",
        "specification": "Full Motion, VESA Compatible, Tilt and Swivel",
        "price": 2499,
    },
    {
        "name": "Google TV Streaming Stick",
        "brand": "Google",
        "category": "Streaming Devices",
        "overview": "Streaming device for accessing entertainment applications on your television.",
        "specification": "4K Streaming, WiFi, Voice Remote",
        "price": 4999,
    },
    {
        "name": "Amazon Fire TV Stick 4K",
        "brand": "Amazon",
        "category": "Streaming Devices",
        "overview": "4K streaming device with voice control.",
        "specification": "4K, HDR, WiFi, Voice Remote",
        "price": 5999,
    },
    {
        "name": "Croma TV Cleaning Kit",
        "brand": "Croma",
        "category": "TV Accessories",
        "overview": "Cleaning kit designed for television displays.",
        "specification": "Microfiber Cloth, Screen Cleaner",
        "price": 399,
    },
    {
        "name": "Croma Universal Remote",
        "brand": "Croma",
        "category": "TV Accessories",
        "overview": "Universal replacement remote compatible with multiple television brands.",
        "specification": "Universal Compatibility, IR Remote",
        "price": 699,
    },
]


def create_product(accessory):
    product_id = str(uuid.uuid4())

    market_price = accessory["price"]

    # Fixed demo discounts.
    # Keeping these deterministic makes testing easier.
    discount_percent = 10.0

    sale_price = round(
        market_price * (1 - discount_percent / 100),
        2
    )

    return Product(
        id=product_id,
        merchant_id=MERCHANT_ID,
        source_id=900000 + len(product_id),
        link="https://demo.croma.local/product/" + product_id,
        name=accessory["name"],
        brand=accessory["brand"],
        category=accessory["category"],
        overview=accessory["overview"],
        images="",
        specification=accessory["specification"],
        search_text=(
            accessory["name"]
            + " "
            + accessory["brand"]
            + " "
            + accessory["category"]
            + " "
            + accessory["overview"]
            + " "
            + accessory["specification"]
        ),
        market_price=market_price,
        discount_percent=discount_percent,
        sale_price=sale_price,
        stock=20,
        is_active=True,
    )


def main():

    db = SessionLocal()

    try:

        existing = (
            db.query(Product)
            .filter(
                Product.merchant_id == MERCHANT_ID,
                Product.source_id >= 900000
            )
            .count()
        )

        if existing > 0:
            print(
                f"{existing} accessory products already exist."
            )
            return

        products = []

        for accessory in ACCESSORIES:

            product = create_product(accessory)

            products.append(product)

            db.add(product)

        db.commit()

        print("=" * 60)
        print("ACCESSORY SEED COMPLETE")
        print("=" * 60)

        print(f"Products inserted: {len(products)}")

        for product in products:

            print(
                f"{product.name} | "
                f"₹{product.sale_price} | "
                f"stock={product.stock}"
            )

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()


if __name__ == "__main__":
    main()