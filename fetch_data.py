
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

# EUROSTAT API
URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/"
    "statistics/1.0/data/nrg_cb_pem"
)

PARAMS = {
    "geo": "EL",
    "freq": "M",
    "unit": "GWH",
    "lang": "en"
}

print("Connecting to Eurostat...")

response = requests.get(URL, params=PARAMS, timeout=60)
response.raise_for_status()

data = response.json()

# DIMENSIONS
dimensions = data["id"]
sizes = data["size"]

categories = {}
labels = {}

for dimension in dimensions:
    category = data["dimension"][dimension]["category"]
    index = category["index"]
    label = category.get("label", {})

    if isinstance(index, dict):
        ordered_codes = sorted(index, key=index.get)
    else:
        ordered_codes = index

    categories[dimension] = ordered_codes
    labels[dimension] = label

# OBSERVATIONS
values = data["value"]

if isinstance(values, list):
    observations = enumerate(values)
else:
    observations = values.items()

flags = data.get("status", {})
rows = []

retrieved_at = datetime.now(timezone.utc).isoformat()

for flat_index, value in observations:

    if value is None:
        continue

    remainder = int(flat_index)
    coordinates = []

    for size in reversed(sizes):
        coordinates.append(remainder % size)
        remainder //= size

    coordinates.reverse()

    observation = {}

    for i, dimension in enumerate(dimensions):
        code = categories[dimension][coordinates[i]]
        observation[dimension] = code

    fuel_code = observation["siec"]
    fuel_name = labels["siec"].get(fuel_code, fuel_code)

    flag = flags.get(str(flat_index), "") if isinstance(flags, dict) else ""

    rows.append({
        "date": observation["time"],
        "fuel_code": fuel_code,
        "fuel": fuel_name,
        "indicator": f"Net electricity generation - {fuel_name}",
        "value": value,
        "unit": "GWh",
        "country": "Greece",
        "source": "Eurostat",
        "source_url": "https://ec.europa.eu/eurostat/databrowser/view/nrg_cb_pem/default/table",
        "retrieved_at": retrieved_at,
        "data_status": flag if flag else "No observation flag"
    })

# SAVE DATA
df = pd.DataFrame(rows)

output_path = Path("data") / "greece_energy.csv"
df.to_csv(output_path, index=False)

print("--------------------------------")
print("EUROSTAT DATA SUCCESSFULLY DOWNLOADED")
print("--------------------------------")
print(f"Observations: {len(df)}")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")
print("\nAvailable energy sources:")
print(df[["fuel_code", "fuel"]].drop_duplicates().to_string(index=False))
print(f"\nSaved to: {output_path}")
