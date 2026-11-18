import pandas as pd
from pathlib import Path
from datetime import date

# ==========================================
# LIGNITE-RELATED EMPLOYMENT DATA
# WESTERN MACEDONIA, GREECE
# ==========================================

data = [
    {
        "date": "2018-12-31",
        "year": 2018,
        "indicator": "PPC regional workforce",
        "value": 4147,
        "unit": "employees",
        "region": "Western Macedonia",
        "data_status": "Observed corporate employment stock",
        "scope": "PPC Western Macedonia + Meliti company",
        "source": "PPC 2018 Annual Report",
        "source_url": "https://www.ppcgroup.com/",
        "reference_study": "Independent ex-post study, August 2026"
    },
    {
        "date": "2019-12-31",
        "year": 2019,
        "indicator": "PPC regional workforce",
        "value": 3488,
        "unit": "employees",
        "region": "Western Macedonia",
        "data_status": "Observed corporate employment stock",
        "scope": "PPC Western Macedonia + Meliti company",
        "source": "PPC 2019 Annual Report",
        "source_url": "https://www.ppcgroup.com/",
        "reference_study": "Independent ex-post study, August 2026"
    },
    {
        "date": "2020-12-31",
        "year": 2020,
        "indicator": "PPC regional workforce",
        "value": 2768,
        "unit": "employees",
        "region": "Western Macedonia",
        "data_status": "Observed corporate employment stock",
        "scope": "PPC Western Macedonia + Meliti company",
        "source": "PPC 2020 Sustainability Report",
        "source_url": "https://www.ppcgroup.com/",
        "reference_study": "Independent ex-post study, August 2026"
    },
    {
        "date": "2021-12-31",
        "year": 2021,
        "indicator": "PPC regional workforce",
        "value": 2418,
        "unit": "employees",
        "region": "Western Macedonia",
        "data_status": "Observed corporate employment stock",
        "scope": "PPC Western Macedonia + Meliti company",
        "source": "PPC 2021 Annual Report",
        "source_url": "https://www.ppcgroup.com/",
        "reference_study": "Independent ex-post study, August 2026"
    }
]

# CREATE DATAFRAME

df = pd.DataFrame(data)

# CALCULATE CHANGE

first_value = df.iloc[0]["value"]
last_value = df.iloc[-1]["value"]

absolute_change = last_value - first_value

percentage_change = (
    absolute_change / first_value
) * 100

# SAVE DATASET

output_path = Path("data") / "lignite_employment.csv"

df.to_csv(output_path, index=False)

# DISPLAY RESULTS

print("========================================")
print("LIGNITE EMPLOYMENT DATA CREATED")
print("========================================")

print(f"Observations: {len(df)}")

print(f"Period: {df['year'].min()}–{df['year'].max()}")

print(f"Initial workforce: {first_value:,}")

print(f"Final workforce: {last_value:,}")

print(f"Absolute change: {absolute_change:,}")

print(f"Percentage change: {percentage_change:.1f}%")

print(f"Saved to: {output_path}")

print("========================================")