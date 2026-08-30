from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session

from app.db.models import Product


class ProductSearchService:

    def __init__(self):
        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    def search(
        self,
        db: Session,
        query: str,
        max_price: float | None = None,
        brand: str | None = None,
        limit: int = 5,
    ):

        query_embedding = self.model.encode(
            query,
            normalize_embeddings=True
        )

        db_query = db.query(Product).filter(
            Product.is_active == True
        )

        # Hard constraint
        if max_price is not None:
            db_query = db_query.filter(
                Product.sale_price <= max_price
            )

        # Hard constraint
        if brand:
            db_query = db_query.filter(
                Product.brand.ilike(brand)
            )

        # Semantic ranking
        products = (
            db_query
            .order_by(
                Product.embedding.cosine_distance(
                    query_embedding.tolist()
                )
            )
            .limit(limit)
            .all()
        )

        return products