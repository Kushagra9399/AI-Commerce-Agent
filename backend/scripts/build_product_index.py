import json
import os

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer


INPUT_FILE = (
    "scripts/data/croma_products_enriched.csv"
)

INDEX_FILE = (
    "data/product_index.faiss"
)

METADATA_FILE = (
    "data/product_metadata.json"
)


def main():

    df = pd.read_csv(INPUT_FILE)

    print("Products:", len(df))

    # Make sure search text exists
    df["search_text"] = (
        df["search_text"]
        .fillna("")
        .astype(str)
    )

    model = SentenceTransformer(
        "all-MiniLM-L6-v2"
    )

    print("Generating embeddings...")

    embeddings = model.encode(
        df["search_text"].tolist(),
        normalize_embeddings=True,
        show_progress_bar=True
    )

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    print(
        "Embedding shape:",
        embeddings.shape
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(
        dimension
    )

    index.add(embeddings)

    os.makedirs(
        os.path.dirname(INDEX_FILE),
        exist_ok=True
    )

    faiss.write_index(
        index,
        INDEX_FILE
    )

    metadata_columns = [
        "product_id",
        "name",
        "brand",
        "category",
        "market_price",
        "sale_price",
        "discount_percent",
        "stock",
        "is_active"
    ]

    metadata = (
        df[metadata_columns]
        .fillna("")
        .to_dict(orient="records")
    )

    with open(
        METADATA_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            metadata,
            f,
            ensure_ascii=False
        )

    print()
    print("Index created:", INDEX_FILE)
    print("Metadata created:", METADATA_FILE)


if __name__ == "__main__":
    main()