import re
import ast
import pandas as pd


# =========================================================
# FILES
# =========================================================

INPUT_FILE = (
    "scripts/data/croma_products_category_extracted.csv"
)

OUTPUT_FILE = (
    "scripts/data/croma_products_category_refined.csv"
)


# =========================================================
# PARSE SPECIFICATION
# =========================================================

def parse_specification(text):

    if pd.isna(text):
        return None

    try:

        data = ast.literal_eval(
            str(text).strip()
        )

        if isinstance(data, dict):
            return data

    except Exception:
        pass

    return None


# =========================================================
# CLEAN VALUE
# =========================================================

def clean_value(value):

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    return value


# =========================================================
# PRODUCT NAME CLASSIFICATION
# =========================================================

PRODUCT_NAME_RULES = [

    # -----------------------------------------------------
    # COFFEE
    # -----------------------------------------------------

    (
        "Coffee Machines",
        [
            "coffee maker",
            "coffee machine",
            "espresso machine",
            "espresso maker",
            "cappuccino maker",
            "coffee grinder",
            "coffee brewer",
        ]
    ),

    # -----------------------------------------------------
    # LIGHTING
    # -----------------------------------------------------

    (
        "Lighting",
        [
            "led bulb",
            "led light",
            "emergency bulb",
            "emergency light",
            "ceiling light",
            "wall light",
            "step light",
            "stair light",
            "spot light",
            "spotlight",
            "night light",
            "smart light",
            "led lamp",
            "lamp",
        ]
    ),

    # -----------------------------------------------------
    # WEARABLES
    # -----------------------------------------------------

    (
        "Wearables",
        [
            "smart watch",
            "smartwatch",
            "fitness tracker",
            "fitness band",
            "smart band",
            "apple watch",
            "watch strap",
            "watch band",
        ]
    ),

    # -----------------------------------------------------
    # AUDIO
    # -----------------------------------------------------

    (
        "Audio Devices",
        [
            "headphone",
            "headphones",
            "earphone",
            "earphones",
            "earbud",
            "earbuds",
            "wireless headphone",
            "wireless earphone",
            "bluetooth headphone",
            "bluetooth earphone",
            "headset",
            "handsfree",
            "airpods",
            "soundbar",
            "sound bar",
        ]
    ),

    # -----------------------------------------------------
    # PERSONAL GROOMING
    # -----------------------------------------------------

    (
        "Personal Grooming",
        [
            "hair straightener",
            "hair straightening",
            "hair dryer",
            "hair trimmer",
            "beard trimmer",
            "body trimmer",
            "nose trimmer",
            "trimmer",
            "shaver",
            "epilator",
            "hair curler",
            "curling iron",
        ]
    ),

    # -----------------------------------------------------
    # KITCHEN APPLIANCES
    # -----------------------------------------------------

    (
        "Kitchen Appliances",
        [
            "juicer",
            "mixer grinder",
            "mixer grinder",
            "hand blender",
            "blender",
            "food processor",
            "chopper",
        ]
    ),

    # -----------------------------------------------------
    # SENSORS
    # -----------------------------------------------------

    (
        "Sensors",
        [
            "motion sensor",
            "pir sensor",
            "door sensor",
            "temperature sensor",
            "sensor",
        ]
    ),

    # -----------------------------------------------------
    # CAMERA
    # -----------------------------------------------------

    (
        "Camera",
        [
            "camera tripod",
            "camera lens",
            "camera remote",
            "camera cover",
            "digital camera",
            "security camera",
            "webcam",
            "camera",
        ]
    ),

    # -----------------------------------------------------
    # MOBILE
    # -----------------------------------------------------

    (
        "Mobile",
        [
            "smartphone",
            "smart phone",
            "mobile phone",
            "mobile",
        ]
    ),

    # -----------------------------------------------------
    # TABLET
    # -----------------------------------------------------

    (
        "Tablet",
        [
            "ipad",
            "tablet",
        ]
    ),

    # -----------------------------------------------------
    # LAPTOP
    # -----------------------------------------------------

    (
        "Laptop",
        [
            "laptop",
            "notebook",
        ]
    ),

    # -----------------------------------------------------
    # PRINTER
    # -----------------------------------------------------

    (
        "Printer",
        [
            "printer",
            "scanner",
        ]
    ),

    # -----------------------------------------------------
    # MONITOR
    # -----------------------------------------------------

    (
        "Monitor",
        [
            "monitor",
            "display monitor",
        ]
    ),

    # -----------------------------------------------------
    # ROUTER
    # -----------------------------------------------------

    (
        "Router",
        [
            "wifi router",
            "wi-fi router",
            "wireless router",
            "router",
        ]
    ),

    # -----------------------------------------------------
    # KETTLE
    # -----------------------------------------------------

    (
        "Kettle",
        [
            "electric kettle",
            "kettle",
        ]
    ),

    # -----------------------------------------------------
    # GEYSER
    # -----------------------------------------------------

    (
        "Geyser",
        [
            "water geyser",
            "instant geyser",
            "storage geyser",
            "geyser",
        ]
    ),

    # -----------------------------------------------------
    # FAN
    # -----------------------------------------------------

    (
        "Fan",
        [
            "ceiling fan",
            "table fan",
            "pedestal fan",
            "wall fan",
            "exhaust fan",
            "fan",
        ]
    ),

    # -----------------------------------------------------
    # DISHWASHER
    # -----------------------------------------------------

    (
        "Dishwasher",
        [
            "dishwasher",
        ]
    ),

    # -----------------------------------------------------
    # CHIMNEY
    # -----------------------------------------------------

    (
        "Chimney",
        [
            "kitchen chimney",
            "chimney",
        ]
    ),

    # -----------------------------------------------------
    # CHARGER
    # -----------------------------------------------------

    (
        "Charger",
        [
            "mobile charger",
            "phone charger",
            "travel adapter",
            "wall charger",
            "fast charger",
            "charger",
        ]
    ),

    # -----------------------------------------------------
    # CABLES
    # -----------------------------------------------------

    (
        "Cables",
        [
            "usb cable",
            "type c cable",
            "type-c cable",
            "hdmi cable",
            "charging cable",
            "data cable",
            "aux cable",
            "cable",
        ]
    ),

    # -----------------------------------------------------
    # POWER BANK
    # -----------------------------------------------------

    (
        "Power Bank",
        [
            "power bank",
            "powerbank",
        ]
    ),

    # -----------------------------------------------------
    # GAMING
    # -----------------------------------------------------

    (
        "Gaming",
        [
            "playstation",
            "ps4",
            "ps5",
            "xbox",
            "gaming console",
            "game console",
        ]
    ),

    # -----------------------------------------------------
    # BACKPACK
    # -----------------------------------------------------

    (
        "Backpack",
        [
            "backpack",
            "laptop backpack",
        ]
    ),
]


def classify_product_name(product_name):

    if not product_name:
        return None

    text = str(product_name).strip().lower()

    # Normalize
    text = re.sub(
        r"[-_/]+",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    for category, keywords in PRODUCT_NAME_RULES:

        for keyword in keywords:

            keyword = keyword.lower()

            keyword = re.sub(
                r"[-_/]+",
                " ",
                keyword
            )

            pattern = (
                r"\b"
                + re.escape(keyword)
                + r"\b"
            )

            if re.search(
                pattern,
                text
            ):
                return category

    return None

    
# =========================================================
# PRODUCT CATEGORY SECTION
# =========================================================

def get_product_category_section(data):

    if not isinstance(data, dict):
        return None

    section = data.get(
        "Product Category"
    )

    if isinstance(section, dict):
        return section

    return None


# =========================================================
# DEVICE TYPE -> CATEGORY
# =========================================================

def classify_device_type(value):

    if not value:
        return None

    value_lower = value.lower().strip()


    # -----------------------------------------------------
    # Audio devices
    # -----------------------------------------------------

    audio_keywords = [
        "earphone",
        "earphones",
        "earbud",
        "earbuds",
        "headphone",
        "headphones",
        "headset",
        "handsfree",
        "in-ear",
        "truly wireless",
        "wireless earphone",
        "wireless headphone",
        "tws",
    ]

    for keyword in audio_keywords:

        if keyword in value_lower:
            return "Audio Devices"


    # -----------------------------------------------------
    # Cooker
    # -----------------------------------------------------

    cooker_keywords = [
        "cooker",
        "rice cooker",
    ]

    for keyword in cooker_keywords:

        if keyword in value_lower:
            return "Cooker"


    # -----------------------------------------------------
    # Burner / Cooktop
    # -----------------------------------------------------

    burner_keywords = [
        "cooking range",
        "gas hob",
        "burner",
    ]

    for keyword in burner_keywords:

        if keyword in value_lower:
            return "Burner/Cooktop"


    # -----------------------------------------------------
    # Gas Stove
    # -----------------------------------------------------

    if "gas stove" in value_lower:
        return "Gas Stove"


    # -----------------------------------------------------
    # Electric Cooktop
    # -----------------------------------------------------

    if "electric cooktop" in value_lower:
        return "Electric Cooktop"


    # -----------------------------------------------------
    # Egg Boiler
    # -----------------------------------------------------

    if "egg boiler" in value_lower:
        return "Egg Boiler"


    # -----------------------------------------------------
    # Food Steamer
    # -----------------------------------------------------

    if "food steamer" in value_lower:
        return "Food Steamer"


    # -----------------------------------------------------
    # Printer
    # -----------------------------------------------------

    printer_keywords = [
        "all-in-one",
        "printer",
        "scanner",
    ]

    for keyword in printer_keywords:

        if keyword in value_lower:
            return "Printer"


    # -----------------------------------------------------
    # DVD
    # -----------------------------------------------------

    dvd_keywords = [
        "dvr",
        "nvr",
        "dvd",
    ]

    for keyword in dvd_keywords:

        if keyword in value_lower:
            return "DVD"


    # -----------------------------------------------------
    # Door Bell
    # -----------------------------------------------------

    if (
        "door bell" in value_lower
        or "doorbell" in value_lower
    ):
        return "Door Bell"


    # -----------------------------------------------------
    # Media Streaming
    # -----------------------------------------------------

    streaming_keywords = [
        "media streaming stick",
        "streaming stick",
        "streaming device",
    ]

    for keyword in streaming_keywords:

        if keyword in value_lower:
            return "Media Streaming"


    # -----------------------------------------------------
    # Sensors
    # -----------------------------------------------------

    sensor_keywords = [
        "pir sensor",
        "pir sensors",
        "sensor",
        "sensors",
    ]

    for keyword in sensor_keywords:

        if keyword in value_lower:
            return "Sensors"


    # -----------------------------------------------------
    # Safety
    # -----------------------------------------------------

    safety_keywords = [
        "personal safety alarm",
        "safety locker",
        "safety lockers",
        "security camera",
        "smart home device",
        "smart lock",
        "smart locks",
        "tracker",
    ]

    for keyword in safety_keywords:

        if keyword in value_lower:
            return "Safety & Security"


    # -----------------------------------------------------
    # Set Top Box
    # -----------------------------------------------------

    if (
        "set top box" in value_lower
        or "set-top box" in value_lower
    ):
        return "Set Top Box"


    return None


# =========================================================
# PRODUCT CATEGORY VALUE -> CATEGORY
# =========================================================

def classify_product_category(value):

    if not value:
        return None

    value_lower = value.lower().strip()


    # -----------------------------------------------------
    # Battery
    # -----------------------------------------------------

    if value_lower == "battery":
        return "Battery"


    # -----------------------------------------------------
    # Camera
    # -----------------------------------------------------

    camera_keywords = [
        "camera cover",
        "camera remote",
        "fill light",
        "flash light",
        "lens",
        "lens filter",
        "mic",
        "monopod",
        "mounting kit",
        "selfie stick",
        "tripod",
    ]

    for keyword in camera_keywords:

        if keyword in value_lower:
            return "Camera"


    # -----------------------------------------------------
    # Charger
    # -----------------------------------------------------

    charger_keywords = [
        "charger",
        "travel adapter",
    ]

    for keyword in charger_keywords:

        if keyword in value_lower:
            return "Charger"


    # -----------------------------------------------------
    # Protection
    # -----------------------------------------------------

    if "screen protector" in value_lower:
        return "Protection"


    # -----------------------------------------------------
    # MCB
    # -----------------------------------------------------

    if "power tools" in value_lower:
        return "MCB"


    # -----------------------------------------------------
    # Case / Cover
    # -----------------------------------------------------

    if "back case" in value_lower:
        return "Case/Cover"


    # -----------------------------------------------------
    # Backpack
    # -----------------------------------------------------

    if "backpack" in value_lower:
        return "Backpack"


    # -----------------------------------------------------
    # Chips
    # -----------------------------------------------------

    if "anti radiation chip" in value_lower:
        return "Chips"


    # -----------------------------------------------------
    # Power Protection
    # -----------------------------------------------------

    if (
        "spike guard" in value_lower
        or "surge protector" in value_lower
    ):
        return "Power Protection"


    # -----------------------------------------------------
    # Transmitter
    # -----------------------------------------------------

    if "transmitter" in value_lower:
        return "Transmitter"


    return None


# =========================================================
# PRODUCT FUNCTIONS -> CATEGORY
# =========================================================

def classify_product_function(value):

    if not value:
        return None

    value_lower = value.lower().strip()


    # -----------------------------------------------------
    # Media Streaming
    # -----------------------------------------------------

    if (
        "audio & video" in value_lower
        or value_lower == "audio"
    ):
        return "Media Streaming"


    # -----------------------------------------------------
    # Cables
    # -----------------------------------------------------

    if (
        "converter" in value_lower
        or "data transfer" in value_lower
    ):
        return "Cables"


    # -----------------------------------------------------
    # Charger
    # -----------------------------------------------------

    if (
        "power/charging" in value_lower
        or "power charging" in value_lower
    ):
        return "Charger"


    return None


# =========================================================
# GENERIC PRODUCT TYPE CLASSIFICATION
# =========================================================

def classify_product_type(value):

    if not value:
        return None

    value_lower = value.lower().strip()


    # -----------------------------------------------------
    # Audio
    # -----------------------------------------------------

    audio_keywords = [
        "earphone",
        "earphones",
        "earbud",
        "earbuds",
        "headphone",
        "headphones",
        "headset",
        "handsfree",
        "in-ear",
        "tws",
        "truly wireless",
        "wireless earphone",
        "wireless headphone",
    ]

    for keyword in audio_keywords:

        if keyword in value_lower:
            return "Audio Devices"


    # -----------------------------------------------------
    # Camera
    # -----------------------------------------------------

    camera_keywords = [
        "camera",
        "lens",
        "tripod",
        "monopod",
        "selfie stick",
        "camera remote",
        "camera cover",
    ]

    for keyword in camera_keywords:

        if keyword in value_lower:
            return "Camera"


    # -----------------------------------------------------
    # Charger
    # -----------------------------------------------------

    charger_keywords = [
        "charger",
        "travel adapter",
        "power adapter",
    ]

    for keyword in charger_keywords:

        if keyword in value_lower:
            return "Charger"


    # -----------------------------------------------------
    # Cables
    # -----------------------------------------------------

    cable_keywords = [
        "cable",
        "converter",
        "data transfer",
    ]

    for keyword in cable_keywords:

        if keyword in value_lower:
            return "Cables"


    # -----------------------------------------------------
    # Gaming
    # -----------------------------------------------------

    gaming_keywords = [
        "playstation",
        "ps4",
        "ps5",
        "xbox",
        "gaming",
        "console",
    ]

    for keyword in gaming_keywords:

        if keyword in value_lower:
            return "Gaming"


    # -----------------------------------------------------
    # Protection
    # -----------------------------------------------------

    if (
        "protector" in value_lower
        or "protection" in value_lower
    ):
        return "Protection"


    # -----------------------------------------------------
    # Case / Cover
    # -----------------------------------------------------

    if (
        "case" in value_lower
        or "cover" in value_lower
    ):
        return "Case/Cover"


    # -----------------------------------------------------
    # Power Protection
    # -----------------------------------------------------

    if (
        "spike guard" in value_lower
        or "surge protector" in value_lower
    ):
        return "Power Protection"


    # -----------------------------------------------------
    # Safety
    # -----------------------------------------------------

    safety_keywords = [
        "safety",
        "security",
        "tracker",
        "alarm",
        "smart lock",
    ]

    for keyword in safety_keywords:

        if keyword in value_lower:
            return "Safety & Security"


    # -----------------------------------------------------
    # Power Bank
    # -----------------------------------------------------

    if "power bank" in value_lower:
        return "Power Bank"


    # -----------------------------------------------------
    # Kettle
    # -----------------------------------------------------

    if "kettle" in value_lower:
        return "Kettle"


    # -----------------------------------------------------
    # Geyser
    # -----------------------------------------------------

    if "geyser" in value_lower:
        return "Geyser"


    # -----------------------------------------------------
    # Fan
    # -----------------------------------------------------

    if "fan" in value_lower:
        return "Fan"


    # -----------------------------------------------------
    # Dishwasher
    # -----------------------------------------------------

    if "dishwasher" in value_lower:
        return "Dishwasher"


    # -----------------------------------------------------
    # Monitor
    # -----------------------------------------------------

    if "monitor" in value_lower:
        return "Monitor"


    # -----------------------------------------------------
    # Router
    # -----------------------------------------------------

    if "router" in value_lower:
        return "Router"


    # -----------------------------------------------------
    # Backpack
    # -----------------------------------------------------

    if "backpack" in value_lower:
        return "Backpack"


    # -----------------------------------------------------
    # Chips
    # -----------------------------------------------------

    if "chip" in value_lower:
        return "Chips"


    return None


# =========================================================
# REFINE PRODUCT ROW
# =========================================================

def refine_product_row(text):

    data = parse_specification(text)

    if not data:

        return "Others", None


    product = get_product_category_section(
        data
    )

    if not product:

        return "Others", None


    # =====================================================
    # 1. CAPACITY -> GEYSER
    # =====================================================

    capacity = clean_value(
        product.get("Capacity")
    )

    if capacity:

        if re.search(
            r"\b\d+(?:\.\d+)?\s*(?:litres?|l)\b",
            capacity,
            re.IGNORECASE
        ):

            return (
                "Geyser",
                capacity
            )


    # =====================================================
    # 2. CHIMNEY SIZE -> CHIMNEY
    # =====================================================

    chimney_size = clean_value(
        product.get("Chimney Size")
    )

    if chimney_size:

        return (
            "Chimney",
            chimney_size
        )


    # =====================================================
    # 3. COMPATIBLE BRAND -> CASE/COVER
    # =====================================================

    compatible_brand = clean_value(
        product.get("Compatible Brand")
    )

    if compatible_brand:

        return (
            "Case/Cover",
            compatible_brand
        )


    # =====================================================
    # 4. COMPATIBLE WITH -> MEMORY CARD
    # =====================================================

    compatible_with = clean_value(
        product.get("Compatible With")
    )

    if compatible_with:

        return (
            "Memory Card",
            compatible_with
        )


    # =====================================================
    # 5. CONSOLE CATEGORY -> GAMING
    # =====================================================

    console = clean_value(
        product.get("Console Category")
    )

    if console:

        return (
            "Gaming",
            console
        )


    # =====================================================
    # 6. DEVICE ORIENTATION -> AUDIO DEVICES
    # =====================================================

    orientation = clean_value(
        product.get("Device Orientation")
    )

    if orientation:

        if "in-ear" in orientation.lower():

            return (
                "Audio Devices",
                orientation
            )


    # =====================================================
    # 7-35. DEVICE TYPE
    # =====================================================

    device_type = clean_value(
        product.get("Device Type")
    )

    if device_type:

        category = classify_device_type(
            device_type
        )

        if category:

            return (
                category,
                device_type
            )


    # =====================================================
    # 36-38. OTHER TYPE FIELDS
    # =====================================================

    dishwasher_type = clean_value(
        product.get("Dishwasher Type")
    )

    if dishwasher_type:

        return (
            "Dishwasher",
            dishwasher_type
        )


    fan_type = clean_value(
        product.get("Fan Type")
    )

    if fan_type:

        return (
            "Fan",
            fan_type
        )


    geyser_type = clean_value(
        product.get("Geyser Type")
    )

    if geyser_type:

        return (
            "Geyser",
            geyser_type
        )


    # =====================================================
    # 39. IDEAL FOR
    # =====================================================

    ideal_for = clean_value(
        product.get("Ideal For")
    )

    if ideal_for:

        if "mobile" in ideal_for.lower():

            return (
                "Case/Cover",
                ideal_for
            )


    # =====================================================
    # 40. INSTALLATION TYPE
    # =====================================================

    installation_type = clean_value(
        product.get("Installation Type")
    )

    if installation_type:

        return (
            "Printer",
            installation_type
        )


    # =====================================================
    # 41. KETTLE CAPACITY
    # =====================================================

    kettle_capacity = clean_value(
        product.get("Kettle Capacity")
    )

    if kettle_capacity:

        return (
            "Kettle",
            kettle_capacity
        )


    # =====================================================
    # 42. LIFESTYLE
    # =====================================================

    lifestyle = clean_value(
        product.get("Lifestyle")
    )

    if lifestyle:

        if "entertainment" in lifestyle.lower():

            return (
                "Audio Devices",
                lifestyle
            )


    # =====================================================
    # 43. MONITOR TYPE
    # =====================================================

    monitor_type = clean_value(
        product.get("Monitor Type")
    )

    if monitor_type:

        return (
            "Monitor",
            monitor_type
        )


    # =====================================================
    # 44. NETWORK DEVICE TYPE
    # =====================================================

    network_type = clean_value(
        product.get("Network Device Type")
    )

    if network_type:

        return (
            "Router",
            network_type
        )


    # =====================================================
    # 45. OPERATION TYPE
    # =====================================================

    operation_type = clean_value(
        product.get("Operation Type")
    )

    if operation_type:

        return (
            "Geyser",
            operation_type
        )


    # =====================================================
    # 46. PLATFORM
    # =====================================================

    platform = clean_value(
        product.get("Platform")
    )

    if platform:

        platform_lower = platform.lower()

        gaming_keywords = [
            "pc",
            "ps4",
            "ps5",
            "playstation",
            "xbox",
        ]

        for keyword in gaming_keywords:

            if keyword in platform_lower:

                return (
                    "Gaming",
                    platform
                )


    # =====================================================
    # 47-56. PRODUCT CATEGORY VALUE
    # =====================================================

    product_category_value = clean_value(
        product.get("Product Category")
    )

    if product_category_value:

        category = classify_product_category(
            product_category_value
        )

        if category:

            return (
                category,
                product_category_value
            )


    # =====================================================
    # 57. TRAVEL ADAPTER
    # =====================================================

    # Already handled through Product Category
    # classification above.


    # =====================================================
    # 59-63. PRODUCT FUNCTIONS
    # =====================================================

    product_functions = clean_value(
        product.get("Product Functions")
    )

    if product_functions:

        category = classify_product_function(
            product_functions
        )

        if category:

            return (
                category,
                product_functions
            )


    # =====================================================
    # 64-66. PRODUCT TYPE
    # =====================================================

    product_type = clean_value(
        product.get("Product Type")
    )

    if product_type:

        category = classify_product_type(
            product_type
        )

        if category:

            return (
                category,
                product_type
            )

        # Important:
        # Product Type exists but we don't know how to
        # classify it.
        return (
            "Others",
            product_type
        )


    # =====================================================
    # NO PRODUCT TYPE
    # =====================================================

    return (
        "Others",
        None
    )


# =========================================================
# MAIN
# =========================================================

def main():

    df = pd.read_csv(
        INPUT_FILE
    )

    print("=" * 80)
    print("REFINING PRODUCT CATEGORY ROWS")
    print("=" * 80)

    print(
        "\nInput shape:",
        df.shape
    )


    # =====================================================
    # CHECK REQUIRED COLUMNS
    # =====================================================

    required_columns = [
        "specification",
        "extracted_category",
        "extracted_product_type",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Missing columns: {missing}"
        )


    # =====================================================
    # ONLY PRODUCT ROWS
    # =====================================================

    product_mask = (
        df["extracted_category"]
        .astype(str)
        .str.strip()
        .str.lower()
        == "product"
    )

    print(
        "\nRows with extracted_category = Product:",
        product_mask.sum()
    )


    # =====================================================
    # APPLY ONLY TO PRODUCT ROWS
    # =====================================================

    refined = df.loc[
        product_mask,
        "specification"
    ].apply(
        refine_product_row
    )


    # =====================================================
    # UPDATE ONLY THOSE ROWS
    # =====================================================

    df.loc[
        product_mask,
        "extracted_category"
    ] = refined.apply(
        lambda x: x[0]
    )

    df.loc[
        product_mask,
        "extracted_product_type"
    ] = refined.apply(
        lambda x: x[1]
    )


    # =====================================================
    # SHOW HOW MANY CHANGED
    # =====================================================

    print("\n" + "=" * 80)
    print("RESULT")
    print("=" * 80)

    remaining_product = (
        (
            df["extracted_category"]
            .astype(str)
            .str.strip()
            .str.lower()
            == "product"
        )
        .sum()
    )

    print(
        "Remaining Product rows:",
        remaining_product
    )


    # =====================================================
    # CATEGORY COUNTS
    # =====================================================

    print("\n" + "=" * 80)
    print("REFINED CATEGORY COUNTS")
    print("=" * 80)

    category_counts = (
        df["extracted_category"]
        .value_counts()
    )

    for category, count in category_counts.items():

        print(
            f"{count:6} | {category}"
        )


    # =====================================================
    # PRODUCT ROW EXAMPLES
    # =====================================================

    print("\n" + "=" * 80)
    print("REFINED EXAMPLES")
    print("=" * 80)

    examples = df.loc[
        product_mask,
        [
            "extracted_category",
            "extracted_product_type",
            "specification",
        ]
    ].head(100)


    for _, row in examples.iterrows():

        print(
            f"\nCATEGORY : "
            f"{row['extracted_category']}"
        )

        print(
            f"TYPE     : "
            f"{row['extracted_product_type']}"
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