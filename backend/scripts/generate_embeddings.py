import pandas as pd
from sentence_transformers import SentenceTransformer
from sqlalchemy import text

from app.db.database import SessionLocal


MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE = 128


def main():

    db = SessionLocal()

    try:
        print("Loading embedding model...")

        model = SentenceTransformer(
            MODEL_NAME
        )

        products = db.execute(
            text("""
                SELECT id, search_text
                FROM products
                WHERE embedding IS NULL
            """)
        ).fetchall()

        print(
            f"Products needing embeddings: {len(products)}"
        )

        for start in range(
            0,
            len(products),
            BATCH_SIZE
        ):

            batch = products[
                start:start + BATCH_SIZE
            ]

            ids = [
                row.id
                for row in batch
            ]

            texts = [
                row.search_text
                for row in batch
            ]

            embeddings = model.encode(
                texts,
                normalize_embeddings=True,
                show_progress_bar=False
            )

            for product_id, embedding in zip(
                ids,
                embeddings
            ):
                db.execute(
                    text("""
                        UPDATE products
                        SET embedding = :embedding
                        WHERE id = :product_id
                    """),
                    {
                        "product_id": product_id,
                        "embedding": embedding.tolist()
                    }
                )

            db.commit()

            print(
                f"Embedded {min(start + BATCH_SIZE, len(products))}"
                f"/{len(products)}"
            )

        print("\n✓ Embeddings generated.")

    finally:
        db.close()


if __name__ == "__main__":
    main()