import pandas as pd
import numpy as np
import re
from pathlib import Path

# Input and output
INPUT = Path("dataset_olympics.csv")
OUT_CSV = Path("top8_country_percentage_per_SummerGames_with_other.csv")

# Load
df = pd.read_csv(INPUT, encoding="utf-8")

# Column picker
def pick(df, names):
    m = {c.lower(): c for c in df.columns}
    for n in names:
        if n.lower() in m:
            return m[n.lower()]
    return None

games_col  = pick(df, ["Games", "Edition", "Games_Name", "Games Name"])
country_col = pick(df, ["Country", "Team", "NOC", "Country_Name", "Nation"])
year_col   = pick(df, ["Year", "Edition_Year", "Games_Year", "Season_Year", "Games Year"])
season_col = pick(df, ["Season", "Games_Season"])

# Basic cleaning
if games_col is None:
    if year_col is None:
        raise ValueError("No Games and no Year column found")
    df[year_col] = pd.to_numeric(df[year_col], errors="coerce").astype("Int64")
    df["Games"] = df[year_col].astype("Int64").astype("string")
    games_col = "Games"
else:
    df[games_col] = df[games_col].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()

if country_col is None:
    if "NOC" in df.columns:
        country_col = "NOC"
    else:
        df["Country"] = "Unknown"
        country_col = "Country"
df[country_col] = df[country_col].astype(str).str.strip()

# Parse/normalise Year
if year_col is not None:
    df[year_col] = pd.to_numeric(df[year_col], errors="coerce").astype("Int64")
    df["Year"] = df[year_col]
else:
    def extract_year(x):
        m = re.search(r"(18|19|20|21)\d{2}", str(x))
        return int(m.group(0)) if m else pd.NA
    df["Year"] = df[games_col].apply(extract_year).astype("Int64")

# Second pass for any missing years
na_mask = df["Year"].isna()
if na_mask.any():
    def from_tokens(x):
        for t in str(x).split():
            if t.isdigit() and len(t) == 4:
                v = int(t)
                if 1800 <= v <= 2100:
                    return v
        return pd.NA
    df.loc[na_mask, "Year"] = df.loc[na_mask, games_col].apply(from_tokens).astype("Int64")

# Keep only Summer Games
summer_years = {
    1896, 1900, 1904, 1908, 1912, 1920, 1924, 1928, 1932, 1936,
    1948, 1952, 1956, 1960, 1964, 1968, 1972, 1976, 1980, 1984,
    1988, 1992, 1996, 2000, 2004, 2008, 2012, 2016, 2020, 2024
}
if season_col:
    df[season_col] = df[season_col].astype(str).str.strip().str.title()
    df = df[df[season_col] == "Summer"]

# Always filter by the known Summer years as a safety net
df = df[df["Year"].isin(summer_years)].copy()

# Also exclude any row whose Games text explicitly says "Winter"
df = df[~df[games_col].str.contains("Winter", case=False, na=False)].copy()

# Drop rows missing Games or Year
df = df.dropna(subset=[games_col, "Year"])

# Count participants per Summer Games and Country
counts = (
    df.groupby([games_col, "Year", country_col], dropna=False)
      .size()
      .reset_index(name="Count")
      .rename(columns={games_col: "Games", country_col: "country"})
)

# Rank within each Games, keep top 8, group the rest as "Other"
counts["Rank"] = counts.groupby("Games")["Count"].rank(method="first", ascending=False)
top8 = counts[counts["Rank"] <= 8].copy()
others = (
    counts[counts["Rank"] > 8]
      .groupby(["Games", "Year"], as_index=False)["Count"].sum()
      .assign(country="Other", Rank=np.nan)
)

result = pd.concat([top8, others], ignore_index=True)

# Percentage per Games
totals = result.groupby("Games")["Count"].transform("sum")
result["Percentage_Attendance"] = (result["Count"] / totals * 100).round(2)

# Final output
out = (
    result[["country", "Games", "Year", "Percentage_Attendance"]]
      .sort_values(["Year", "Games", "Percentage_Attendance"], ascending=[True, True, False])
      .reset_index(drop=True)
)

out.to_csv(OUT_CSV, index=False)
print(f"Saved {OUT_CSV.resolve()}")
