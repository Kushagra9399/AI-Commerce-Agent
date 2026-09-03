from sqlalchemy.orm import Session

from app.db.models import Product


class UpsellService:

    def find_upgrade(
        self,
        db: Session,
        product: Product,
        max_extra_percent: float = 20
    ):

        max_price = float(product.sale_price) * (
            1 + max_extra_percent / 100
        )

        candidates = (
            db.query(Product)
            .filter(
                Product.is_active == True,
                Product.stock > 0,
                Product.merchant_id == product.merchant_id,
                Product.category == product.category,
                Product.id != product.id,
                Product.sale_price > product.sale_price,
                Product.sale_price <= max_price
            )
            .order_by(
                Product.sale_price.asc()
            )
            .limit(20)
            .all()
        )

        if not candidates:
            return None

        # Prefer same brand
        same_brand = [
            p for p in candidates
            if p.brand and product.brand
            and p.brand.lower() == product.brand.lower()
        ]

        if same_brand:
            return same_brand[0]

        return candidates[0]