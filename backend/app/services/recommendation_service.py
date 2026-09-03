from sqlalchemy.orm import Session

from app.db.models import Product, ProductRelation


class RecommendationService:

    def get_cross_sell_products(
        self,
        db: Session,
        product_id: str,
        budget_remaining: float | None = None,
        limit: int = 3
    ):

        query = (
            db.query(Product)
            .join(
                ProductRelation,
                ProductRelation.target_product_id == Product.id
            )
            .filter(
                ProductRelation.source_product_id == product_id,
                ProductRelation.relation_type == "cross_sell",
                Product.is_active.is_(True),
                Product.stock > 0
            )
        )

        source_merchant_id = (
            db.query(Product.merchant_id)
            .filter(Product.id == product_id)
            .scalar()
        )

        if source_merchant_id is None:
            return []

        query = query.filter(
            Product.merchant_id == source_merchant_id
        )

        if budget_remaining is not None:

            query = query.filter(
                Product.sale_price <= budget_remaining
            )

        products = (
            query
            .order_by(
                ProductRelation.priority.desc()
            )
            .limit(limit)
            .all()
        )

        return products