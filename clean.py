import pandas as pd

# Load dataset
data = pd.read_csv("dataset_olympics.csv")

# Drop rows without team or year
data = data.dropna(subset=["Team", "Year"])

# Count number of athletes per team per year
attendance = data.groupby(["Team", "Year"]).size().reset_index(name="Count")

# Calculate total number of athletes each year
year_total = attendance.groupby("Year")["Count"].sum().reset_index(name="Total")

# Merge totals back to attendance data
merged = pd.merge(attendance, year_total, on="Year")

# Calculate percentage attendance per country
merged["Percentage_Attendance"] = (merged["Count"] / merged["Total"]) * 100

# Rank teams within each year by number of athletes
merged["Rank"] = merged.groupby("Year")["Count"].rank(ascending=False, method="first")

# Replace all ranks above 8 with 'Other' using vectorized assignment to avoid SettingWithCopyWarning
merged.loc[merged["Rank"] > 8, "Team"] = "Other"

# Regroup counts so that all "Other" entries are combined together and recompute percentages from counts
final = merged.groupby(["Team", "Year"], as_index=False).agg({"Count": "sum", "Total": "first"})

# Calculate percentage attendance per country from aggregated counts
final["Percentage_Attendance"] = (final["Count"] / final["Total"]) * 100

# Round to 2 decimal places and keep only the needed columns
final["Percentage_Attendance"] = final["Percentage_Attendance"].round(2)
final = final[["Team", "Year", "Percentage_Attendance"]]

# Save cleaned dataset
final.to_csv("top8_countries_attendance.csv", index=False)

# Display first few rows
print(final.head())
