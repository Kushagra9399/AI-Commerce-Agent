import re
import ast
import pandas as pd


INPUT_FILE = "scripts/data/croma_products_enriched.csv"
OUTPUT_FILE = "scripts/data/croma_products_category_extracted.csv"


# =========================================================
# CATEGORY NORMALIZATION
# =========================================================

CATEGORY_MAPPING = {

    # Home / Accessories
    "Home Accessories Category": "Home Accessories",

    # Machines
    "Machine Category": "Machine",
    "Sewing Machine Category": "Sewing Machine",

    # Television
    "Television Category": "Television",

    # Air
    "Air Conditioner Category": "Air Conditioner",
    "Air Cooler Category": "Air Cooler",
    "Air Purifier Category": "Air Purifier",

    # Audio
    "Audio Category": "Audio",

    # Camera
    "Camera Category": "Camera",

    # Car
    "Car Accessories Category": "Car Accessories",

    # Computer
    "Computer Accessories Category": "Computer Accessories",

    # Device
    "Device Category": "Device",

    # Fitness
    "Fitness Equipments Category": "Fitness Equipment",

    # Laptop
    "Laptop Category": "Laptop",

    # Mobile
    "Mobile Category": "Mobile",

    # PPA
    "PPA Category": "PPA",

    # General product category
    "Product Category": "Product",
}


# =========================================================
# SPECIFIC RULES
# =========================================================

# For categories where the exact inner key is known.
SPECIFIC_KEYS = {

    "Home Accessories Category": [
        "Product Type"
    ],

    "Machine Category": [
        "Machine Type"
    ],

    "Sewing Machine Category": [
        "Machine Category"
    ],

    "Television Category": [
        "Television Type"
    ],

    "Air Conditioner Category": [
        "Air Conditioner Type"
    ],

    "Air Cooler Category": [
        "Air Cooler Type"
    ],

    "Air Purifier Category": [
        "Product Type"
    ],

    "Camera Category": [
        "Camera Type"
    ],

    "Car Accessories Category": [
        "Product Type"
    ],

    "Computer Accessories Category": [
        "Product Type"
    ],

    "Device Category": [
        "Device Type"
    ],

    "Fitness Equipments Category": [
        "Product Type"
    ],

    "Laptop Category": [
        "Laptop Type",
        "Product Type"
    ],

    "Mobile Category": [
        "Mobile Type"
    ],

    "PPA Category": [
        "Product Type"
    ],

    # Existing Product Category cases
    "Product Category": [
        "Device Type",
        "Fan Type",
        "Geyser Type",
        "Product Type",
        "Refrigerator Type",
        "Projector Type",
        "Battery Technology",
        "Capacity",
        "Dishwasher Type",
    ],
}


# =========================================================
# HELPERS
# =========================================================

def parse_specification(text):
    """
    Try to convert specification string into a Python dictionary.

    Example:
    "{'Product Category': {'Projector Type': 'DLP '}}"
    """

    if pd.isna(text):
        return None

    text = str(text).strip()

    try:
        data = ast.literal_eval(text)

        if isinstance(data, dict):
            return data

    except Exception:
        pass

    return None


def extract_key_value(text, key):
    """
    Extract:

    'Product Type': 'Smart Remote Control'

    from raw specification text.
    """

    if pd.isna(text):
        return None

    text = str(text)

    pattern = (
        r"['\"]"
        + re.escape(key)
        + r"['\"]"
        r"\s*:\s*"
        r"['\"]"
        r"(.*?)"
        r"['\"]"
    )

    match = re.search(pattern, text)

    if not match:
        return None

    value = match.group(1).strip()

    if not value:
        return None

    return value


def get_category_dict(data, category):
    """
    Return the inner dictionary for a category.

    Example:

    {
        'Product Category': {
            'Projector Type': 'DLP'
        }
    }

    returns:

    {
        'Projector Type': 'DLP'
    }
    """

    if not isinstance(data, dict):
        return None

    value = data.get(category)

    if isinstance(value, dict):
        return value

    return None


# =========================================================
# MANUFACTURER BRAND EXTRACTION
# =========================================================

def extract_brand(text):
    """
    Extract:

    {'Manufacturer Details': {'Brand': 'boAt'}}

    -> boAt
    """

    data = parse_specification(text)

    if not data:
        return None

    manufacturer = data.get("Manufacturer Details")

    if not isinstance(manufacturer, dict):
        return None

    brand = manufacturer.get("Brand")

    if brand is None:
        return None

    brand = str(brand).strip()

    return brand if brand else None


# =========================================================
# PRODUCT CATEGORY EXTRACTION
# =========================================================

def extract_product_category(text):
    """
    Returns:

        category, product_type

    """

    data = parse_specification(text)

    if not data:
        return None, None

    # -----------------------------------------------------
    # 1. ACCESSORIES SPECIAL CASE
    # -----------------------------------------------------
    #
    # Example:
    #
    # 'In The Box': {
    #     'Generic Name': 'Earphone/Headphone',
    #     'Main Product': '1 U Headphone',
    #     'Accessories': 'USB Cable'
    # }
    #
    # User specifically wants Accessories as product type.
    #
    # -----------------------------------------------------

    for section_name, section_data in data.items():

        if not isinstance(section_data, dict):
            continue

        if "Accessories" in section_data:

            accessories = section_data.get("Accessories")

            if accessories:
                accessories = str(accessories).strip()

                if accessories:
                    # We don't know the actual category here,
                    # so continue category detection below.
                    #
                    # The Accessories value is stored separately
                    # and can override the normal product type.
                    accessories_value = accessories
                    break
    else:
        accessories_value = None


    # -----------------------------------------------------
    # 2. SPECIFIC CATEGORY PROCESSING
    # -----------------------------------------------------

    for source_category, keys in SPECIFIC_KEYS.items():

        inner = get_category_dict(
            data,
            source_category
        )

        if inner is None:
            continue

        normalized_category = CATEGORY_MAPPING.get(
            source_category,
            source_category
        )

        # -------------------------------------------------
        # Try known keys
        # -------------------------------------------------

        for key in keys:

            value = inner.get(key)

            if value is None:
                continue

            value = str(value).strip()

            if not value:
                continue


            # =============================================
            # PROJECTOR
            # =============================================

            if key == "Projector Type":

                projector_type = value

                # LCD | LED -> LCD/LED Projector
                if "|" in projector_type:

                    projector_type = re.sub(
                        r"\s*\|\s*",
                        "/",
                        projector_type
                    )

                return (
                    "Projector",
                    f"{projector_type} Projector"
                )


            # =============================================
            # REFRIGERATOR
            # =============================================

            if key == "Refrigerator Type":

                return (
                    "Refrigerator",
                    value
                )


            # =============================================
            # BATTERY TECHNOLOGY
            # =============================================

            if key == "Battery Technology":

                return (
                    "Power Bank",
                    "Power Bank"
                )


            # =============================================
            # CAPACITY
            # =============================================

            if key == "Capacity":

                # Example:
                # 16GB
                # 32 GB
                # 128gb

                if re.search(
                    r"\b\d+(?:\.\d+)?\s*GB\b",
                    value,
                    re.IGNORECASE
                ):

                    capacity = re.sub(
                        r"\s+",
                        "",
                        value
                    )

                    return (
                        "Pendrive",
                        f"Pendrive {capacity}"
                    )


            # =============================================
            # DISHWASHER
            # =============================================

            if key == "Dishwasher Type":

                return (
                    "Dishwasher",
                    f"Dishwasher {value}"
                )


            # =============================================
            # TELEVISION
            # =============================================

            if key == "Television Type":

                return (
                    "Television",
                    value
                )


            # =============================================
            # LAPTOP
            # =============================================

            if source_category == "Laptop Category":

                return (
                    "Laptop",
                    value
                )


            # =============================================
            # COMPUTER ACCESSORIES
            # =============================================

            if source_category == "Computer Accessories Category":

                return (
                    "Computer Accessories",
                    value
                )


            # =============================================
            # NORMAL CASE
            # =============================================

            return (
                normalized_category,
                value
            )


        # -------------------------------------------------
        # Generic fallback:
        #
        # Example:
        #
        # {'Audio Category': {
        #       'Speaker Type': 'Bluetooth Speaker'
        # }}
        #
        # Whatever the inner key is, use its value.
        # -------------------------------------------------

        if inner:

            for key, value in inner.items():

                if value is None:
                    continue

                # Ignore nested dictionaries
                if isinstance(value, dict):
                    continue

                value = str(value).strip()

                if value:

                    return (
                        normalized_category,
                        value
                    )


    # -----------------------------------------------------
    # 3. GENERIC CATEGORY FALLBACK
    # -----------------------------------------------------
    #
    # This handles categories such as:
    #
    # Audio Category
    # etc.
    #
    # even if they were not explicitly added above.
    #
    # -----------------------------------------------------

    for source_category, inner in data.items():

        if not isinstance(inner, dict):
            continue

        if source_category in CATEGORY_MAPPING:

            normalized_category = CATEGORY_MAPPING[
                source_category
            ]

            for key, value in inner.items():

                if value is None:
                    continue

                if isinstance(value, dict):
                    continue

                value = str(value).strip()

                if value:
                    return (
                        normalized_category,
                        value
                    )


    # Nothing found
    return None, None


# =========================================================
# ACCESSORIES OVERRIDE
# =========================================================

def extract_accessories(text):
    """
    Find Accessories anywhere inside specification.

    Example:

    'In The Box': {
        ...
        'Accessories': 'USB Cable'
    }

    -> USB Cable
    """

    data = parse_specification(text)

    if not data:
        return None

    def recursive_search(obj):

        if isinstance(obj, dict):

            if "Accessories" in obj:

                value = obj["Accessories"]

                if value is not None:

                    value = str(value).strip()

                    if value:
                        return value

            for value in obj.values():

                result = recursive_search(value)

                if result:
                    return result

        elif isinstance(obj, list):

            for item in obj:

                result = recursive_search(item)

                if result:
                    return result

        return None

    return recursive_search(data)


# =========================================================
# MAIN
# =========================================================

def main():

    df = pd.read_csv(INPUT_FILE)

    print("=" * 80)
    print("PRODUCT CATEGORY EXTRACTION")
    print("=" * 80)

    print("\nDataset shape:")
    print(df.shape)


    # =====================================================
    # EXTRACT BRAND
    # =====================================================

    print("\n" + "=" * 80)
    print("BRAND EXTRACTION")
    print("=" * 80)

    df["extracted_brand"] = df["specification"].apply(
        extract_brand
    )

    brand_count = df["extracted_brand"].notna().sum()

    print(
        f"Brands extracted: {brand_count}"
    )


    # =====================================================
    # UPDATE EXISTING BRAND COLUMN
    # =====================================================

    # Handle either "brand" or "Brand"

    if "brand" in df.columns:

        df["brand"] = df["extracted_brand"].combine_first(
            df["brand"]
        )

    elif "Brand" in df.columns:

        df["Brand"] = df["extracted_brand"].combine_first(
            df["Brand"]
        )

    else:

        # If no brand column exists, create one.
        df["brand"] = df["extracted_brand"]


    # =====================================================
    # EXTRACT CATEGORY + PRODUCT TYPE
    # =====================================================

    extracted = df["specification"].apply(
        extract_product_category
    )

    df["extracted_category"] = extracted.apply(
        lambda x: x[0]
    )

    df["extracted_product_type"] = extracted.apply(
        lambda x: x[1]
    )


    # =====================================================
    # ACCESSORIES OVERRIDE
    # =====================================================

    df["extracted_accessories"] = df[
        "specification"
    ].apply(
        extract_accessories
    )

    accessories_mask = (
        df["extracted_accessories"].notna()
    )

    df.loc[
        accessories_mask,
        "extracted_product_type"
    ] = df.loc[
        accessories_mask,
        "extracted_accessories"
    ]

    print(
        f"\nAccessories overrides: "
        f"{accessories_mask.sum()}"
    )


    # =====================================================
    # CATEGORY COUNT
    # =====================================================

    print("\n" + "=" * 80)
    print("CATEGORY COUNTS")
    print("=" * 80)

    category_counts = (
        df["extracted_category"]
        .dropna()
        .value_counts()
    )

    for category, count in category_counts.items():

        print(
            f"{count:6} | {category}"
        )


    # =====================================================
    # PRODUCT TYPE COUNT
    # =====================================================

    print("\n" + "=" * 80)
    print("EXTRACTED PRODUCT TYPE COUNTS")
    print("=" * 80)

    value_counts = (
        df["extracted_product_type"]
        .dropna()
        .value_counts()
    )

    for value, count in value_counts.items():

        print(
            f"{count:6} | {value}"
        )


    # =====================================================
    # CATEGORY + PRODUCT TYPE
    # =====================================================

    print("\n" + "=" * 80)
    print("CATEGORY + PRODUCT TYPE COUNTS")
    print("=" * 80)

    category_value_counts = (
        df[
            df["extracted_category"].notna()
            & df["extracted_product_type"].notna()
        ]
        .groupby(
            [
                "extracted_category",
                "extracted_product_type"
            ]
        )
        .size()
        .sort_values(ascending=False)
    )

    for (category, value), count in category_value_counts.items():

        print(
            f"{count:6} | "
            f"{category:30} | "
            f"{value}"
        )


    # =====================================================
    # EXAMPLES
    # =====================================================

    print("\n" + "=" * 80)
    print("EXAMPLES")
    print("=" * 80)

    examples = (
        df[
            df["extracted_product_type"].notna()
        ][
            [
                "extracted_category",
                "extracted_product_type",
                "extracted_brand",
                "specification"
            ]
        ]
        .drop_duplicates(
            subset=[
                "extracted_category",
                "extracted_product_type"
            ]
        )
    )

    for _, row in examples.head(100).iterrows():

        print(
            f"\nCATEGORY : "
            f"{row['extracted_category']}"
        )

        print(
            f"TYPE     : "
            f"{row['extracted_product_type']}"
        )

        print(
            f"BRAND    : "
            f"{row['extracted_brand']}"
        )

        print(
            f"RAW      : "
            f"{row['specification']}"
        )


    # =====================================================
    # SAVE
    # =====================================================

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n" + "=" * 80)
    print(
        f"Output saved to: {OUTPUT_FILE}"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()