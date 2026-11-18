import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

BASE_URL = (
    "https://ec.europa.eu/eurostat/api/"
    "dissemination/statistics/1.0/data/"
)

REGIONS = {
    "EL53": "Western Macedonia",
    "EL65": "Peloponnese"
}

OUTPUT = Path("data/regional_data.csv")


def download_dataset(dataset, params, indicator, unit):

    print(f"\nDownloading {dataset}...")

    query = [
        ("lang", "en")
    ]

    for key, value in params.items():

        if isinstance(value, list):
            for item in value:
                query.append((key, item))
        else:
            query.append((key, value))

    response = requests.get(
        BASE_URL + dataset,
        params=query,
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    dimensions = data["id"]
    sizes = data["size"]

    categories = {}

    for dimension in dimensions:

        index = data["dimension"][dimension]["category"]["index"]

        if isinstance(index, dict):
            categories[dimension] = sorted(
                index,
                key=index.get
            )
        else:
            categories[dimension] = index

    values = data.get("value", {})
    flags = data.get("status", {})

    if isinstance(values, list):
        observations = enumerate(values)
    else:
        observations = values.items()

    rows = []

    for flat_index, value in observations:

        if value is None:
            continue

        remainder = int(flat_index)
        coordinates = []

        for size in reversed(sizes):
            coordinates.append(remainder % size)
            remainder //= size

        coordinates.reverse()

        observation = {
            dimensions[i]: categories[dimensions[i]][coordinates[i]]
            for i in range(len(dimensions))
        }

        geo = observation.get("geo", "")

        rows.append({

            "year": observation.get("time", ""),

            "region_code": geo,

            "region": REGIONS.get(geo, geo),

            "indicator": indicator,

            "value": value,

            "unit": unit,

            "source": "Eurostat",

            "dataset": dataset,

            "source_url": (
                f"https://ec.europa.eu/eurostat/"
                f"databrowser/view/{dataset}/default/table"
            ),

            "retrieved_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "data_flag": (
                flags.get(str(flat_index), "")
                if isinstance(flags, dict)
                else ""
            ),

            "dimensions": str(observation)

        })

    print(f"Observations retrieved: {len(rows)}")

    return rows


# =====================================================
# GDP PER CAPITA
# =====================================================

gdp_data = download_dataset(

    "nama_10r_2gdp",

    {
        "geo": ["EL53", "EL65"],
        "freq": "A",
        "unit": "EUR_HAB"
    },

    "GDP per capita",

    "EUR per inhabitant"
)


# =====================================================
# EMPLOYMENT RATE
# =====================================================

employment_data = download_dataset(

    "lfst_r_lfe2emprt",

    {
        "geo": ["EL53", "EL65"],
        "freq": "A",
        "unit": "PC",
        "sex": "T",
        "age": "Y15-64"
    },

    "Employment rate",

    "%"
)


# =====================================================
# SAVE DATA
# =====================================================

all_rows = gdp_data + employment_data

df = pd.DataFrame(all_rows)

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    OUTPUT,
    index=False
)


print("\n================================")
print("REGIONAL DATA DOWNLOAD COMPLETE")
print("================================")

print(f"Total observations: {len(df)}")

print("\nAvailable indicators:")

if not df.empty:
    print(df["indicator"].value_counts())

    print("\nAvailable regions:")
    print(df["region"].value_counts())

    print("\nDate range:")
    print(df["year"].min(), "to", df["year"].max())

print(f"\nSaved to: {OUTPUT}")