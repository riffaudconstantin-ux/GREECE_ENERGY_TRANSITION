import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

BASE_URL = (
    "https://ec.europa.eu/eurostat/api/"
    "dissemination/statistics/1.0/data/"
)

OUTPUT = Path("data/security_data.csv")

def download_dataset(dataset, params, indicator, unit):
    print(f"Downloading {dataset}...")

    response = requests.get(
        BASE_URL + dataset,
        params={**params, "lang": "en"},
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
            categories[dimension] = sorted(index, key=index.get)
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

        rows.append({
            "date": observation.get("time", ""),
            "indicator": indicator,
            "value": value,
            "unit": unit,
            "country": "Greece",
            "source": "Eurostat",
            "dataset": dataset,
            "source_url": (
                f"https://ec.europa.eu/eurostat/databrowser/"
                f"view/{dataset}/default/table"
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

    print(f"Retrieved: {len(rows)} observations")

    return rows


all_rows = []

# ELECTRICITY IMPORTS AND EXPORTS
for balance, label in [
    ("IMP", "Electricity imports"),
    ("EXP", "Electricity exports")
]:

    all_rows += download_dataset(
        "nrg_cb_e",
        {
            "geo": "EL",
            "freq": "A",
            "siec": "E7000",
            "unit": "GWH",
            "nrg_bal": balance
        },
        label,
        "GWh"
    )


# TOTAL ENERGY IMPORT DEPENDENCY
all_rows += download_dataset(
    "nrg_ind_id",
    {
        "geo": "EL",
        "freq": "A",
        "siec": "TOTAL",
        "unit": "PC"
    },
    "Total energy import dependency",
    "%"
)


# NATURAL GAS IMPORT DEPENDENCY
all_rows += download_dataset(
    "nrg_ind_id",
    {
        "geo": "EL",
        "freq": "A",
        "siec": "G3000",
        "unit": "PC"
    },
    "Natural gas import dependency",
    "%"
)


# SAVE DATA
OUTPUT.parent.mkdir(exist_ok=True)

df = pd.DataFrame(all_rows)

df.to_csv(OUTPUT, index=False)

print("\n================================")
print("SECURITY DATA DOWNLOAD COMPLETE")
print("================================")
print(f"Total observations: {len(df)}")
print(f"Saved to: {OUTPUT}")

if not df.empty:
    print("\nAvailable indicators:")
    print(df["indicator"].value_counts())
    print("\nDate range:")
    print(df["date"].min(), "to", df["date"].max())