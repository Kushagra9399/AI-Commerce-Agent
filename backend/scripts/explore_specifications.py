import json
import pandas as pd
from collections import Counter


INPUT_FILE = "scripts/data/croma_products_enriched.csv"


def main():

    df = pd.read_csv(INPUT_FILE)

    print("=" * 70)
    print("SPECIFICATION EDA")
    print("=" * 70)

    print("\nDataset shape:")
    print(df.shape)

    print("\nSpecification missing:")
    print(df["specification"].isna().sum())

    key_counter = Counter()
    invalid_json = 0
    valid_json = 0

    examples = {}

    for value in df["specification"]:

        if pd.isna(value):
            continue

        try:

            data = json.loads(value)

            if not isinstance(data, dict):
                continue

            valid_json += 1

            for key, value in data.items():

                key_counter[key] += 1

                if key not in examples:
                    examples[key] = value

        except (json.JSONDecodeError, TypeError):

            invalid_json += 1

    print("\nValid JSON:")
    print(valid_json)

    print("\nInvalid JSON:")
    print(invalid_json)

    print("\nUnique specification keys:")
    print(len(key_counter))

    print("\nTop specification keys:")
    print("-" * 70)

    for key, count in key_counter.most_common():

        print(f"{count:6} | {key}")

    print("\n" + "=" * 70)
    print("EXAMPLES")
    print("=" * 70)

    for key, example in examples.items():

        print(f"\nKEY: {key}")
        print(f"EXAMPLE: {example}")


if __name__ == "__main__":
    main()