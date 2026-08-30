import json
import os

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class ProductSearchService:

    def __init__(
        self,
        index_path: str = "data/product_index.faiss",
        metadata_path: str = "data/product_metadata.json"
    ):
        self.index_path = index_path
        self.metadata_path = metadata_path

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        self.index = None
        self.metadata = None

        self._load()

    def _load(self):

        if not os.path.exists(self.index_path):
            raise FileNotFoundError(
                f"FAISS index not found: {self.index_path}"
            )

        if not os.path.exists(self.metadata_path):
            raise FileNotFoundError(
                f"Metadata not found: {self.metadata_path}"
            )

        self.index = faiss.read_index(
            self.index_path
        )

        with open(
            self.metadata_path,
            "r",
            encoding="utf-8"
        ) as f:
            self.metadata = json.load(f)

    def search(
        self,
        query: str,
        top_k: int = 5,
        max_price: float | None = None,
        min_price: float | None = None,
        brand: str | None = None,
        min_discount: float | None = None,
        in_stock_only: bool = True
    ):

        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True
        )

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32"
        )

        scores, indices = self.index.search(
            query_embedding,
            max(top_k * 10, 50)
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):

            if index < 0:
                continue

            product = self.metadata[index]

            if in_stock_only and not product["is_active"]:
                continue

            if max_price is not None:
                if float(product["sale_price"]) > max_price:
                    continue

            if min_price is not None:
                if float(product["sale_price"]) < min_price:
                    continue

            if min_discount is not None:
                if float(product["discount_percent"]) < min_discount:
                    continue

            if brand is not None:
                if (
                    not product["brand"]
                    or product["brand"].lower() != brand.lower()
                ):
                    continue

            results.append({
                "product_id": product["product_id"],
                "name": product["name"],
                "brand": product["brand"],
                "category": product["category"],
                "market_price": product["market_price"],
                "sale_price": product["sale_price"],
                "discount_percent": product["discount_percent"],
                "stock": product["stock"],
                "is_active": product["is_active"],
                "similarity_score": round(
                    float(score),
                    4
                )
            })
                
            if len(results) >= top_k:
                break

        return results