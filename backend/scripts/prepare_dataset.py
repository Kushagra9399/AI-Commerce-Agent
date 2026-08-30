import pandas as pd
import random
import uuid


INPUT_FILE = "scripts/data/croma_products_final.csv"
OUTPUT_FILE = "scripts/data/croma_products_enriched.csv"

MERCHANT_ID = "CROMA_DEMO"


def generate_pricing(market_price: float):
    discount_percent = round(random.uniform(0, 20), 2)

    sale_price = market_price * (
        1 - discount_percent / 100
    )

    return discount_percent, round(sale_price, 2)


def extract_brand(name):
    if not isinstance(name, str):
        return "Other"

    known_brands = [
        "Samsung",
        "OnePlus",
        "Panasonic",
        "Lenovo",
        "Hisense",
        "Xiaomi",
        "Haier",
        "Philips",
        "Honeywell",
        "DeLonghi",
        "Oppo",
        "Realme",
        "Apple",
        "Egate",
        "Toshiba",
        "Kuber Industries",
        "Sun King",
        "Novita",
        "Racold",
        "Atomberg",
        "BenQ",
        "Wipro",
        "Agnisolar",
        "Anker",
        "Sennheiser",
        "Hitachi",
        "Portronics",
        "Skullcandy",
        "Blaupunkt",
        "Borosil",
        "Halonix",
        "RD Plast",
        "Amazon",
        "Oakter",
        "Airtel",
        "Mobvoi",
        "Merlin",
        "Sensy",
        "Huawei",
        "Mighty",
        "SunKing",
        "Alta Tecnologia",
        "Environics",
        "Whirlpool",
        "Black & Decker",
        "Symphony",
        "Urbanears",
        "Bang & Olufsen",
        "Lumiford",
        "Vanguard",
        "EurekaForbes",
        "Lloyd",
        "Stuffcool",
        "Leather Talks",
        "Cosmic Byte",
        "Miracle Digital",
        "Voltas",
        "ViewSonic",
        "Coway",
        "Siemens",
        "Milagrow",
        "Morphy Richards",
        "Liebherr",
        "Soundlogic",
        "Bosch",
        "iRobot",
        "Bajaj",
        "Blue Star",
        "Kenstar",
        "Havells",
        "Kingston",
        "Cisco",
        "Fujifilm",
        "Oakter",
        "Seagate",
        "Redmi",
        "Adidas",
        "Nokia",
        "Crossbeats",
        "Jabra",
        "Benro",
        "Anchor",
        "A.O. Smith",
        "Sunflame",
        "Fire-Boltt",
        "Eureka Forbes",
        "Daikin",
        "Belkin",
        "Prolink",
        "Ambrane",
        "Syska",
        "Blueair",
        "Profoto",
        "Preethi",
        "Harman Kardon",
        "PowerMax",
        "Onsitego",
        "Nikon",
        "Natraj",
        "Motorola",
        "Lowepro",
        "Linksys",
        "Manfrotto",
        "Ultraprolink",
        "Aquaguard",
        "Amkette",
        "Popsocket",
        "Infinity",
        "Jaipan",
        "O General"
        "Beurer",
        "Babyliss",
        "Godrej",
        "Hindware",
        "Globalkart",
        "Bergmann",
        "Catz",
        "Case-Mate",
        "Tropicool",
        "Soundmagic",
        "Resideo",
        "Xech",
        "Peng Essentials",
        "Vaku Luxos",
        "NuvoMed",
        "Crompton",
        "Safestab",
        "SINGER ",
        "Acer",
        "SanDisk",
        "Google",
        "Dyson",
        "XGIMI",
        "Viomi",
        "Elofic",
        "Orient",
        "Faber",
        "Vertel",
        "Trifo",
        "Karcher",
        "Fossil",
        "Amazfit",
        "Hyphen",
        "Fitbit",
        "Scratchgard",
        "Timex",
        "Inbase",
        "Itek",
        "Crossloop",
        "Skyvik",
        "Balzano",
        "Cygnett",
        "Eurodomo",
        "Equator",
        "Butterfly",
        "RoadGods",
        "Robobull",
        "Targus",
        "Nextech",
        "Marshall",
        "Duracell",
        "Plantronics",
        "Fuse Chicken",
        "Boompods",
        "Brother",
        "AfterShokz",
        "Tucano",
        "Storme",
        "Skybags",
        "Shifu",
        "Western Digital",
        "Mr. Beams",
        "Kaiterra",
        "WatchOut",
        "Agni Solar",
        "Tucano",
        "Saregama",
        "Saramonic",
        "Travel Blue",
        "The Souled Store",
        "Sabichi",
        "Eaton",
        "Juvo",
        "tag8",
        "Tenda",
        "Wahl",
        "Asus",
        "Origin",
        "Dell",
        "KitchenAid",
        "Croma",
        "Sony",
        "Ubisoft"
        "iGear",
        "iBall",
        "V-Guard",
        "Zopper",
        "Xiomi",
        "Glen",
        "Alogic",
        "Qubo",
        "Vivo",
        "Usha",
        "D-Link",
        "Yale",
        "Bose",
        "Vego",
        "Vega",
        "Redgear",
        "Rapoo",
        "R for Rabbit",
        "Quick Heal",
        "boAt",
        "Pureit",
        "House of Marley",
        "Hamilton Beach",
        "Sharp",
        "ILIFE",
        "Neopack",
        "Thermaltake",
        "Logitech",
        "Canon",
        "Resonate",
        "Eleon",
        "EUME",
        "GoPro",
        "Go Pro",
        "GOQii",
        "GODOX",
        "Wonderchef",
        "Hoya",
        "Elica",
        "Pigeon",
        "Venus",
        "Grob",
        "Eufy",
        "TCL",
        "IFB",
        "JBL",
        "LG",
        "DMR",
        "RNG",
        "UAG",
        "NKD",
        "APC",
        "AKG",
        "RHA",
        "HP",
        "Vu ",
        "GM ",
        "Lifelong",
        "Mi",
        "Noise",
        "360"
    ]

    name_lower = name.lower().strip()

    for brand in known_brands:
        if name_lower.startswith(brand.lower()):
            return brand

    return "Other"


def create_search_text(row):
    parts = [
        str(row["name"]),
        str(row["category"]),
        str(row["overview"]),
        str(row["specification"]),
    ]

    # Remove missing-value strings
    parts = [
        part for part in parts
        if part and part.lower() != "nan"
    ]

    return " ".join(parts)


def main():

    # --------------------------------------------------
    # 1. Load dataset
    # --------------------------------------------------

    df = pd.read_csv(INPUT_FILE)

    print("Original shape:", df.shape)

    # --------------------------------------------------
    # 2. Clean column names
    # --------------------------------------------------

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
    )

    print("Columns:", df.columns.tolist())

    # --------------------------------------------------
    # 3. Rename columns
    # --------------------------------------------------

    df = df.rename(columns={
        "unnamed: 0": "source_id"
    })

    # --------------------------------------------------
    # 4. Clean price
    # --------------------------------------------------

    df["market_price"] = (
        df["price"]
        .astype(str)
        .str.replace("₹", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )

    df["market_price"] = pd.to_numeric(
        df["market_price"],
        errors="coerce"
    )

    # --------------------------------------------------
    # 5. Remove invalid products
    # --------------------------------------------------

    df = df.dropna(
        subset=["name", "category", "market_price"]
    )

    df = df[
        df["market_price"] > 0
    ]

    # --------------------------------------------------
    # 6. Generate product ID
    # --------------------------------------------------

    df["product_id"] = [
        str(uuid.uuid4())
        for _ in range(len(df))
    ]

    # --------------------------------------------------
    # 7. Merchant
    # --------------------------------------------------

    df["merchant_id"] = MERCHANT_ID

    # --------------------------------------------------
    # 8. Generate discount + sale price
    # --------------------------------------------------

    pricing = df["market_price"].apply(
        generate_pricing
    )

    df["discount_percent"] = pricing.apply(
        lambda x: x[0]
    )

    df["sale_price"] = pricing.apply(
        lambda x: x[1]
    )

    # --------------------------------------------------
    # 9. Generate stock
    # --------------------------------------------------

    df["stock"] = [
        random.randint(0, 20)
        for _ in range(len(df))
    ]

    df["is_active"] = df["stock"] > 0

    # --------------------------------------------------
    # 10. Extract brand
    # --------------------------------------------------

    df["brand"] = df["name"].apply(
        extract_brand
    )

    # --------------------------------------------------
    # 11. Create searchable text
    # --------------------------------------------------

    df["search_text"] = df.apply(
        create_search_text,
        axis=1
    )

    # --------------------------------------------------
    # 12. Select final columns
    # --------------------------------------------------

    df = df[
        [
            "product_id",
            "merchant_id",
            "source_id",
            "link",
            "name",
            "brand",
            "category",
            "overview",
            "images",
            "specification",
            "search_text",
            "market_price",
            "discount_percent",
            "sale_price",
            "stock",
            "is_active",
        ]
    ]

    # --------------------------------------------------
    # 13. Save
    # --------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------------------------
    # 14. Summary
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("ENRICHED DATASET")
    print("=" * 60)

    print("Shape:", df.shape)

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nDuplicate product IDs:")
    print(df["product_id"].duplicated().sum())

    print("\nUnique brands:")
    print(df["brand"].nunique())

    print("\nBrands:")
    print(df["brand"].value_counts().head(20))

    print("\nUnique categories:")
    print(df["category"].nunique())

    print("\nDiscount range:")
    print(
        df["discount_percent"].min(),
        "to",
        df["discount_percent"].max()
    )

    print("\nStock range:")
    print(
        df["stock"].min(),
        "to",
        df["stock"].max()
    )

    print("\nOut of stock:")
    print(
        (df["stock"] == 0).sum()
    )

    print("\nSample:")
    print(
        df[
            [
                "product_id",
                "name",
                "brand",
                "market_price",
                "discount_percent",
                "sale_price",
                "stock",
                "is_active",
            ]
        ].head()
    )


if __name__ == "__main__":
    main()